from typing import List, Optional, Dict, Any, Tuple
import re
import logging

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

from app.domain.models import ChatInput, ChatOutput, ChatMessage, Evidence, MetadatoImagen
from app.domain.errors import DocumentoNoEncontradoOExpiradoError
from app.domain.enums import MetodoExtraccion
from app.services.cache_service import get_l1_cache, L1DocumentEntry
from app.services.semantic_extraction_service import normalize_parameter
from app.settings import settings

logger = logging.getLogger("pydective.chat")


def _clean_query_concept(pregunta: str) -> str:
    """Limpia palabras interrogativas comunes para aislar el concepto consultado."""
    text = pregunta.strip().lower()
    text = re.sub(r"[¿\?¡\!]", "", text)
    # Quitar muletillas y verbos iniciales de pregunta
    prefixes = [
        "tiene un", "tiene una", "tiene el", "tiene la", "tiene los", "tiene las", "tiene",
        "hay un", "hay una", "hay el", "hay la", "hay los", "hay las", "hay",
        "cuál es el", "cuál es la", "cuáles son los", "cuáles son las", "cuál es", "cuáles son",
        "cuanto es el", "cuanto es la", "cuanto cuesta", "a cuánto asciende el", "a cuánto asciende la", "a cuánto asciende",
        "dime si tiene", "dime si hay", "dime el", "dime la", "dime",
        "existe un", "existe una", "existen", "existe",
    ]
    for p in prefixes:
        if text.startswith(p + " "):
            text = text[len(p) + 1:].strip()
            break
    return text.strip()


def _search_visual_elements(resultados_por_pagina: List[Any], query_norm: str) -> Tuple[List[str], List[Evidence], str]:
    """
    Busca elementos visuales catalogados (códigos de barras, QR, firmas, sellos, fotos, gráficos, imágenes).
    Retorna (citas, evidencias_simuladas, descripcion).
    """
    citas: List[str] = []
    evidencias: List[Evidence] = []
    descripcion = ""

    # Si la consulta indaga sobre una página específica, delegar al extractor pericial de página
    if re.search(r"\b(?:p[áa]gina|p[áa]g\.?|hoja|folio)(?:\s*(?:n[úu]mero|no\.?|num\.?|#))?\s*(\d+)\b", query_norm, re.IGNORECASE):
        return [], [], ""

    # Detección de consultas de conteo total o existencia general de imágenes
    is_image_count = any(kw in query_norm for kw in (
        "cuantas imagenes", "cuantas fotos", "cuantos graficos", "cuantos diagramas",
        "total de imagenes", "total imagenes", "cantidad de imagenes", "numero de imagenes",
        "cuantas imagenes hay", "cuantas imagenes tiene", "cuantas imagenes contiene",
        "cuantos escaneos", "cuantas imagenes existen", "cuantas fotos hay"
    )) or (
        any(q in query_norm for q in ("cuantas", "cuantos", "total de", "cantidad de", "numero de")) and
        any(img_w in query_norm for img_w in ("imagen", "imagenes", "foto", "fotos", "grafico", "graficos", "diagrama", "diagramas", "escaneo", "escaneos"))
    )

    is_image_general = any(kw in query_norm for kw in (
        "hay imagenes", "tiene imagenes", "contiene imagenes", "existen imagenes",
        "que imagenes hay", "que imagenes tiene", "cuales imagenes", "cuales son las imagenes"
    ))

    if is_image_count or is_image_general:
        img_pages = []
        for res in resultados_por_pagina:
            p_num = getattr(res, "numero_pagina", 1)
            visuals: List[MetadatoImagen] = getattr(res, "metadatos_visuales", [])
            for v in visuals:
                if p_num not in img_pages:
                    img_pages.append(p_num)
                evidencias.append(
                    Evidence(
                        evidence_id=f"ev_img_p{p_num}_{v.id_imagen}",
                        page=p_num,
                        text=f"Elemento gráfico / escaneo ({v.clasificacion_semantica or 'imagen'}) en Pág {p_num}",
                        bbox=v.bbox,
                        source=MetodoExtraccion.VISUAL_AI,
                        evidence_score=0.98,
                    )
                )
        img_pages.sort()
        total_imgs = len(evidencias)
        if total_imgs > 0:
            citas = [f"[Página {p}]" for p in img_pages]
            citas_str = ", ".join(citas)
            if is_image_count:
                descripcion = (
                    f"El documento cuenta con un total comprobado de **{total_imgs} imágenes** registradas en su inventario visual forense, "
                    f"distribuidas en {len(img_pages)} páginas del expediente: {citas_str}. "
                    f"Cada una corresponde a evidencia gráfica, fotografías, diagramas técnicos o comprobantes escaneados."
                )
            else:
                descripcion = (
                    f"Sí, el documento cuenta con **{total_imgs} imágenes** identificadas en su inspección visual, "
                    f"localizadas en las páginas: {citas_str}."
                )
        else:
            descripcion = "El expediente analizado no contiene imágenes incrustadas ni elementos gráficos registrados."
        return citas, evidencias, descripcion

    # Mapeo de términos de consulta a clasificaciones semánticas específicas
    is_barcode = any(kw in query_norm for kw in ("codigo de barras", "codigo barras", "barcode", "barras", "radicado"))
    is_qr = any(kw in query_norm for kw in ("codigo qr", "qr", "cufe"))
    is_signature = any(kw in query_norm for kw in ("firma", "firmas", "firmado", "rubrica", "firmantes"))
    is_seal = any(kw in query_norm for kw in ("sello", "sellos", "notaria", "notarial", "autenticado", "estampilla"))
    is_photo = any(kw in query_norm for kw in ("foto", "fotografia", "fotografias", "datacenter", "servidor"))
    is_chart = any(kw in query_norm for kw in ("grafico", "grafica", "diagrama", "pastel", "barras comparativo"))

    found_pages: List[int] = []
    item_type = ""

    for res in resultados_por_pagina:
        p_num = getattr(res, "numero_pagina", 1)
        visuals: List[MetadatoImagen] = getattr(res, "metadatos_visuales", [])
        for v in visuals:
            sem = v.clasificacion_semantica or ""
            matched = False
            if is_barcode and sem == "codigo_barras":
                matched = True
                item_type = "código de barras de radicación oficial"
            elif is_qr and sem == "codigo_qr":
                matched = True
                item_type = "código QR de validación fiscal"
            elif is_signature and sem == "firma_manuscrita":
                matched = True
                item_type = "firma autógrafa caligráfica"
            elif is_seal and sem == "sello_oficial":
                matched = True
                item_type = "sello oficial notarial"
            elif is_photo and sem == "fotografia":
                matched = True
                item_type = "evidencia fotográfica pericial"
            elif is_chart and sem == "diagrama":
                matched = True
                item_type = "gráfico o diagrama técnico"

            if matched:
                if p_num not in found_pages:
                    found_pages.append(p_num)
                txt = f"Elemento visual detectado: {item_type}"
                if v.contenido_decodificado:
                    txt += f" (contenido decodificado: '{v.contenido_decodificado}')"
                txt += f" en bbox {v.bbox}"
                evidencias.append(
                    Evidence(
                        evidence_id=f"ev_vis_p{p_num}_{v.id_imagen}",
                        page=p_num,
                        text=txt,
                        bbox=v.bbox,
                        source=MetodoExtraccion.VISUAL_AI,
                        evidence_score=0.96,
                    )
                )

    if found_pages:
        found_pages.sort()
        citas = [f"[Página {p}]" for p in found_pages]
        citas_str = ", ".join(citas)
        decoded_notes = []
        for res in resultados_por_pagina:
            for v in getattr(res, "metadatos_visuales", []):
                if v.contenido_decodificado and (is_qr and v.clasificacion_semantica == "codigo_qr"):
                    decoded_notes.append(f"contenido/URL: {v.contenido_decodificado}")
        extra_note = f" ({', '.join(decoded_notes)})" if decoded_notes else ""
        descripcion = f"Sí, el documento cuenta con {item_type} verificado e inventariado en {citas_str}{extra_note}."

    return citas, evidencias, descripcion


def process_chat_query(
    pdf_hash: str,
    pregunta: str,
    historial: List[ChatMessage] = [],
    fallback_store: Optional[Dict[str, Any]] = None,
) -> ChatOutput:
    """
    Procesa consultas en lenguaje natural con inteligencia contextual, búsqueda en L1,
    catálogo de elementos visuales (códigos de barras, QR, firmas, sellos) y respuestas conversacionales fluidas (US-23).
    """
    l1_entry: Optional[L1DocumentEntry] = get_l1_cache(pdf_hash)
    fallback_job = fallback_store.get(pdf_hash) if fallback_store else None

    if l1_entry is None and fallback_job is None:
        from pathlib import Path
        disk_path = Path(__file__).resolve().parent.parent.parent / "data" / "results" / f"{pdf_hash}.json"
        if disk_path.exists():
            from app.domain.models import JobOutput
            try:
                fallback_job = JobOutput.model_validate_json(disk_path.read_text(encoding="utf-8"))
            except Exception:
                pass

    if l1_entry is None and fallback_job is None:
        raise DocumentoNoEncontradoOExpiradoError(pdf_hash)

    q_norm = normalize_parameter(pregunta)
    q_tokens = [t for t in q_norm.split() if len(t) > 2]
    concepto_limpio = _clean_query_concept(pregunta)

    # 1. Obtener páginas procesadas para inspección visual y textual
    resultados_paginas = []
    total_pages = 1
    if l1_entry:
        resultados_paginas = l1_entry.resultados_por_pagina
        total_pages = l1_entry.paginas_totales or len(resultados_paginas) or 1
    elif fallback_job:
        resultados_paginas = fallback_job.resultados_por_pagina
        total_pages = fallback_job.paginas_totales or len(resultados_paginas) or 1

    # 2. Inspeccionar elementos visuales (códigos de barras, QR, firmas, sellos, fotos)
    vis_citas, vis_evidencias, vis_desc = _search_visual_elements(resultados_paginas, q_norm)
    if vis_citas:
        return ChatOutput(
            respuesta=vis_desc,
            citas=vis_citas,
            evidencias_relacionadas=vis_evidencias[:3],
        )

    # 3. Detectar si el usuario pregunta por una página específica o la última página
    page_match = re.search(r"\b(?:p[áa]gina|p[áa]g\.?|hoja|folio)(?:\s*(?:n[úu]mero|no\.?|num\.?|#))?\s*(\d+)\b", pregunta, re.IGNORECASE)
    if not page_match:
        page_match = re.search(r"\b(?:p[áa]gina|p[áa]g\.?|hoja|folio)(?:\s*(?:n[úu]mero|no\.?|num\.?|#))?\s*(\d+)\b", q_norm, re.IGNORECASE)
    is_last_page = bool(re.search(r"\b(?:[úu]ltima\s+p[áa]gina|final\s+del\s+documento|cierre\s+del\s+expediente)\b", pregunta, re.IGNORECASE))
    specific_page: Optional[int] = None
    if page_match:
        try:
            p_val = int(page_match.group(1))
            if 1 <= p_val <= total_pages:
                specific_page = p_val
        except ValueError:
            pass
    elif is_last_page:
        specific_page = total_pages

    # 4. Inspeccionar índice asociativo y hallazgos estructurados de L1 o fallback
    matched_evidences: List[Evidence] = []
    matched_findings: List[str] = []
    available_params: List[str] = []

    if l1_entry:
        for param, ev_list in l1_entry.indice_asociativo.items():
            available_params.append(param)
            param_norm = normalize_parameter(param)
            if any(t in param_norm for t in q_tokens) or any(param_norm in t for t in q_tokens):
                for ev in ev_list:
                    if ev not in matched_evidences:
                        matched_evidences.append(ev)
                        matched_findings.append(f"{param}: {ev.text}")

        for h in l1_entry.hallazgos_previos:
            if h.parametro not in available_params:
                available_params.append(h.parametro)
            h_norm = normalize_parameter(h.parametro)
            if any(t in h_norm for t in q_tokens) or any(h_norm in t for t in q_tokens):
                for ev in h.evidencias:
                    if ev not in matched_evidences:
                        matched_evidences.append(ev)
                        matched_findings.append(f"{h.parametro}: {h.valor}")

    elif fallback_job:
        for h in fallback_job.hallazgos:
            available_params.append(h.parametro)
            h_norm = normalize_parameter(h.parametro)
            if any(t in h_norm for t in q_tokens) or any(h_norm in t for t in q_tokens):
                for ev in h.evidencias:
                    if ev not in matched_evidences:
                        matched_evidences.append(ev)
                        matched_findings.append(f"{h.parametro}: {h.valor}")

    # Búsqueda adicional en evidencias directas de todas las páginas
    for res in resultados_paginas:
        for ev in getattr(res, "evidencias", []):
            ev_norm = normalize_parameter(ev.text)
            if any(t in ev_norm for t in q_tokens) or (specific_page and ev.page == specific_page):
                if ev not in matched_evidences:
                    matched_evidences.append(ev)
                    matched_findings.append(ev.text)

    # 5. Si se preguntó por una página específica, asociar también sus elementos visuales
    if specific_page:
        for res in resultados_paginas:
            if getattr(res, "numero_pagina", None) == specific_page:
                for v in getattr(res, "metadatos_visuales", []):
                    matched_evidences.append(
                        Evidence(
                            evidence_id=f"ev_p{specific_page}_{v.id_imagen}",
                            page=specific_page,
                            text=f"Elemento visual: {v.clasificacion_semantica}",
                            bbox=v.bbox,
                            source=MetodoExtraccion.VISUAL_AI,
                            evidence_score=0.95,
                        )
                    )

    # 6. Extracción dinámica integral de texto y mapa de elementos visuales (PyMuPDF)
    doc_text_snippets = []
    visuals_by_page = {}
    for res in resultados_paginas:
        p_num = getattr(res, "numero_pagina", 1)
        v_list = [v.clasificacion_semantica for v in getattr(res, "metadatos_visuales", []) if v.clasificacion_semantica]
        if v_list:
            visuals_by_page[p_num] = ", ".join(v_list)

    pdf_bytes = None
    specific_page_text = ""
    specific_page_image_bytes = None
    try:
        from app.services.pdf_viewer_service import get_pdf_bytes_by_hash
        from app.services.ocr_service import (
            get_or_extract_ocr_page,
            get_cached_page_ocr,
            search_ocr_scanned_pages,
        )

        pdf_bytes = get_pdf_bytes_by_hash(pdf_hash)
        if pdf_bytes:
            import pymupdf
            doc_ctx = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            total_pdf_pages = len(doc_ctx)

            # Si el usuario preguntó por una página específica, extraer su contenido íntegro con máxima prioridad
            if specific_page and 1 <= specific_page <= total_pdf_pages:
                page_obj = doc_ctx[specific_page - 1]
                txt_spec = page_obj.get_text().strip()
                vis_source = "Texto Digital"

                # Si la página no tiene texto digital pero contiene imágenes (escaneada/recibo), extraer OCR
                if not txt_spec and len(page_obj.get_images()) > 0:
                    txt_spec = get_or_extract_ocr_page(pdf_hash, doc_ctx, specific_page, dpi=95)
                    vis_source = "Transcripción OCR de Imagen"

                # Renderizar imagen para adjuntar a Gemini Multimodal si la página tiene imágenes
                if len(page_obj.get_images()) > 0:
                    try:
                        pix = page_obj.get_pixmap(dpi=100)
                        specific_page_image_bytes = pix.tobytes("jpeg")
                    except Exception as e_pix:
                        logger.warning(f"No se pudo renderizar imagen de pág {specific_page} para Gemini: {e_pix}")

                vis_info = f" [Elementos visuales en página: {visuals_by_page.get(specific_page, 'recibo o documento escaneado')}]" if visuals_by_page.get(specific_page) else ""
                specific_page_text = f"=== PÁGINA ESPECÍFICA SOLICITADA: PÁGINA {specific_page} ({vis_source}) ===\n{txt_spec}{vis_info}"

            # Extraer mapa representativo de las páginas del expediente
            max_pages_to_scan = min(total_pdf_pages, 50)
            for p_idx in range(max_pages_to_scan):
                p_num = p_idx + 1
                txt = doc_ctx[p_idx].get_text().strip()
                vis_desc = f" (Contiene: {visuals_by_page[p_num]})" if p_num in visuals_by_page else ""
                if txt:
                    char_limit = 1200 if total_pdf_pages <= 25 else 600
                    clean_p = " ".join(txt.split())[:char_limit]
                    doc_text_snippets.append(f"[Página {p_num}]{vis_desc}: {clean_p}")
                elif p_num in visuals_by_page:
                    cached_ocr = get_cached_page_ocr(pdf_hash, p_num)
                    if cached_ocr:
                        clean_ocr = " ".join(cached_ocr.split())[:600]
                        doc_text_snippets.append(f"[Página {p_num}]{vis_desc} (Transcripción OCR): {clean_ocr}")
                    else:
                        doc_text_snippets.append(f"[Página {p_num}]{vis_desc}: (Página gráfica o escaneada)")

            # Si no se solicitó una página específica pero hay términos clave que no coinciden en texto digital,
            # buscar en las páginas escaneadas mediante OCR inteligente
            if not specific_page and q_tokens:
                stop_words = {
                    "dime", "sabes", "sobre", "que", "para", "como", "cual", "cuales", "donde", "cuando",
                    "quien", "quienes", "por", "con", "sin", "del", "las", "los", "una", "uno", "unos", "unas",
                    "este", "esta", "estos", "estas", "ese", "esa", "esos", "esas", "aquel", "todo", "toda",
                    "todos", "todas", "hay", "tiene", "cuenta", "registra", "dice", "muestra", "algo", "nada"
                }
                content_tokens = [t for t in q_tokens if t not in stop_words]
                search_tokens = content_tokens if content_tokens else q_tokens

                has_digital_match = any(
                    any(t in snippet.lower() for t in search_tokens)
                    for snippet in doc_text_snippets if "Transcripción OCR" not in snippet
                )
                if not has_digital_match:
                    ocr_matches = search_ocr_scanned_pages(pdf_hash, doc_ctx, search_tokens)
                    for matched_pnum, ocr_txt in ocr_matches:
                        clean_ocr = " ".join(ocr_txt.split())[:800]
                        doc_text_snippets.append(f"[Página {matched_pnum}] (Transcripción OCR): {clean_ocr}")
                        matched_findings.append(f"Página {matched_pnum} (Transcripción OCR): {clean_ocr[:200]}")
                        matched_evidences.append(
                            Evidence(
                                evidence_id=f"ev_ocr_p{matched_pnum}",
                                page=matched_pnum,
                                text=f"Coincidencia en Pág {matched_pnum}: {clean_ocr[:120]}",
                                bbox=[50.0, 50.0, 500.0, 700.0],
                                source=MetodoExtraccion.OCR_TESSERACT,
                                evidence_score=0.98,
                            )
                        )

            doc_ctx.close()
    except Exception as exc:
        logger.warning(f"No se pudo extraer texto integral para contexto de chat: {exc}")

    # 7. Construcción de Contexto Cognitivo Enriquecido
    context_parts = [f"Total folios/páginas del documento: {total_pages}."]
    if specific_page_text:
        context_parts.append(f"\n{specific_page_text}\n")
    if matched_findings:
        context_parts.append(f"Hallazgos relevantes identificados: {'; '.join(matched_findings[:8])}.")
    if available_params:
        context_parts.append(f"Parámetros clave extraídos: {', '.join(set(available_params))}.")
    if doc_text_snippets:
        context_parts.append("Contenido de las páginas del expediente:\n" + "\n".join(doc_text_snippets))

    context_summary = "\n\n".join(context_parts)

    # 8. Formateo de Historial Previo para Continuidad Conversacional
    history_context = ""
    is_followup = bool(historial and len(historial) > 0)
    if is_followup:
        recent_turns = []
        for msg in historial[-6:]:
            m_role = getattr(msg, "role", None) or (msg.get("role") if isinstance(msg, dict) else "user")
            m_content = getattr(msg, "content", None) or (msg.get("content") if isinstance(msg, dict) else "")
            speaker = "Usuario" if m_role in ("user", "human") else "SmartDoc"
            recent_turns.append(f"{speaker}: {m_content}")
        history_context = "HISTORIAL PREVIO DE LA CONVERSACIÓN:\n" + "\n".join(recent_turns) + "\n\n"

    # 9. Prompt Conversacional Natural, Empático y Profesional
    prompt = (
        "Eres SmartDoc, el asistente pericial de inteligencia documental del Buzón Corporativo RIWI.\n"
        "Tu misión es responder preguntas sobre el expediente o documento analizado de forma conversacional, "
        "natural, fluida, clara y altamente profesional, como un perito o auditor experto dialogando con un colega.\n\n"
        "DIRECTRICES OBLIGATORIAS:\n"
        "1. CONTINUIDAD CONVERSACIONAL Y SALUDOS: "
        + ("El usuario ya está conversando contigo (historial previo activo). NUNCA saludes de nuevo (prohibido decir 'Hola', 'Hola de nuevo', 'Buenas tardes', 'Estimado colega', etc.). Responde DIRECTAMENTE a la pregunta de forma natural y sin rodeos."
           if is_followup else
           "Es el primer mensaje de la conversación. Puedes dar un saludo muy breve, profesional y directo.")
        + "\n2. LECTURA DE IMÁGENES Y RECIBOS: Si la consulta es sobre una imagen, recibo, factura o página escaneada (como en la Página 24), "
        "utiliza toda la información disponible en la transcripción OCR y/o la imagen adjunta. Detalla con máxima precisión "
        "nombres de comercios (ej: Tienda El Mirador), NITs, números de recibo, fechas, productos o conceptos, cantidades, valores unitarios y totales.\n"
        "3. CITAS COMPROBABLES: Cada vez que menciones un dato, hecho, firma o comprobante de una página, indica la referencia con formato [Página X] "
        "(ejemplo: [Página 24]), para que el usuario pueda verificarlo directamente en el visor de documentos.\n"
        "4. FORMATO: Emplea Markdown limpio con negritas para destacar nombres o datos clave y listas si enumeras varios puntos.\n"
        "5. HONESTIDAD: Si un dato genuinamente no se encuentra en el documento, dilo amablemente y de forma natural, indicando qué datos afines sí están disponibles.\n\n"
        f"{history_context}"
        f"EXPEDIENTE ANALIZADO ({total_pages} páginas):\n{context_summary}\n\n"
        f"Pregunta del Usuario: {pregunta}"
    )

    llm_response_text = None

    # Intento 1: Google Gemini (Gemini 3.5 Flash Lite o Gemini 3.5 Flash con soporte Multimodal)
    active_key = settings.api_keys_list[0] if settings.api_keys_list else None
    if active_key and genai is not None:
        try:
            client = genai.Client(api_key=active_key)
            gemini_contents = [prompt]
            if specific_page_image_bytes and types is not None:
                gemini_contents.append(
                    types.Part.from_bytes(data=specific_page_image_bytes, mime_type="image/jpeg")
                )
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=gemini_contents,
            )
            if response and response.text:
                llm_response_text = response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini no disponible ({e}). Activando failover ultra-rápido Groq LPU...")

    # Intento 2: Failover ultra-rápido a Groq (qwen/qwen3.8-27b o openai/gpt-oss-120b)
    if not llm_response_text and settings.GROQ_API_KEY:
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            }
            groq_system = (
                "Eres SmartDoc, el asistente pericial de inteligencia documental de RIWI. "
                "Responde con fluidez, naturalidad, exactitud pericial y citas comprobables [Página X]. "
                + ("REGLA ESTRICTA DE CONTINUIDAD: Ya existe conversación previa activa. NUNCA saludes de nuevo ('Hola', 'Qué tal', etc.). "
                   "Responde DIRECTAMENTE a la pregunta." if is_followup else
                   "Da un saludo inicial breve y responde con profesionalismo.")
            )
            groq_messages = [{"role": "system", "content": groq_system}]
            for m in historial[-6:]:
                m_role = getattr(m, "role", None) or (m.get("role") if isinstance(m, dict) else "user")
                m_content = getattr(m, "content", None) or (m.get("content") if isinstance(m, dict) else "")
                role = "assistant" if m_role in ("assistant", "system", "bot") else "user"
                groq_messages.append({"role": role, "content": m_content})
            groq_messages.append({"role": "user", "content": prompt})

            body = {
                "model": settings.GROQ_MODEL or "qwen/qwen3.8-27b",
                "messages": groq_messages,
                "temperature": 0.2,
                "max_tokens": 800,
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body, timeout=10.0)
            if r.status_code == 200:
                resp_json = r.json()
                llm_response_text = resp_json["choices"][0]["message"]["content"].strip()
                logger.info("Respuesta de chat generada exitosamente vía Groq failover!")
        except Exception as e:
            logger.warning(f"Error en failover Groq chat: {e}")

    if llm_response_text:
        # Extraer páginas citadas en el texto de la respuesta
        cited_pages = set()
        for m in re.finditer(r"\[P[áa]gina\s*(\d+)\]", llm_response_text, re.IGNORECASE):
            try:
                cited_pages.add(int(m.group(1)))
            except ValueError:
                pass
        if specific_page:
            cited_pages.add(specific_page)
        for ev in matched_evidences:
            cited_pages.add(ev.page)

        citas = [f"[Página {p}]" for p in sorted(list(cited_pages))] if cited_pages else []
        return ChatOutput(
            respuesta=llm_response_text,
            citas=citas,
            evidencias_relacionadas=matched_evidences[:3],
        )

    # 10. Síntesis local determinista fluida si no hay conexión a APIs LLM
    if specific_page and specific_page_text:
        vis_note = f", incluyendo {visuals_by_page[specific_page]}" if specific_page in visuals_by_page else ""
        clean_content = re.sub(r"=== PÁGINA ESPECÍFICA SOLICITADA:[^=]+===", "", specific_page_text).strip()
        saludo = "" if is_followup else "Hola. "
        respuesta = (
            f"{saludo}En la **[Página {specific_page}]** del expediente se registra la siguiente información{vis_note}:\n\n"
            f"{clean_content}"
        )
        return ChatOutput(
            respuesta=respuesta,
            citas=[f"[Página {specific_page}]"],
            evidencias_relacionadas=matched_evidences[:3],
        )

    if not matched_evidences:
        resumen_disponible = f" ({', '.join(list(set(available_params))[:4])})" if available_params else ""
        saludo = "" if is_followup else "Hola. "
        respuesta = (
            f"{saludo}He revisado las {total_pages} páginas del documento y no encontré referencias sobre "
            f"'{concepto_limpio}'."
        )
        if available_params:
            respuesta += f" Los datos disponibles que puedes consultar son: {', '.join(list(set(available_params))[:5])}."

        return ChatOutput(
            respuesta=respuesta,
            citas=[],
            evidencias_relacionadas=[],
        )

    matched_evidences.sort(key=lambda e: e.evidence_score, reverse=True)
    top_evidences = matched_evidences[:3]
    pages = sorted(list(set(e.page for e in top_evidences)))
    citas = [f"[Página {p}]" for p in pages]
    citas_str = ", ".join(citas)

    details = "; ".join(matched_findings[:2])
    saludo = "" if is_followup else "Hola. "
    respuesta = (
        f"{saludo}En {citas_str} se identifica la siguiente información relevante: **{details}**."
    )

    return ChatOutput(
        respuesta=respuesta,
        citas=citas,
        evidencias_relacionadas=top_evidences,
    )
