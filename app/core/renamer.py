"""Standardized Document Renamer and Packaging Engine.

Applies the corporate naming convention:
{FECHA}_{CATEGORIA}_{ARBOL_SI/NO}_{ID}.{ext}
Organizes output directories and bundles processed files into a single ZIP archive.
"""

from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path
from typing import List, Tuple

from app.config import OUTPUT_DIR
from app.parsers.base_parser import ProcessedDocument


class DocumentRenamer:
    """Handles renaming, directory placement, and ZIP archiving of processed documents."""

    def __init__(self, output_dir: Path = OUTPUT_DIR) -> None:
        """Initializes renamer with target output directory."""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_standardized_name(self, doc: ProcessedDocument) -> str:
        """Constructs the canonical filename according to RIWI business specifications.

        Format: {FECHA}_{CATEGORIA}_{ID}.{ext}

        Args:
            doc: ProcessedDocument with metadata populated.

        Returns:
            Standardized filename string.
        """
        meta = doc.metadata

        # Clean date string (YYYYMMDD) or fallback
        if meta.issue_date:
            clean_date = re.sub(r"[^0-9]", "", meta.issue_date)[:8]
        else:
            clean_date = "20260923"

        # Canonical category
        category = meta.category.upper()

        # Unique identifier (Invoice #, PO #, NIT, or clean original stem)
        raw_id = meta.document_number or meta.nit_or_id or doc.file_path.stem
        clean_id = re.sub(r"[^A-Za-z0-9]", "", raw_id)[:16] or "DOC"

        suffix = doc.file_path.suffix.lower()
        standardized_name = f"{clean_date}_{category}_{clean_id}{suffix}"
        return standardized_name

    def save_and_rename(self, doc: ProcessedDocument) -> Path:
        """Copies the processed document to output_dir with its new standardized name.

        Args:
            doc: Processed document.

        Returns:
            Path to the saved renamed file.
        """
        new_filename = self.generate_standardized_name(doc)
        target_path = self.output_dir / new_filename

        # Avoid accidental overwrite by suffixing counter if collision occurs
        counter = 1
        base_stem = target_path.stem
        while target_path.exists() and target_path != doc.file_path:
            target_path = self.output_dir / f"{base_stem}_v{counter}{doc.file_path.suffix}"
            counter += 1

        shutil.copy2(doc.file_path, target_path)
        doc.metadata.suggested_filename = target_path.name
        return target_path

    def package_batch_zip(self, processed_docs: List[ProcessedDocument], zip_name: str = "lote_documentos_procesados.zip") -> Path:
        """Packages all renamed documents into a single downloadable ZIP file.

        Args:
            processed_docs: List of documents to bundle.
            zip_name: Name of the resulting ZIP file.

        Returns:
            Path to the generated ZIP package.
        """
        zip_path = self.output_dir / zip_name
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for doc in processed_docs:
                renamed_path = self.output_dir / doc.metadata.suggested_filename
                if not renamed_path.exists():
                    renamed_path = self.save_and_rename(doc)
                z.write(renamed_path, arcname=renamed_path.name)

        return zip_path
