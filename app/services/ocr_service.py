"""High-Speed Deterministic OCR and Document Vision Indexing Service.

Handles high-precision OCR extraction for scanned/image-only PDF pages using PyMuPDF and Tesseract,
providing thread-safe, in-memory caching and background indexing for instant chat responses.
"""

from typing import Dict, List, Optional, Tuple, Set
import threading
import logging
import re
import pymupdf

logger = logging.getLogger("pydective.ocr")

# Thread lock for C Leptonica / PyMuPDF OCR safety
_OCR_LOCK = threading.Lock()

# Centralized in-memory OCR cache: {pdf_hash: {page_number: text}}
_DOCUMENT_OCR_CACHE: Dict[str, Dict[int, str]] = {}


def get_cached_page_ocr(pdf_hash: str, page_number: int) -> Optional[str]:
    """Obtiene el texto OCR en caché para una página si ya fue procesada."""
    return _DOCUMENT_OCR_CACHE.get(pdf_hash, {}).get(page_number)


def get_cached_document_ocr(pdf_hash: str) -> Dict[int, str]:
    """Obtiene todo el diccionario OCR en caché para un documento."""
    return _DOCUMENT_OCR_CACHE.get(pdf_hash, {})


def extract_page_ocr_text(page: pymupdf.Page, dpi: int = 100) -> str:
    """
    Extrae el texto de una página gráfica o escaneada utilizando PyMuPDF OCR
    con bloqueo de seguridad para hilos (Leptonica C-library).
    """
    with _OCR_LOCK:
        try:
            tp = page.get_textpage_ocr(language="eng", dpi=dpi)
            text = tp.extractTEXT().strip()
            if text:
                return text
        except Exception as exc:
            logger.warning(f"Error en get_textpage_ocr (dpi={dpi}): {exc}")

        # Fallback a subprocess tesseract si get_textpage_ocr fallara o retornara vacío
        try:
            import subprocess
            pix = page.get_pixmap(dpi=dpi)
            img_bytes = pix.tobytes("jpeg")
            res = subprocess.run(
                ["tesseract", "stdin", "stdout", "--psm", "6", "-l", "eng"],
                input=img_bytes,
                capture_output=True,
                timeout=5.0,
            )
            return res.stdout.decode("utf-8", errors="ignore").strip()
        except Exception as e2:
            logger.error(f"Fallback tesseract también falló: {e2}")
            return ""


def get_or_extract_ocr_page(pdf_hash: str, doc: pymupdf.Document, page_number: int, dpi: int = 100) -> str:
    """
    Retorna el texto OCR de una página (1-indexed). Si no está en caché, lo extrae
    y lo almacena en memoria para consultas instantáneas posteriores.
    """
    if pdf_hash not in _DOCUMENT_OCR_CACHE:
        _DOCUMENT_OCR_CACHE[pdf_hash] = {}

    if page_number in _DOCUMENT_OCR_CACHE[pdf_hash]:
        return _DOCUMENT_OCR_CACHE[pdf_hash][page_number]

    if not (1 <= page_number <= len(doc)):
        return ""

    page = doc[page_number - 1]
    raw_text = page.get_text().strip()
    if raw_text:
        _DOCUMENT_OCR_CACHE[pdf_hash][page_number] = raw_text
        return raw_text

    # Si es escaneada / gráfica, ejecutar OCR
    ocr_text = extract_page_ocr_text(page, dpi=dpi)
    _DOCUMENT_OCR_CACHE[pdf_hash][page_number] = ocr_text
    return ocr_text


def search_ocr_scanned_pages(
    pdf_hash: str,
    doc: pymupdf.Document,
    query_tokens: List[str],
) -> List[Tuple[int, str]]:
    """
    Busca términos de consulta en las páginas escaneadas del documento.
    Revisa la caché primero, y si no hay coincidencias y faltan páginas por escanear,
    inspecciona las páginas escaneadas faltantes.
    """
    if pdf_hash not in _DOCUMENT_OCR_CACHE:
        _DOCUMENT_OCR_CACHE[pdf_hash] = {}

    cached = _DOCUMENT_OCR_CACHE[pdf_hash]
    matches: List[Tuple[int, str]] = []

    clean_tokens = [t.lower() for t in query_tokens if len(t) > 2]
    if not clean_tokens:
        return []

    # 1. Buscar primero en lo ya cacheado
    for p_num, text in cached.items():
        text_lower = text.lower()
        if any(t in text_lower for t in clean_tokens):
            matches.append((p_num, text))

    if matches:
        return matches

    # 2. Si no hubo coincidencias, buscar en páginas escaneadas que aún no han sido OCR-eadas
    # Iterar en orden inverso porque los comprobantes, anexos y recibos se ubican usualmente al final
    total_pages = len(doc)
    for p_idx in reversed(range(total_pages)):
        p_num = p_idx + 1
        if p_num in cached:
            continue

        page = doc[p_idx]
        # Solo procesar páginas que no tengan texto digital y tengan imágenes
        if not page.get_text().strip() and len(page.get_images()) > 0:
            ocr_text = extract_page_ocr_text(page, dpi=75)
            cached[p_num] = ocr_text
            text_lower = ocr_text.lower()
            if any(t in text_lower for t in clean_tokens):
                matches.append((p_num, ocr_text))
                break

    return matches


def warmup_document_ocr(pdf_hash: str, pdf_bytes: bytes) -> None:
    """
    Inicia un hilo en segundo plano (daemon) que indexa progresivamente
    las páginas escaneadas en caché sin bloquear ni demorar las respuestas.
    """
    def _worker():
        try:
            if pdf_hash not in _DOCUMENT_OCR_CACHE:
                _DOCUMENT_OCR_CACHE[pdf_hash] = {}

            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            for p_idx in range(len(doc)):
                p_num = p_idx + 1
                if p_num in _DOCUMENT_OCR_CACHE[pdf_hash]:
                    continue
                page = doc[p_idx]
                if not page.get_text().strip() and len(page.get_images()) > 0:
                    txt = extract_page_ocr_text(page, dpi=85)
                    _DOCUMENT_OCR_CACHE[pdf_hash][p_num] = txt
            doc.close()
            logger.info(f"Indexación OCR en segundo plano completada para documento {pdf_hash}")
        except Exception as exc:
            logger.warning(f"Error en warmup_document_ocr: {exc}")

    t = threading.Thread(target=_worker, daemon=True)
    t.start()

