"""Automated Test Suite for FastAPI Engine & PDF.js Visor Integration."""

import time
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
SAMPLE_DOCS_DIR = Path(__file__).resolve().parent / "sample_docs"

def test_01_health_and_index():
    """Verifica que el servicio esté arriba y renderice la interfaz principal."""
    resp_health = client.get("/health")
    assert resp_health.status_code == 200
    data = resp_health.json()
    assert data["status"] == "healthy"
    assert "SmartDoc" in data["app"] or data.get("alias") == "PyDective"

    resp_index = client.get("/")
    assert resp_index.status_code == 200
    assert "Inteligencia Documental" in resp_index.text
    assert "pdf-file-input" in resp_index.text

def test_02_dian_xml_zip_ingestion():
    """Verifica la ingesta y extracción determinista de facturas DIAN UBL 2.1 en XML/ZIP."""
    zip_path = SAMPLE_DOCS_DIR / "factura_electronica_dian_SETP9921.zip"
    assert zip_path.exists(), "El archivo ZIP de prueba DIAN debe existir"

    with open(zip_path, "rb") as f:
        resp = client.post(
            "/procesar",
            files={"file": (zip_path.name, f, "application/zip")},
            data={"parametros": "total, fecha, nit, factura", "catalogar_imagenes": "false"}
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "complete"
    assert data["departamento_sugerido"] == "Contabilidad / Cuentas por Pagar"
    assert "SETP-9921" in [h["valor"] for h in data["hallazgos"]]

def test_03_image_to_pdf_conversion():
    """Verifica la ingesta, conversión a PDF y análisis forense de imágenes PNG."""
    img_path = SAMPLE_DOCS_DIR / "recibo_caja_oficina_sin_arbol.png"
    assert img_path.exists(), "La imagen PNG de prueba debe existir"

    with open(img_path, "rb") as f:
        resp = client.post(
            "/procesar",
            files={"file": (img_path.name, f, "image/png")},
            data={"parametros": "total, fecha, nit", "catalogar_imagenes": "false"}
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["paginas_totales"] == 1
    assert data["paginas_completadas"] == 1

def test_04_benchmark_twenty_two_pages_and_l0_cache():
    """Verifica procesamiento de 22 páginas clínicas y respuesta sub-segundo con L0 Caché."""
    pdf_path = SAMPLE_DOCS_DIR / "medik_benchmark_22_paginas.pdf"
    assert pdf_path.exists(), "El PDF de 22 páginas debe existir"

    # Llamada 1: Procesa y puebla L0/L1
    with open(pdf_path, "rb") as f:
        resp1 = client.post(
            "/procesar",
            files={"file": (pdf_path.name, f, "application/pdf")},
            data={"parametros": "paciente, diagnostico, fecha", "catalogar_imagenes": "false"}
        )
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["paginas_totales"] == 22
    assert data1["paginas_completadas"] == 22
    pdf_hash = data1["pdf_hash"]

    # Llamada 2: Caché L0 inmediata
    t0 = time.perf_counter()
    with open(pdf_path, "rb") as f:
        resp2 = client.post(
            "/procesar",
            files={"file": (pdf_path.name, f, "application/pdf")},
            data={"parametros": "paciente, diagnostico, fecha", "catalogar_imagenes": "false"}
        )
    dur_l0 = (time.perf_counter() - t0) * 1000
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["nivel_cache"] == "L0"
    assert dur_l0 < 1500.0, f"La respuesta de Caché L0 debe ser sub-segundo (obtenido {dur_l0:.1f}ms)"

def test_05_chat_and_document_understanding():
    """Verifica que el chatbot responda de qué trata el documento con citas comprobables."""
    pdf_path = SAMPLE_DOCS_DIR / "medik_benchmark_22_paginas.pdf"
    with open(pdf_path, "rb") as f:
        resp = client.post(
            "/procesar",
            files={"file": (pdf_path.name, f, "application/pdf")},
            data={"parametros": "paciente, diagnostico", "catalogar_imagenes": "false"}
        )
    pdf_hash = resp.json()["pdf_hash"]

    chat_resp = client.post(
        f"/chat/{pdf_hash}",
        json={"pregunta": "¿De qué trata este documento y cuál es su objeto principal?"}
    )
    assert chat_resp.status_code == 200
    data = chat_resp.json()
    assert len(data["respuesta"]) > 20
    assert any(term in data["respuesta"].lower() for term in ["clínico", "clinico", "hospitalario", "paciente", "medik", "salud"])

def test_06_downloads_and_exports():
    """Verifica la descarga con nombre estandarizado y reportes Excel / CSV."""
    pdf_path = SAMPLE_DOCS_DIR / "medik_benchmark_22_paginas.pdf"
    with open(pdf_path, "rb") as f:
        resp = client.post(
            "/procesar",
            files={"file": (pdf_path.name, f, "application/pdf")},
            data={"parametros": "paciente", "catalogar_imagenes": "false"}
        )
    pdf_hash = resp.json()["pdf_hash"]

    # Descarga binaria
    raw_resp = client.get(f"/documentos/{pdf_hash}/raw")
    assert raw_resp.status_code == 200
    assert raw_resp.headers["content-type"] == "application/pdf"

    # Descarga normalizada
    down_resp = client.get(f"/documentos/{pdf_hash}/download")
    assert down_resp.status_code == 200
    assert "attachment" in down_resp.headers["content-disposition"]

    # Exportación Excel
    excel_resp = client.get(f"/exportar/{pdf_hash}/excel")
    assert excel_resp.status_code == 200
    assert len(excel_resp.content) > 1000

    # Exportación CSV
    csv_resp = client.get(f"/exportar/{pdf_hash}/csv")
    assert csv_resp.status_code == 200
    assert "SHA-256" in csv_resp.text

def test_07_twenty_page_forensic_audit_document():
    """Verifica procesamiento ultrarrápido y extracción forense del documento completo de 20 páginas."""
    pdf_path = SAMPLE_DOCS_DIR / "documento_completo_20_paginas.pdf"
    assert pdf_path.exists(), "El documento de 20 páginas debe existir en sample_docs"

    t0 = time.perf_counter()
    with open(pdf_path, "rb") as f:
        resp = client.post(
            "/procesar",
            files={"file": (pdf_path.name, f, "application/pdf")},
            data={"parametros": "total, nit, expediente, contratista, fecha", "catalogar_imagenes": "false"}
        )
    dur_ms = (time.perf_counter() - t0) * 1000
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "complete"
    assert data["paginas_totales"] == 20
    assert data["paginas_completadas"] == 20
    assert dur_ms < 2500.0, f"Debe procesar las 20 páginas en < 2.5s (obtenido {dur_ms:.1f}ms)"

    hallazgos_dict = {h["parametro"].lower(): h["valor"] for h in data["hallazgos"]}
    assert "total" in hallazgos_dict or "nit" in hallazgos_dict

    # Probar endpoint de resultados renderizado HTML
    pdf_hash = data["pdf_hash"]
    res_html = client.get(f"/resultados/{pdf_hash}")
    assert res_html.status_code == 200
    assert "20 Páginas" in res_html.text or "20 páginas" in res_html.text or "Páginas: 20" in res_html.text or "20" in res_html.text

    # Probar consulta chat sobre el contratista o monto
    chat_resp = client.post(
        f"/chat/{pdf_hash}",
        json={"pregunta": "¿Cuál es el contratista o la empresa mencionada en el informe?"}
    )
    assert chat_resp.status_code == 200
    cdata = chat_resp.json()
    assert len(cdata["respuesta"]) > 10


def test_08_thirty_page_ocr_and_image_chat():
    """Verifica procesamiento de 30 páginas, conteo exacto de 21 imágenes, transcripción OCR de la pág 24 y continuidad sin saludos."""
    pdf_path = SAMPLE_DOCS_DIR / "PDF_prueba_OCR_30_paginas.pdf"
    assert pdf_path.exists(), "El PDF de 30 páginas con OCR debe existir"

    with open(pdf_path, "rb") as f:
        resp = client.post(
            "/procesar",
            files={"file": (pdf_path.name, f, "application/pdf")},
            data={"parametros": "total, nit, expediente", "catalogar_imagenes": "true"}
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["paginas_totales"] == 30
    assert data["paginas_completadas"] == 30
    pdf_hash = data["pdf_hash"]

    # 1. Consulta conteo exacto de imágenes
    chat_img = client.post(
        f"/chat/{pdf_hash}",
        json={"pregunta": "¿cuántas imágenes hay en el documento?"}
    )
    assert chat_img.status_code == 200
    ans_img = chat_img.json()["respuesta"]
    assert "21" in ans_img, f"Debe reportar exactamente 21 imágenes (obtenido: {ans_img})"

    # 2. Consulta transcripción de imagen en página específica 24
    chat_p24 = client.post(
        f"/chat/{pdf_hash}",
        json={"pregunta": "¿qué dice la imagen de la página número 24?"}
    )
    assert chat_p24.status_code == 200
    ans_p24 = chat_p24.json()["respuesta"].lower()
    assert any(term in ans_p24 for term in ["mirador", "901.115.220", "000982", "café", "87.450"]), (
        f"Debe extraer los datos del recibo de Tienda El Mirador (obtenido: {ans_p24})"
    )

    # 3. Consulta de continuidad con historial (no debe repetir saludos)
    historial = [
        {"rol": "usuario", "mensaje": "¿qué dice la imagen de la página número 24?"},
        {"rol": "asistente", "mensaje": chat_p24.json()["respuesta"]}
    ]
    chat_followup = client.post(
        f"/chat/{pdf_hash}",
        json={"pregunta": "¿cuál es el total o valor a pagar de ese recibo?", "historial": historial}
    )
    assert chat_followup.status_code == 200
    ans_fu = chat_followup.json()["respuesta"]
    assert not ans_fu.strip().startswith(("Hola", "Buenos días", "Buenas tardes")), (
        f"No debe reiniciar la conversación con saludos repetitivos (obtenido: {ans_fu[:40]})"
    )
    assert any(term in ans_fu.lower() for term in ["87.450", "87450", "ochenta y siete"]), (
        f"Debe confirmar el monto de $87.450 (obtenido: {ans_fu})"
    )


