"""Operational Reporting and Executive Metrics Generator.

Generates structured Excel and CSV audit reports containing classification,
routing departments, fiscal values, and KPI summaries as required by Section 14
of the RIWI challenge specifications.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd

from app.config import OUTPUT_DIR
from app.parsers.base_parser import ProcessedDocument


class OperationalReporter:
    """Produces tabular reports and operational dashboards from processed documents."""

    def __init__(self, output_dir: Path = OUTPUT_DIR) -> None:
        """Initializes reporter with output directory."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_dataframe(self, documents: List[ProcessedDocument]) -> pd.DataFrame:
        """Converts document batch records into a structured Pandas DataFrame.

        Args:
            documents: List of ProcessedDocument objects.

        Returns:
            Pandas DataFrame ready for display or export.
        """
        rows = []
        for doc in documents:
            m = doc.metadata
            # Visual elements catalog
            v_elements = []
            if m.has_signature_or_seal or any(p.has_signature for p in doc.pages):
                v_elements.append("Firma ✍️")
            if m.has_stamp or any(p.has_stamp for p in doc.pages):
                v_elements.append("Sello 🏷️")
            if any(p.has_table for p in doc.pages):
                v_elements.append("Tabla 📊")
            if any(p.has_tree for p in doc.pages):
                v_elements.append("Foto/Imagen 📷")
            v_summary_str = " + ".join(v_elements) if v_elements else "Texto Plano"

            rows.append({
                "Archivo Original": doc.original_name,
                "Nuevo Nombre Estandarizado": m.suggested_filename,
                "Tipo Formato": doc.file_type,
                "Páginas": doc.num_pages,
                "Categoría Asignada": m.category,
                "Área de Direccionamiento": m.target_department,
                "Nivel Confianza (%)": round(m.confidence_score * 100, 1),
                "Número Documento": m.document_number or "N/A",
                "NIT / Cédula": m.nit_or_id or "N/A",
                "Emisor / Proveedor": m.sender_name or "N/A",
                "Fecha Emisión": m.issue_date or "N/A",
                "Fecha Vencimiento": m.due_date or "N/A",
                "Valor Total": f"${m.total_amount:,.2f}" if m.total_amount is not None else "N/A",
                "Moneda": m.currency,
                "Tipo Orden": m.order_type or "N/A",
                "Elementos Visuales": v_summary_str,
                "¿Árbol en Imagen?": "SÍ" if m.tree_detected else "NO",
                "¿Firma / Sello?": "SÍ" if (m.has_signature_or_seal or m.has_stamp) else "NO",
                "¿Requiere Revisión?": "SÍ" if m.is_exception else "NO",
                "Causa de Revisión": m.exception_reason or "Ninguna",
                "Tiempo Procesamiento (s)": doc.processing_time_sec,
                "Desde Caché (L1/L2)": "SÍ" if doc.was_cached else "NO",
            })

        return pd.DataFrame(rows)

    def calculate_kpis(self, df: pd.DataFrame) -> Dict[str, any]:
        """Calculates executive summary metrics for daily tracking.

        Args:
            df: Report DataFrame.

        Returns:
            Dictionary containing aggregated KPIs.
        """
        if df.empty:
            return {
                "total_docs": 0,
                "auto_processed": 0,
                "exceptions": 0,
                "auto_rate_pct": 0.0,
                "category_counts": {},
                "total_invoice_amount": 0.0,
                "cache_saved_pct": 0.0,
            }

        total_docs = len(df)
        exceptions = len(df[df["¿Requiere Revisión?"] == "SÍ"])
        auto_processed = total_docs - exceptions
        auto_rate = (auto_processed / total_docs) * 100.0 if total_docs > 0 else 0.0

        cat_counts = df["Categoría Asignada"].value_counts().to_dict()
        cache_hits = len(df[df["Desde Caché (L1/L2)"] == "SÍ"])
        cache_saved_pct = (cache_hits / total_docs) * 100.0 if total_docs > 0 else 0.0

        return {
            "total_docs": total_docs,
            "auto_processed": auto_processed,
            "exceptions": exceptions,
            "auto_rate_pct": round(auto_rate, 1),
            "category_counts": cat_counts,
            "cache_saved_pct": round(cache_saved_pct, 1),
        }

    def export_excel(self, df: pd.DataFrame, filename: str = "reporte_operativo_riwi.xlsx") -> Path:
        """Exports the DataFrame to a formatted Excel workbook.

        Args:
            df: DataFrame to save.
            filename: Target Excel filename.

        Returns:
            Path to the written Excel file.
        """
        file_path = self.output_dir / filename
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Detalle Operativo")
            # Auto-fit columns
            worksheet = writer.sheets["Detalle Operativo"]
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = min(40, max(max_len + 3, 12))

        return file_path

    def export_csv(self, df: pd.DataFrame, filename: str = "reporte_operativo_riwi.csv") -> Path:
        """Exports the DataFrame to CSV format.

        Args:
            df: DataFrame to save.
            filename: Target CSV filename.

        Returns:
            Path to the written CSV file.
        """
        file_path = self.output_dir / filename
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        return file_path
