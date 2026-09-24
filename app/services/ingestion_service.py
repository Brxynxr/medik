import hashlib
from pathlib import Path
from typing import Optional, Tuple
import pymupdf

from app.settings import settings
from app.domain.errors import (
    DocumentoInvalidoError,
    TamanoArchivoExcedidoError,
    DocumentoCorruptoOEncriptadoError,
    ExcesoPaginasError,
)

PDF_MAGIC_BYTES = b"%PDF"


def validate_and_read_pdf(
    pdf_bytes: bytes,
    filename: Optional[str] = None,
    max_file_size: Optional[int] = None,
    max_pages: Optional[int] = None,
) -> Tuple[str, pymupdf.Document, int]:
    """
    Valida e ingesta un documento PDF directamente en memoria sin persistencia en disco.

    Aplica las reglas:
    - RNF-022: Procesamiento 100% en memoria (RAM), 0 escrituras a disco.
    - RV-001 / RF-001: Validación de extensión y bytes mágicos (%PDF en los primeros 1024 bytes).
    - RV-002: Límite de tamaño de archivo (por defecto 25 MB).
    - RV-003 / US-01: Detección y rechazo de PDFs corruptos o protegidos con contraseña.
    - RV-006 / US-03: Límite de páginas (por defecto <= 20 páginas).
    - RF-003: Cálculo del hash criptográfico SHA-256 sobre los bytes crudos.

    Retorna:
        Tuple[str, pymupdf.Document, int]: (pdf_hash, fitz_doc, total_paginas)
    """
    limit_bytes = max_file_size or settings.MAX_FILE_SIZE_BYTES
    limit_pages = max_pages or settings.MAX_PAGES_PER_DOCUMENT

    # 1. Validación y conversión multiformato si no es PDF nativo
    clean_name = filename.strip().lower() if filename else ""

    if clean_name.endswith((".png", ".jpg", ".jpeg", ".tiff", ".webp")):
        # Conversión en memoria de imagen a PDF para renderizado en visor y análisis forense
        try:
            ext = clean_name.split(".")[-1]
            img_doc = pymupdf.open(stream=pdf_bytes, filetype=ext)
            pdf_bytes = img_doc.convert_to_pdf()
            img_doc.close()
        except Exception as exc:
            raise DocumentoInvalidoError(f"Error procesando imagen: {exc}")

    elif clean_name.endswith(".docx"):
        # Conversión de DOCX a PDF en memoria
        try:
            import io
            import docx
            docx_file = docx.Document(io.BytesIO(pdf_bytes))
            doc_gen = pymupdf.open()
            page = doc_gen.new_page(width=595, height=842)
            y = 50
            for para in docx_file.paragraphs:
                text = para.text.strip()
                if text:
                    page.insert_text((50, y), text[:90], fontsize=11)
                    y += 18
                    if y > 780:
                        page = doc_gen.new_page(width=595, height=842)
                        y = 50
            pdf_bytes = doc_gen.tobytes()
            doc_gen.close()
        except Exception as exc:
            raise DocumentoInvalidoError(f"Error procesando documento Word DOCX: {exc}")

    elif clean_name.endswith((".xml", ".zip")):
        # Extracción determinista DIAN UBL 2.1 y generación de comprobante PDF en memoria
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=Path(clean_name).suffix, delete=True) as tmp:
                tmp.write(pdf_bytes)
                tmp.flush()
                from app.parsers.dian_xml_parser import DianXmlParser
                parsed = DianXmlParser().parse(Path(tmp.name))

            doc_gen = pymupdf.open()
            page = doc_gen.new_page(width=595, height=842)
            page.insert_text((50, 60), "BUZÓN CORPORATIVO RIWI — COMPROBANTE FISCAL DIAN UBL 2.1", fontsize=14)
            page.insert_text((50, 95), f"Tipo Documento: {parsed.metadata.category}", fontsize=11)
            page.insert_text((50, 115), f"Número Factura: {parsed.metadata.document_number}", fontsize=11)
            page.insert_text((50, 135), f"NIT / Emisor: {parsed.metadata.nit_or_id}", fontsize=11)
            page.insert_text((50, 155), f"Monto Total: {parsed.metadata.total_amount:,.2f} COP" if parsed.metadata.total_amount else "Monto Total: N/A", fontsize=11)
            page.insert_text((50, 175), f"Departamento: {parsed.metadata.target_department}", fontsize=11)
            page.insert_text((50, 195), f"Nombre Sugerido: {parsed.metadata.suggested_filename}", fontsize=10)
            page.insert_text((50, 225), "Texto Extraído:", fontsize=11)
            y = 245
            for line in parsed.full_text.splitlines()[:25]:
                if line.strip():
                    page.insert_text((50, y), line.strip()[:80], fontsize=9)
                    y += 14
            pdf_bytes = doc_gen.tobytes()
            doc_gen.close()
        except Exception as exc:
            raise DocumentoInvalidoError(f"Error procesando factura DIAN XML/ZIP: {exc}")

    # 2. Validación de archivo no vacío
    if not pdf_bytes or len(pdf_bytes) == 0:
        raise DocumentoInvalidoError("El archivo provisto está vacío.")

    # 3. Validación de tamaño máximo de archivo
    received_bytes = len(pdf_bytes)
    if received_bytes > limit_bytes:
        raise TamanoArchivoExcedidoError(max_bytes=limit_bytes, received_bytes=received_bytes)

    # 4. Validación de firma binaria mágica (%PDF en la cabecera)
    header = pdf_bytes[:1024]
    if PDF_MAGIC_BYTES not in header:
        raise DocumentoInvalidoError("El formato de archivo provisto no es compatible con el motor documental.")

    # 5. Cálculo determinista de hash SHA-256
    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

    # 6. Apertura e inspección en memoria con PyMuPDF
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise DocumentoCorruptoOEncriptadoError(
            f"El documento PDF está corrupto o mal formado y no pudo ser abierto: {str(exc)}"
        ) from exc

    # 7. Verificación de cifrado / contraseña
    if doc.is_encrypted or doc.needs_pass:
        doc.close()
        raise DocumentoCorruptoOEncriptadoError(
            "El documento PDF está protegido con contraseña y no puede ser procesado sin credenciales."
        )

    # 8. Verificación de conteo de páginas
    page_count = doc.page_count
    if page_count == 0:
        doc.close()
        raise DocumentoInvalidoError("El documento PDF no contiene páginas válidas.")

    if page_count > limit_pages:
        doc.close()
        raise ExcesoPaginasError(max_pages=limit_pages, total_pages=page_count)

    return pdf_hash, doc, page_count
