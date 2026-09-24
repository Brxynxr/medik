"""Standalone Image Parser for PNG, JPG, JPEG, TIFF, BMP, and WEBP formats.

Loads image, assesses blurriness, applies OpenCV restoration, and packages into
ProcessedDocument structure for OCR and visual detection.
"""

from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np

from app.core.cache_manager import CacheManager
from app.parsers.base_parser import BaseParser, DocumentMetadata, PageData, ProcessedDocument
from app.vision.image_enhancer import ImageEnhancer


class ImageParser(BaseParser):
    """Parser for standalone image files."""

    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}

    def can_handle(self, file_path: Path) -> bool:
        """Checks if file is a supported image format."""
        return file_path.suffix.lower() in self.IMAGE_EXTENSIONS

    def parse(self, file_path: Path) -> ProcessedDocument:
        """Loads and enhances the image.

        Args:
            file_path: Path to the image file.

        Returns:
            ProcessedDocument containing the single enhanced image page.
        """
        sha256 = CacheManager.compute_sha256(file_path)
        img = cv2.imread(str(file_path))

        if img is None:
            # Handle non-standard formats or corrupt images
            meta = DocumentMetadata(
                category="REVISION_HUMANA",
                target_department="Mesa de Control y Excepciones Humanas",
                confidence_score=0.0,
                is_exception=True,
                exception_reason="La imagen no pudo ser leída o se encuentra dañada.",
                suggested_filename=f"REVISION_{file_path.name}",
            )
            return ProcessedDocument(
                file_path=file_path,
                original_name=file_path.name,
                sha256_hash=sha256,
                file_type="IMAGE",
                num_pages=0,
                metadata=meta,
                full_text="Imagen no legible.",
                processing_time_sec=0.001,
            )

        initial_var = ImageEnhancer.calculate_blur_variance(img)
        # Apply OpenCV restoration (deskew, unsharp mask, CLAHE if blurry)
        enhanced_img, blur_var, is_blurry = ImageEnhancer.enhance_document_page(img)

        page = PageData(
            page_number=1,
            image_np=enhanced_img,
            blur_variance=blur_var,
            initial_blur_variance=initial_var,
            is_blurry=is_blurry,
            extra_metadata={
                "dimensions": f"{img.shape[1]}x{img.shape[0]}",
                "channels": img.shape[2],
                "original_image_np": img.copy(),
            },
        )

        metadata = DocumentMetadata(
            category="GENERAL",
            target_department="Administración General",
            confidence_score=0.5,
            suggested_filename=f"IMG_{file_path.stem}{file_path.suffix}",
        )

        return ProcessedDocument(
            file_path=file_path,
            original_name=file_path.name,
            sha256_hash=sha256,
            file_type="IMAGE",
            num_pages=1,
            pages=[page],
            metadata=metadata,
            full_text="",
            processing_time_sec=0.02,
        )
