"""Base classes and data models for document parsing.

Defines the common protocol, data structures, and contract that every format
parser must fulfill to ensure modularity and interoperability across the engine.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class PageData:
    """Represents the extracted text and visual characteristics of a single page or image.

    Attributes:
        page_number: 1-indexed page number within the document.
        raw_text: Text extracted directly via digital layer or OCR.
        cleaned_text: Normalized and cleaned text representation.
        image_np: Optional OpenCV image (numpy array BGR or Grayscale).
        blur_variance: Laplacian variance score (higher = sharper, lower = blurrier).
        is_blurry: True if blur_variance is below the configured threshold.
        detected_objects: List of object labels found visually (e.g. ['tree', 'person']).
        has_tree: Convenience boolean indicating if a tree was detected.
        has_signature: Convenience boolean indicating if a signature or stamp was detected.
        extra_metadata: Arbitrary dictionary for parser-specific attributes.
    """

    page_number: int
    raw_text: str = ""
    cleaned_text: str = ""
    image_np: Optional[np.ndarray] = None
    blur_variance: float = 0.0
    initial_blur_variance: float = 0.0
    is_blurry: bool = False
    detected_objects: List[str] = field(default_factory=list)
    has_tree: bool = False
    has_signature: bool = False
    has_stamp: bool = False
    has_table: bool = False
    signatures_found: List[str] = field(default_factory=list)
    stamps_found: List[str] = field(default_factory=list)
    visual_elements: List[Dict[str, Any]] = field(default_factory=list)
    visual_summary: str = ""
    extra_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentMetadata:
    """Structured business metadata extracted from a document.

    Attributes:
        category: Business category (FACTURA, ORDEN_COMPRA, PQRS, GENERAL, REVISION_HUMANA).
        target_department: Operational department responsible for handling the communication.
        confidence_score: Float between 0.0 and 1.0 indicating classification confidence.
        document_number: Identifier such as invoice number (e.g. 'SETP-9921') or PO number.
        nit_or_id: Tax ID or personal identification number.
        sender_name: Legal name or contact of the provider/client.
        issue_date: Date of issuance in YYYY-MM-DD format if available.
        due_date: Date of expiration or deadline if available.
        total_amount: Monetary amount if applicable.
        currency: Currency code (e.g. 'COP', 'USD').
        order_type: 'PRODUCTO' or 'SERVICIO' if the document is a purchase order.
        is_exception: True if the document requires human review/intervention.
        exception_reason: Explanation why human intervention is required.
        suggested_filename: Standardized filename according to RIWI naming convention.
        tree_detected: Overall boolean indicating if any page contains a tree.
        has_signature_or_seal: Overall boolean indicating presence of physical validation.
        has_stamp: Overall boolean indicating presence of institution/notary stamp.
        signatures_found: List of signature locations by page.
        stamps_found: List of stamp locations by page.
        visual_inventory_summary: Summary of all visual artifacts identified across the document.
    """

    category: str = "GENERAL"
    target_department: str = "Administración General"
    confidence_score: float = 0.0
    document_number: Optional[str] = None
    nit_or_id: Optional[str] = None
    sender_name: Optional[str] = None
    issue_date: Optional[str] = None
    due_date: Optional[str] = None
    total_amount: Optional[float] = None
    currency: str = "COP"
    order_type: Optional[str] = None
    is_exception: bool = False
    exception_reason: Optional[str] = None
    suggested_filename: str = ""
    tree_detected: bool = False
    has_signature_or_seal: bool = False
    has_stamp: bool = False
    signatures_found: List[str] = field(default_factory=list)
    stamps_found: List[str] = field(default_factory=list)
    visual_inventory_summary: str = ""


@dataclass
class ProcessedDocument:
    """Encapsulates the complete analysis result for an ingested document.

    Attributes:
        file_path: Absolute path to the original file.
        original_name: Original filename as uploaded.
        sha256_hash: Cryptographic SHA-256 hash used for Level-2 caching.
        file_type: Canonical type descriptor (PDF, DOCX, ZIP_DIAN, IMAGE).
        num_pages: Total number of pages or slides analyzed.
        pages: List of PageData instances for each page.
        metadata: Extracted business and classification metadata.
        full_text: Aggregated text across all pages.
        processing_time_sec: Wall-clock execution time in seconds.
        was_cached: True if the document was retrieved from the double cache.
    """

    file_path: Path
    original_name: str
    sha256_hash: str
    file_type: str
    num_pages: int
    pages: List[PageData] = field(default_factory=list)
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    full_text: str = ""
    processing_time_sec: float = 0.0
    was_cached: bool = False


class BaseParser(ABC):
    """Abstract base class that all document format parsers must implement."""

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Determines if this parser is capable of handling the specified file.

        Args:
            file_path: Path to the candidate file.

        Returns:
            True if this parser supports the file extension / signature.
        """
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> ProcessedDocument:
        """Parses the document, extracting text, pages, and metadata.

        Args:
            file_path: Path to the input file.

        Returns:
            A populated ProcessedDocument instance.
        """
        pass
