"""High-Performance PDF Parser with Digital Text Triage and Raster Fallback.

Processes multi-page documents (including 20-page scans) using PyMuPDF (fitz).
Implements fast digital text extraction if a selectable text layer is present,
or renders pages to high-resolution raster images for OpenCV enhancement and OCR.
"""

from __future__ import annotations

from pathlib import Path
import pymupdf
import numpy as np

from app.config import MAX_PAGES_LIMIT
from app.core.cache_manager import CacheManager
from app.parsers.base_parser import BaseParser, DocumentMetadata, PageData, ProcessedDocument
from app.vision.image_enhancer import ImageEnhancer


class PdfParser(BaseParser):
    """Parser for multi-page PDF documents."""

    def can_handle(self, file_path: Path) -> bool:
        """Checks if file is a PDF document."""
        return file_path.suffix.lower() == ".pdf"

    def parse(
        self,
        file_path: Path,
        render_images: bool = True,
        max_pages: int = MAX_PAGES_LIMIT,
        dpi: int = 120,
    ) -> ProcessedDocument:
        """Parses a multi-page PDF document.

        Args:
            file_path: Path to the PDF file.
            render_images: Whether to rasterize pages to OpenCV images for visual analysis.
            max_pages: Upper safety limit on pages to parse.
            dpi: Dots per inch for rasterization if images are rendered.

        Returns:
            ProcessedDocument containing extracted pages and text.
        """
        sha256 = CacheManager.compute_sha256(file_path)
        doc = pymupdf.open(file_path)
        total_pages = len(doc)
        pages_to_process = min(total_pages, max_pages)

        pages: List[PageData] = []
        full_text_chunks: List[str] = []

        for page_idx in range(pages_to_process):
            page_num = page_idx + 1
            fitz_page = doc[page_idx]

            # 1. Digital text extraction (instant)
            extracted_text = fitz_page.get_text("text").strip()

            img_np: Optional[np.ndarray] = None
            blur_var = 0.0
            initial_blur = 0.0
            is_blurry = False
            img_bgr_orig: Optional[np.ndarray] = None

            # 2. Render to raster image for visual analysis (tree, blur, signatures)
            if render_images:
                # Render page pixmap
                zoom = dpi / 72.0
                matrix = pymupdf.Matrix(zoom, zoom)
                pix = fitz_page.get_pixmap(matrix=matrix, alpha=False)

                # Convert pixmap buffer to OpenCV BGR numpy array
                img_data = np.frombuffer(pix.samples, dtype=np.uint8)
                img_bgr = img_data.reshape((pix.h, pix.w, 3))
                # PyMuPDF produces RGB, convert to BGR for OpenCV
                import cv2
                img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGB2BGR)
                img_bgr_orig = img_bgr.copy()

                initial_blur = ImageEnhancer.calculate_blur_variance(img_bgr)
                # Enhance if blurry
                img_np, blur_var, is_blurry = ImageEnhancer.enhance_document_page(img_bgr)

            # Store page representation
            page_obj = PageData(
                page_number=page_num,
                raw_text=extracted_text,
                cleaned_text=extracted_text,
                image_np=img_np,
                blur_variance=blur_var,
                initial_blur_variance=initial_blur,
                is_blurry=is_blurry,
                extra_metadata={"original_image_np": img_bgr_orig} if img_bgr_orig is not None else {},
            )
            pages.append(page_obj)

            if extracted_text:
                full_text_chunks.append(f"--- Página {page_num} ---\n{extracted_text}")

        doc.close()

        full_text = "\n\n".join(full_text_chunks)

        # Baseline metadata (will be classified downstream)
        metadata = DocumentMetadata(
            category="GENERAL",
            target_department="Administración General",
            confidence_score=0.5,
            suggested_filename=f"DOC_{file_path.stem}.pdf",
        )

        return ProcessedDocument(
            file_path=file_path,
            original_name=file_path.name,
            sha256_hash=sha256,
            file_type="PDF",
            num_pages=total_pages,
            pages=pages,
            metadata=metadata,
            full_text=full_text,
            processing_time_sec=0.15,
        )
