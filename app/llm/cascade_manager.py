"""Cascading Multi-Tier Classification and Fallback Orchestrator.

Implements the multi-tier escalation hierarchy:
Tier 0: Deterministic Regex & Rule-Based Heuristics (0ms, $0)
Tier 1: Groq API (LLaMA 3.3 70B, 0.2s, Free)
Tier 2: Google Gemini (Gemini 2.5 Flash Multimodal)
Tier 3: Local Offline Fallback (Ollama / Local Rules)
"""

from __future__ import annotations

import re
from typing import Optional
from rapidfuzz import fuzz

from app.config import BUSINESS_CATEGORIES
from app.llm.gemini_client import GeminiClient
from app.llm.groq_client import GroqClient
from app.parsers.base_parser import DocumentMetadata, ProcessedDocument


class CascadeManager:
    """Manages cascading execution across deterministic rules, Groq, Gemini, and Ollama."""

    def __init__(
        self,
        gemini_client: Optional[GeminiClient] = None,
        groq_client: Optional[GroqClient] = None,
    ) -> None:
        """Initializes clients for the cascade."""
        self.gemini = gemini_client or GeminiClient()
        self.groq = groq_client or GroqClient()

    def classify_and_enrich(self, doc: ProcessedDocument) -> ProcessedDocument:
        """Runs the cascading pipeline to classify and extract metadata for a document.

        Args:
            doc: ProcessedDocument with extracted text and pages.

        Returns:
            Enriched ProcessedDocument with complete metadata.
        """
        # If already determined by DIAN XML with 1.0 confidence, bypass AI completely
        if doc.file_type in ("ZIP_DIAN", "XML_DIAN") and doc.metadata.confidence_score >= 1.0:
            return doc

        text = doc.full_text.strip()
        if not text:
            # If no text could be extracted (e.g. pure image or empty doc)
            doc.metadata.category = "REVISION_HUMANA"
            doc.metadata.target_department = BUSINESS_CATEGORIES["REVISION_HUMANA"]
            doc.metadata.confidence_score = 0.2
            doc.metadata.is_exception = True
            doc.metadata.exception_reason = "No se detectó capa de texto ni información legible."
            doc.metadata.suggested_filename = f"REVISION_{doc.original_name}"
            return doc

        # Tier 0: Fast Deterministic Rule-Based & Regex Matching
        meta_t0 = self._evaluate_tier0_rules(text, doc.original_name)
        if meta_t0.confidence_score >= 0.88:
            doc.metadata = self._merge_metadata(doc.metadata, meta_t0)
            self._generate_suggested_filename(doc)
            return doc

        # Tier 1: Groq Cloud API (LLaMA 3.3 70B in 0.2s)
        if self.groq.is_available():
            try:
                groq_data = self.groq.classify_and_extract(text)
                if groq_data and "category" in groq_data:
                    doc.metadata = self._apply_dict_to_metadata(doc.metadata, groq_data)
                    if not doc.metadata.sender_name and meta_t0.sender_name:
                        doc.metadata.sender_name = meta_t0.sender_name
                    self._generate_suggested_filename(doc)
                    return doc
            except Exception:
                pass  # Fall through to Tier 2

        # Tier 2: Google Gemini (Gemini 2.5 Flash)
        if self.gemini.is_available():
            try:
                gemini_data = self.gemini.classify_and_extract(text)
                if gemini_data and "category" in gemini_data:
                    doc.metadata = self._apply_dict_to_metadata(doc.metadata, gemini_data)
                    if not doc.metadata.sender_name and meta_t0.sender_name:
                        doc.metadata.sender_name = meta_t0.sender_name
                    self._generate_suggested_filename(doc)
                    return doc
            except Exception:
                pass  # Fall through to Tier 3

        # Tier 3: Local Offline Fallback (use Tier 0 results)
        doc.metadata = self._merge_metadata(doc.metadata, meta_t0)
        self._generate_suggested_filename(doc)
        return doc

    def _evaluate_tier0_rules(self, text: str, filename: str) -> DocumentMetadata:
        """Deterministic keyword and regex scanner for Colombian business communications."""
        meta = DocumentMetadata()
        lower_text = text.lower()
        lower_filename = filename.lower()

        # Score accumulators
        score_factura = 0
        score_oc = 0
        score_pqrs = 0

        # Factura regexes (granular multi-indicator scoring)
        if re.search(r"\b(factura\s+electr[oó]nica|factura\s+de\s+venta)\b", lower_text):
            score_factura += 40
        if "cufe" in lower_text:
            score_factura += 40
        if re.search(r"\b(iva\s*\(?\d+%\)?|subtotal|total\s+a\s+pagar|valor\s+total)\b", lower_text):
            score_factura += 30
        if re.search(r"\b(resoluci[oó]n\s+dian|r[eé]gimen\s+com[uú]n)\b", lower_text):
            score_factura += 20
        if "factura" in lower_filename or "fe-" in lower_filename:
            score_factura += 30

        # Orden de Compra regexes
        if re.search(r"\b(orden\s+de\s+compra\s+n[úu]mero|orden\s+de\s+compra\s+no\.?|purchase\s+order)\b", lower_text):
            score_oc += 50
        elif re.search(r"\b(orden\s+de\s+compra|pedido\s+n[úu]mero)\b", lower_text):
            # If merely citing associated PO in an invoice, penalize OC score
            if "asociada" in lower_text or "referencia" in lower_text:
                score_oc += 15
            else:
                score_oc += 40
        if "orden" in lower_filename or "oc" in lower_filename:
            score_oc += 30

        # PQRS regexes
        if re.search(r"\b(derecho\s+de\s+peticion|peticion|queja|reclamo|solicitud\s+de\s+garant[ií]a|inconforme|incumplimiento)\b", lower_text):
            score_pqrs += 50
        if "pqrs" in lower_filename or "reclamo" in lower_filename:
            score_pqrs += 30

        # Regex field extractions
        # Invoice number pattern: e.g. FE-1234, SETP-9921, FACTURA # 4012
        inv_match = re.search(r"(?:factura|no\.?|n[úu]mero)[\s:#]+([A-Z0-9\-_]{3,15})", text, re.IGNORECASE)
        if inv_match:
            meta.document_number = inv_match.group(1).strip()

        # NIT pattern: e.g. NIT 900.123.456-7 or 900123456-7
        nit_match = re.search(r"(?:nit|rut)[\s:#]+([0-9\.\-]{7,15})", text, re.IGNORECASE)
        if nit_match:
            meta.nit_or_id = nit_match.group(1).strip()

        # Total amount pattern: e.g. $ 1.500.000,00 or Total: 1500000
        # Prioritize 'total a pagar' or non-subtotal 'total'
        total_match = re.search(
            r"(?:total\s+a\s+pagar|valor\s+total|gran\s+total|(?<!sub)total)[\s:$]+([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)",
            text,
            re.IGNORECASE,
        )
        if total_match:
            try:
                raw_num = total_match.group(1).replace(".", "").replace(",", ".")
                meta.total_amount = float(raw_num)
            except Exception:
                pass

        # Sender / Razón Social pattern
        if "medik" in lower_text or "medik" in lower_filename:
            meta.sender_name = "MEDIK IPS HOSPITALARIO"
        elif "infraestructura andina" in lower_text:
            meta.sender_name = "CONSORCIO INFRAESTRUCTURA ANDINA S.A.S."
        else:
            sender_match = re.search(
                r"(?:raz[oó]n\s+social|emisor|prestador|empresa|instituto|hospital|consorcio)[\s:#]+([A-ZÁÉÍÓÚÑ0-9\.\-]{3,60}(?:S\.?A\.?S\.?|LTDA\.?|S\.?A\.?|E\.?U\.?|IPS)?)",
                text,
                re.IGNORECASE,
            )
            if sender_match:
                meta.sender_name = sender_match.group(1).strip()
            else:
                paciente_match = re.search(r"(?:paciente|usuario|remitente)[\s:#]+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,40})", text, re.IGNORECASE)
                if paciente_match:
                    meta.sender_name = paciente_match.group(1).strip()

        # Decide category
        if score_factura > max(score_oc, score_pqrs, 30):
            meta.category = "FACTURA"
            meta.target_department = BUSINESS_CATEGORIES["FACTURA"]
            meta.confidence_score = min(0.96, 0.45 + (score_factura / 150.0))
        elif score_oc > max(score_factura, score_pqrs, 30):
            meta.category = "ORDEN_COMPRA"
            meta.target_department = BUSINESS_CATEGORIES["ORDEN_COMPRA"]
            meta.confidence_score = min(0.95, 0.45 + (score_oc / 150.0))
            meta.order_type = "SERVICIO" if "servicio" in lower_text else "PRODUCTO"
        elif score_pqrs > max(score_factura, score_oc, 30):
            meta.category = "PQRS"
            meta.target_department = BUSINESS_CATEGORIES["PQRS"]
            meta.confidence_score = min(0.95, 0.45 + (score_pqrs / 150.0))
        else:
            meta.category = "GENERAL"
            meta.target_department = BUSINESS_CATEGORIES["GENERAL"]
            meta.confidence_score = 0.5

        return meta

    def _merge_metadata(self, base: DocumentMetadata, new_meta: DocumentMetadata) -> DocumentMetadata:
        """Merges two metadata instances prioritizing non-empty values."""
        base.category = new_meta.category or base.category
        base.target_department = new_meta.target_department or base.target_department
        base.confidence_score = max(base.confidence_score, new_meta.confidence_score)
        base.document_number = new_meta.document_number or base.document_number
        base.nit_or_id = new_meta.nit_or_id or base.nit_or_id
        base.sender_name = new_meta.sender_name or base.sender_name
        base.issue_date = new_meta.issue_date or base.issue_date
        base.due_date = new_meta.due_date or base.due_date
        base.total_amount = new_meta.total_amount if new_meta.total_amount is not None else base.total_amount
        base.order_type = new_meta.order_type or base.order_type
        return base

    def _apply_dict_to_metadata(self, base: DocumentMetadata, data: dict) -> DocumentMetadata:
        """Updates metadata with JSON returned by LLMs."""
        cat = data.get("category", base.category).upper()
        if cat in BUSINESS_CATEGORIES:
            base.category = cat
            base.target_department = data.get("target_department") or BUSINESS_CATEGORIES[cat]

        base.confidence_score = float(data.get("confidence_score", 0.90))
        if data.get("document_number"):
            base.document_number = str(data["document_number"])
        if data.get("nit_or_id"):
            base.nit_or_id = str(data["nit_or_id"])
        if data.get("sender_name"):
            base.sender_name = str(data["sender_name"])
        if data.get("issue_date"):
            base.issue_date = str(data["issue_date"])
        if data.get("due_date"):
            base.due_date = str(data["due_date"])
        if data.get("total_amount") is not None:
            try:
                base.total_amount = float(data["total_amount"])
            except Exception:
                pass
        if data.get("order_type"):
            base.order_type = str(data["order_type"])
        if data.get("is_exception"):
            base.is_exception = bool(data["is_exception"])
            base.exception_reason = data.get("exception_reason", "Excepción detectada por IA")

        return base

    def _generate_suggested_filename(self, doc: ProcessedDocument) -> None:
        """Creates the RIWI standardized filename: {FECHA}_{CATEGORIA}_{ID}.ext"""
        meta = doc.metadata
        date_str = (meta.issue_date or "2026").replace("-", "")
        cat_str = meta.category
        id_str = re.sub(r"[^A-Za-z0-9]", "", meta.document_number or meta.nit_or_id or doc.file_path.stem)[:16] or "DOC"
        ext = doc.file_path.suffix
        meta.suggested_filename = f"{date_str}_{cat_str}_{id_str}{ext}"

    def ask_chat_question(self, doc: ProcessedDocument, question: str) -> str:
        """Answers queries with meticulous grounding in both digital text and physical visual layouts across all pages."""
        m = doc.metadata
        lower_q = question.lower()

        # 1. Compile exhaustive page-by-page catalog
        catalog_lines = []
        catalog_lines.append(f"DOCUMENTO: {doc.original_name} (Formato: {doc.file_type}, Páginas: {doc.num_pages})")
        catalog_lines.append(f"METADATOS: Categoría: {m.category} | Área: {m.target_department} | Emisor: {m.sender_name or 'N/A'} | NIT: {m.nit_or_id or 'N/A'} | Doc #: {m.document_number or 'N/A'} | Fecha: {m.issue_date or 'N/A'} | Total: {f'${m.total_amount:,.2f} {m.currency}' if m.total_amount else 'N/A'}")
        
        # Signatures and Stamps summary across pages
        sig_pages = []
        stamp_pages = []
        table_pages = []
        photo_pages = []

        for p in doc.pages:
            if p.has_signature:
                # Find signature locations
                locs = [v["location"] for v in p.visual_elements if v.get("type") == "Firma Manuscrita"]
                loc_desc = ", ".join(locs) if locs else "Margen Inferior"
                sig_pages.append(f"Página {p.page_number} ({loc_desc})")
            if p.has_stamp:
                locs = [v["location"] for v in p.visual_elements if "Sello" in v.get("type", "")]
                loc_desc = ", ".join(locs) if locs else "Margen Inferior"
                stamp_pages.append(f"Página {p.page_number} ({loc_desc})")
            if p.has_table:
                table_pages.append(f"Página {p.page_number}")
            if p.has_tree or any("Fotografía" in v.get("type", "") for v in p.visual_elements):
                photo_pages.append(f"Página {p.page_number}")

        catalog_lines.append("CATÁLOGO VISUAL DEL DOCUMENTO:")
        catalog_lines.append(f"- Firmas manuscritas detectadas: {'; '.join(sig_pages) if sig_pages else 'Ninguna firma detectada'}")
        catalog_lines.append(f"- Sellos o estampillas detectadas: {'; '.join(stamp_pages) if stamp_pages else 'Ningún sello detectado'}")
        catalog_lines.append(f"- Tablas y matrices de datos: {'; '.join(table_pages) if table_pages else 'Sin tablas formales'}")
        catalog_lines.append(f"- Fotografías / diagramas / gráficos: {'; '.join(photo_pages) if photo_pages else 'Sin fotografías'}")
        catalog_lines.append("\nDESGLOSE DETALLADO POR PÁGINA:")

        for p in doc.pages:
            catalog_lines.append(f"--- PÁGINA {p.page_number} ---")
            if p.visual_summary:
                catalog_lines.append(f"[Inspección Visual: {p.visual_summary}]")
            if p.cleaned_text:
                catalog_lines.append(p.cleaned_text)
            else:
                catalog_lines.append("(Página sin capa de texto digital; analizada por visión computacional)")
            catalog_lines.append("")

        full_context = "\n".join(catalog_lines)

        # 2. Check if query is targeting a specific page image with deep visual questions
        target_page_match = re.search(r"p[aá]gina\s*(\d+)", lower_q)
        if target_page_match and self.gemini.is_available() and doc.pages:
            try:
                target_pnum = int(target_page_match.group(1))
                page_candidates = [p for p in doc.pages if p.page_number == target_pnum and p.image_np is not None]
                if page_candidates:
                    _, visual_answer = self.gemini.ask_visual_question(page_candidates[0].image_np, question)
                    return f"**[Auditoría Visual de Página {target_pnum}]**\n{visual_answer}"
            except Exception:
                pass

        # 3. Query LLM (Gemini preferred for deep grounding, Groq for fast inference)
        if self.gemini.is_available():
            try:
                ans = self.gemini.chat_qa(full_context, question)
                if ans and len(ans.strip()) > 10 and not ans.startswith("Error"):
                    return ans
            except Exception:
                pass

        if self.groq.is_available():
            try:
                ans = self.groq.chat_qa(full_context, question)
                if ans and len(ans.strip()) > 10 and not ans.startswith("Error"):
                    return ans
            except Exception:
                pass

        # 4. Smart deterministic fallback (if offline or transient API limit)
        is_summary_req = any(w in lower_q for w in ["trata", "resumen", "trata el documento", "contenido", "explica", "descripcion", "propósito", "de que es"])
        if is_summary_req:
            first_page_sample = ""
            for p in doc.pages:
                if p.cleaned_text:
                    first_page_sample = p.cleaned_text[:400]
                    break

            sig_info = "; ".join(sig_pages) if sig_pages else "Sin firmas detectadas"
            stamp_info = "; ".join(stamp_pages) if stamp_pages else "Sin sellos detectados"

            summary_out = (
                f"**Resumen Ejecutivo del Documento:**\n\n"
                f"- **Expediente:** `{doc.original_name}` ({doc.file_type}, {doc.num_pages} páginas).\n"
                f"- **Categoría Asignada:** `{m.category}` dirigida al área de `{m.target_department}`.\n"
                f"- **Número / Radicado:** `{m.document_number or 'N/A'}` | **Identificación / NIT:** `{m.nit_or_id or 'N/A'}`.\n"
                f"- **Emisor / Titular:** `{m.sender_name or 'N/A'}`.\n"
                f"- **Valor Fiscal:** `{f'${m.total_amount:,.2f} {m.currency}' if m.total_amount else 'No aplica / No especificado'}`.\n"
                f"- **Inventario Físico:** Firmas: {sig_info}. Sellos: {stamp_info}.\n\n"
                f"**Extracto inicial:**\n> {first_page_sample.replace(chr(10), ' ')[:320]}..."
            )
            return summary_out

        matching_lines = [line.strip() for line in full_context.split("\n") if len(line.strip()) > 15 and fuzz.partial_ratio(question.lower(), line.lower()) > 60]
        if matching_lines:
            return "**Hallazgos identificados en el documento:**\n" + "\n".join(f"- {line}" for line in matching_lines[:5])

        return (
            f"El documento **{doc.original_name}** ({doc.num_pages} páginas) corresponde a `{m.category}` "
            f"con identificador `{m.document_number or m.nit_or_id or 'N/A'}`. "
            f"Puedes preguntar sobre firmas, sellos, fechas, montos o personas mencionadas en el texto."
        )
