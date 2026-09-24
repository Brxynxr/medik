"""Unified File Router and Ingestion Controller.

Inspects incoming files, computes SHA-256 digests, consults the Double Cache
(returning instant results on duplicates), routes to the specialized parser
(PDF, DOCX, ZIP/XML, or Image), and orchestrates metadata extraction.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional, Union

from app.core.cache_manager import CacheManager
from app.parsers.base_parser import BaseParser, ProcessedDocument
from app.parsers.dian_xml_parser import DianXmlParser
from app.parsers.docx_parser import DocxParser
from app.parsers.image_parser import ImageParser
from app.parsers.pdf_parser import PdfParser


class FileRouter:
    """Orchestrates format detection, caching, and document dispatching."""

    def __init__(self, cache_manager: Optional[CacheManager] = None) -> None:
        """Initializes the router with all registered format parsers.

        Args:
            cache_manager: CacheManager instance. If None, instantiates a default.
        """
        self.cache_manager = cache_manager or CacheManager()
        self.parsers: List[BaseParser] = [
            DianXmlParser(),  # Check XML/ZIP first
            PdfParser(),      # Check PDF
            DocxParser(),     # Check Word
            ImageParser(),    # Check Images
        ]

    def get_parser(self, file_path: Path) -> Optional[BaseParser]:
        """Finds the first parser capable of handling the file.

        Args:
            file_path: Path to the target file.

        Returns:
            Matching BaseParser or None if format is unsupported.
        """
        for parser in self.parsers:
            if parser.can_handle(file_path):
                return parser
        return None

    def process_file(
        self,
        file_path: Union[str, Path],
        force_reprocess: bool = False,
        render_images: bool = True,
    ) -> ProcessedDocument:
        """Routes and parses a single file with double-cache acceleration.

        Args:
            file_path: Path to the document on disk.
            force_reprocess: If True, bypasses cache and re-analyzes from scratch.
            render_images: If True, rasterizes pages for computer vision.

        Returns:
            ProcessedDocument containing structured data.
        """
        start_time = time.perf_counter()
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Document file does not exist: {path}")

        # Step 1: Compute SHA-256 Fingerprint
        sha256 = self.cache_manager.compute_sha256(path)

        # Step 2: Check Double Cache (Level 1 RAM -> Level 2 SQLite)
        if not force_reprocess:
            cached_doc = self.cache_manager.get(sha256)
            if cached_doc:
                # Return immediately in < 0.003s
                cached_doc.processing_time_sec = round(time.perf_counter() - start_time, 4)
                return cached_doc

        # Step 3: Find appropriate parser
        parser = self.get_parser(path)
        if not parser:
            raise ValueError(f"Formato no soportado para el archivo: {path.name}")

        # Step 4: Execute parsing
        if isinstance(parser, PdfParser):
            doc = parser.parse(path, render_images=render_images)
        else:
            doc = parser.parse(path)

        doc.processing_time_sec = round(time.perf_counter() - start_time, 4)
        doc.sha256_hash = sha256

        # Step 5: Save to Double Cache
        self.cache_manager.set(doc)

        return doc
