"""Script to generate realistic test files for the SmartDoc Engine.

Generates:
1. DIAN UBL 2.1 Electronic Invoice inside a ZIP archive.
2. Word DOCX Purchase Order with tables and items.
3. PQRS Customer Complaint letter in PDF format.
4. Image containing a green tree / vegetation (Testing 'Árbol: SÍ').
5. Image of an office receipt without tree (Testing 'Árbol: NO').
6. Degraded blurry scanned PDF (Testing OpenCV Unsharp Masking + CLAHE).
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
import cv2
import numpy as np

# Output directory for test files
TEST_DIR = Path(__file__).resolve().parent / "sample_docs"
TEST_DIR.mkdir(parents=True, exist_ok=True)


def create_dian_xml_zip() -> Path:
    """Generates a realistic DIAN UBL 2.1 electronic invoice inside a ZIP."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
    <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>
    <cbc:CustomizationID>10</cbc:CustomizationID>
    <cbc:ProfileExecutionID>1</cbc:ProfileExecutionID>
    <cbc:ID>SETP-9921</cbc:ID>
    <cbc:UUID schemeName="CUFE-SHA384">c3f2e1a4b5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2</cbc:UUID>
    <cbc:IssueDate>2026-09-21</cbc:IssueDate>
    <cbc:DueDate>2026-10-21</cbc:DueDate>
    <cbc:InvoiceTypeCode>01</cbc:InvoiceTypeCode>
    <cac:OrderReference>
        <cbc:ID>OC-RIWI-2026-088</cbc:ID>
    </cac:OrderReference>
    <cac:AccountingSupplierParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>COLOMBIA TECH &amp; CLOUD SOLUTIONS SAS</cbc:Name>
            </cac:PartyName>
            <cac:PartyTaxScheme>
                <cbc:RegistrationName>COLOMBIA TECH &amp; CLOUD SOLUTIONS SAS</cbc:RegistrationName>
                <cbc:CompanyID schemeAgencyID="195">901345678-9</cbc:CompanyID>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingSupplierParty>
    <cac:AccountingCustomerParty>
        <cac:Party>
            <cac:PartyName>
                <cbc:Name>RIWI BARRANQUILLA SAS</cbc:Name>
            </cac:PartyName>
            <cac:PartyTaxScheme>
                <cbc:RegistrationName>RIWI BARRANQUILLA SAS</cbc:RegistrationName>
                <cbc:CompanyID schemeAgencyID="195">901789012-3</cbc:CompanyID>
            </cac:PartyTaxScheme>
        </cac:Party>
    </cac:AccountingCustomerParty>
    <cac:LegalMonetaryTotal>
        <cbc:LineExtensionAmount currencyID="COP">4075630.25</cbc:LineExtensionAmount>
        <cbc:TaxExclusiveAmount currencyID="COP">4075630.25</cbc:TaxExclusiveAmount>
        <cbc:TaxInclusiveAmount currencyID="COP">4850000.00</cbc:TaxInclusiveAmount>
        <cbc:PayableAmount currencyID="COP">4850000.00</cbc:PayableAmount>
    </cac:LegalMonetaryTotal>
</Invoice>
"""
    zip_path = TEST_DIR / "factura_electronica_dian_SETP9921.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("FacturaElectronica_SETP-9921.xml", xml_content)
        z.writestr("Representacion_Grafica_SETP-9921.pdf", b"%PDF-1.4 Mock Invoice PDF Content")

    return zip_path


def create_tree_image() -> Path:
    """Generates an image showing an outdoor landscape with a clear green tree."""
    img = np.ones((600, 800, 3), dtype=np.uint8) * 235  # Light sky background (soft blueish gray)
    img[:, :, 0] = 230
    img[:, :, 1] = 210
    img[:, :, 2] = 180

    # Draw ground (grass green)
    cv2.rectangle(img, (0, 450), (800, 600), (45, 140, 45), -1)

    # Draw tree trunk (brown)
    cv2.rectangle(img, (370, 320), (430, 490), (30, 60, 110), -1)

    # Draw tree foliage / canopy (vibrant green circles)
    cv2.circle(img, (400, 240), 90, (35, 155, 35), -1)
    cv2.circle(img, (330, 260), 75, (30, 140, 30), -1)
    cv2.circle(img, (470, 260), 75, (40, 165, 40), -1)
    cv2.circle(img, (400, 160), 65, (45, 175, 45), -1)

    # Add label text
    cv2.putText(img, "Inspeccion de Predio - RIWI Sede Norte", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (20, 20, 20), 2)
    cv2.putText(img, "Zona Verde y Arbolado Protegido", (40, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (60, 60, 60), 2)

    image_path = TEST_DIR / "inspeccion_predio_con_arbol.jpg"
    cv2.imwrite(str(image_path), img)
    return image_path


def create_no_tree_receipt_image() -> Path:
    """Generates an office receipt image without any trees or vegetation."""
    img = np.ones((600, 500, 3), dtype=np.uint8) * 248  # Off-white paper background

    # Draw receipt header
    cv2.putText(img, "PAPELERIA & SUMINISTROS EL CENTRO", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (10, 10, 10), 2)
    cv2.putText(img, "NIT: 800.221.993-1 | Tel: 605-3882200", (30, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 60, 60), 1)
    cv2.putText(img, "Barranquilla, Colombia", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 60, 60), 1)
    cv2.line(img, (30, 140), (470, 140), (100, 100, 100), 1)

    cv2.putText(img, "Comprobante de Caja No: REC-4410", (30, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10, 10, 10), 2)
    cv2.putText(img, "Fecha: 22/09/2026", (30, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 10, 10), 1)
    cv2.putText(img, "Cliente: RIWI Barranquilla", (30, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (10, 10, 10), 1)

    # Line items
    cv2.putText(img, "1x Resma Papel Carta 75g     $ 18.500", (30, 280), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (20, 20, 20), 1)
    cv2.putText(img, "5x Marcadores Borrables      $ 22.000", (30, 310), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (20, 20, 20), 1)
    cv2.putText(img, "2x Borrador de Tablero       $ 12.000", (30, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (20, 20, 20), 1)
    cv2.line(img, (30, 360), (470, 360), (100, 100, 100), 1)

    cv2.putText(img, "TOTAL PAGADO: $ 52.500 COP", (30, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)

    image_path = TEST_DIR / "recibo_caja_oficina_sin_arbol.png"
    cv2.imwrite(str(image_path), img)
    return image_path


def create_20_page_pdf() -> Path:
    """Generates a realistic 20-page corporate PDF document.

    Page 1: Invoice Header & Summary (FE-9921, Total $ 4,850,000 COP, Provider COLOMBIA TECH SAS)
    Pages 2-18: Technical infrastructure specifications, SLA tables, and delivery logs.
    Page 19: Photographic field inspection annex containing a clear green tree.
    Page 20: Signatures, approval stamps, and final certificate of receipt.
    """
    import fitz  # PyMuPDF

    pdf_path = TEST_DIR / "expediente_completo_20_paginas.pdf"
    tree_img_path = create_tree_image()

    doc = fitz.open()

    for p in range(1, 21):
        page = doc.new_page(width=595, height=842)  # Standard A4 points

        if p == 1:
            text = (
                "FACTURA ELECTRÓNICA DE VENTA No. FE-9921\n"
                "COLOMBIA TECH & CLOUD SOLUTIONS SAS\n"
                "NIT: 901.345.678-9 | Régimen Común\n"
                "Dirección: Calle 77 # 57-103, Barranquilla, Atlántico\n\n"
                "CLIENTE: RIWI BARRANQUILLA SAS\n"
                "NIT: 901.789.012-3\n"
                "Fecha de Emisión: 2026-09-21 | Fecha de Vencimiento: 2026-10-21\n"
                "Orden de Compra Asociada: OC-RIWI-2026-088\n\n"
                "DETALLE DE CONCEPTOS:\n"
                "1. Servicios de Infraestructura en la Nube y Nodos de Cómputo: $ 3.500.000,00\n"
                "2. Licenciamiento de Seguridad y Firewalls Perimetrales:        $   575.630,25\n"
                "SUBTOTAL:                                                     $ 4.075.630,25\n"
                "IVA (19%):                                                    $   774.369,75\n"
                "TOTAL A PAGAR:                                                $ 4.850.000,00 COP\n\n"
                "CUFE: c3f2e1a4b5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2"
            )
            page.insert_text(fitz.Point(50, 70), text, fontsize=11)
        elif p == 19:
            # Inspection photo with the tree!
            page.insert_text(
                fitz.Point(50, 60),
                "ANEXO TÉCNICO FOTOGRÁFICO - PÁGINA 19\n"
                "Inspección de Adecuación y Entorno Físico - Sede Norte RIWI\n"
                "Verificación de Zonas Verdes y Arbolado Protegido:",
                fontsize=11,
            )
            page.insert_image(fitz.Rect(50, 100, 545, 480), filename=str(tree_img_path))
            page.insert_text(
                fitz.Point(50, 510),
                "Fotografía tomada en terreno: Se certifica la preservación del árbol exterior y vegetación perimetral.",
                fontsize=9,
            )
        elif p == 20:
            page.insert_text(
                fitz.Point(50, 70),
                "ACTA FINAL DE CIERRE Y RECIBO A SATISFACCIÓN - PÁGINA 20\n\n"
                "Por medio de la presente, el área de Servicios Internos y Tecnología de RIWI\n"
                "manifiesta recibir a satisfacción los servicios estipulados en la Orden de Compra OC-RIWI-2026-088.\n\n"
                "Firmado en Barranquilla el 22 de septiembre de 2026.\n\n"
                "______________________________        ______________________________\n"
                "Ing. Andrés Silva                     Dra. Marcela Mendoza\n"
                "Líder de Infraestructura - Proveedor   Directora de Operaciones - RIWI\n"
                "C.C. 1.042.883.190                    C.C. 1.140.822.451",
                fontsize=11,
            )
        else:
            page.insert_text(
                fitz.Point(50, 70),
                f"ANEXO TÉCNICO Y ESPECIFICACIONES DE INFRAESTRUCTURA - PÁGINA {p} DE 20\n\n"
                f"Cláusula {p}.1: Condiciones de Disponibilidad y SLA\n"
                f"El servicio de computación en nube mantiene una garantía de disponibilidad del 99.98% mensual.\n"
                f"Registro de telemetría, monitoreo de latencia y pruebas de redundancia ejecutadas satisfactoriamente.\n"
                f"Identificador de auditoría interna: AUD-2026-SEG-{p:03d}.",
                fontsize=11,
            )

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def main():
    print("Generando documentos de prueba para SmartDoc Engine...")
    p1 = create_dian_xml_zip()
    print(f"  ✓ Creado: {p1.name}")
    p2 = create_tree_image()
    print(f"  ✓ Creado: {p2.name}")
    p3 = create_no_tree_receipt_image()
    print(f"  ✓ Creado: {p3.name}")
    p4 = create_20_page_pdf()
    print(f"  ✓ Creado: {p4.name}")
    print("¡Generación completada exitosamente!")


if __name__ == "__main__":
    main()
