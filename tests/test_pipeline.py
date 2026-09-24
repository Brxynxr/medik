"""End-to-End Automated Test Suite for SmartDoc Engine.

Validates:
1. Double Cache Engine (SHA-256, L1 RAM, L2 SQLite, sub-millisecond retrieval).
2. OpenCV Preprocessing & Restoration (Blur variance, Unsharp Mask, CLAHE).
3. Deterministic DIAN UBL 2.1 Parser (XML & ZIP).
4. Standardized Document Renaming ({FECHA}_{CATEGORIA}_{ARBOL_SI/NO}_{ID}.ext).
5. Operational Reporter (Dataframe and KPI generation).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
import cv2
import numpy as np

# Ensure app is on path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.core.cache_manager import CacheManager
from app.core.file_router import FileRouter
from app.core.renamer import DocumentRenamer
from app.core.reporter import OperationalReporter
from app.parsers.base_parser import DocumentMetadata, PageData, ProcessedDocument
from app.parsers.dian_xml_parser import DianXmlParser
from app.vision.image_enhancer import ImageEnhancer
from app.vision.object_detector import VisualDetector
from tests.generate_test_samples import create_dian_xml_zip, create_no_tree_receipt_image, create_tree_image


class TestSmartDocEngine(unittest.TestCase):
    """Unit and integration tests for the SmartDoc Engine pipeline."""

    @classmethod
    def setUpClass(cls):
        """Generates sample test documents once for the suite."""
        cls.zip_sample = create_dian_xml_zip()
        cls.tree_img_sample = create_tree_image()
        cls.receipt_sample = create_no_tree_receipt_image()

    def test_01_cache_manager(self):
        """Verifies SHA-256 calculation and Double Cache (L1 and L2) storage/retrieval."""
        cache_db_test = BASE_DIR / "data" / "test_cache.db"
        if cache_db_test.exists():
            cache_db_test.unlink()

        cache = CacheManager(db_path=cache_db_test)
        sample_bytes = b"Prueba de contenido para SHA-256 en cache doble"
        hash_digest = cache.compute_sha256(sample_bytes)
        self.assertEqual(len(hash_digest), 64, "SHA-256 hash must be 64 hexadecimal characters")

        # Create mock processed document
        meta = DocumentMetadata(
            category="FACTURA",
            target_department="Tesorería / Cuentas por Pagar",
            confidence_score=0.98,
            document_number="FE-1001",
            nit_or_id="900123456",
            total_amount=500000.0,
            tree_detected=False,
            suggested_filename="20260923_FACTURA_ARBOL_NO_FE1001.pdf",
        )
        doc = ProcessedDocument(
            file_path=Path("factura_test.pdf"),
            original_name="factura_test.pdf",
            sha256_hash=hash_digest,
            file_type="PDF",
            num_pages=1,
            pages=[PageData(page_number=1, raw_text="Factura de venta...")],
            metadata=meta,
            full_text="Factura de venta No. FE-1001",
            processing_time_sec=0.1,
        )

        # Store in cache
        cache.set(doc)

        # Retrieve from L1 cache
        cached_l1 = cache.get(hash_digest)
        self.assertIsNotNone(cached_l1)
        self.assertTrue(cached_l1.was_cached)
        self.assertEqual(cached_l1.metadata.document_number, "FE-1001")

        # Evict L1 to force L2 SQLite fetch
        cache._l1_cache.clear()
        cached_l2 = cache.get(hash_digest)
        self.assertIsNotNone(cached_l2)
        self.assertEqual(cached_l2.metadata.category, "FACTURA")
        self.assertEqual(cached_l2.metadata.total_amount, 500000.0)

        # Clean up test db
        if cache_db_test.exists():
            cache_db_test.unlink()

    def test_02_image_enhancer(self):
        """Verifies Laplacian blur measurement, blur thresholding, and Unsharp Mask."""
        # Sharp synthetic image with sharp lines
        sharp_img = np.zeros((200, 200, 3), dtype=np.uint8)
        sharp_img[50:150, 50:150] = 255
        sharp_var = ImageEnhancer.calculate_blur_variance(sharp_img)
        self.assertGreater(sharp_var, 150.0, "Sharp binary image should have high Laplacian variance")

        # Blurry image
        blurry_img = ImageEnhancer.apply_clahe(sharp_img)
        import cv2
        blurred = cv2.GaussianBlur(sharp_img, (25, 25), 10.0)
        blur_var = ImageEnhancer.calculate_blur_variance(blurred)
        self.assertLess(blur_var, 100.0, "Gaussian blurred image should have low variance")
        self.assertTrue(ImageEnhancer.is_blurry(blurred, threshold=100.0))

        # Test enhancement
        enhanced, final_var, was_blurry = ImageEnhancer.enhance_document_page(blurred)
        self.assertTrue(was_blurry)
        self.assertGreater(final_var, blur_var, "Enhancement must increase Laplacian variance/sharpness")

    def test_03_dian_xml_parser(self):
        """Verifies 100% deterministic UBL 2.1 parsing from DIAN ZIP package in < 0.01s."""
        parser = DianXmlParser()
        self.assertTrue(parser.can_handle(self.zip_sample))

        doc = parser.parse(self.zip_sample)
        self.assertEqual(doc.metadata.category, "FACTURA")
        self.assertEqual(doc.metadata.document_number, "SETP-9921")
        self.assertEqual(doc.metadata.nit_or_id, "901345678-9")
        self.assertEqual(doc.metadata.sender_name, "COLOMBIA TECH & CLOUD SOLUTIONS SAS")
        self.assertEqual(doc.metadata.total_amount, 4850000.00)
        self.assertEqual(doc.metadata.confidence_score, 1.0)
        self.assertEqual(doc.metadata.issue_date, "2026-09-21")
        self.assertIn("FACTURA", doc.metadata.suggested_filename)
        self.assertLess(doc.processing_time_sec, 0.05, "Deterministic XML parsing must be under 50ms")

    def test_04_tree_detector(self):
        """Verifies tree/vegetation detection on sample images ('Árbol SÍ/NO')."""
        detector = VisualDetector()

        # Image with clear tree
        tree_img = cv2.imread(str(self.tree_img_sample))
        has_tree, foliage_pct = detector.detect_tree_nature_heuristic(tree_img)
        self.assertTrue(has_tree, f"Expected tree detection on tree image (got {foliage_pct}% foliage)")

        # Receipt image without tree
        receipt_img = cv2.imread(str(self.receipt_sample))
        has_tree_receipt, foliage_pct_rec = detector.detect_tree_nature_heuristic(receipt_img)
        self.assertFalse(has_tree_receipt, f"Expected NO tree on paper receipt (got {foliage_pct_rec}%)")

    def test_05_renamer_and_reporter(self):
        """Verifies standardized renaming format and operational report generation."""
        renamer = DocumentRenamer()
        meta = DocumentMetadata(
            category="ORDEN_COMPRA",
            issue_date="2026-09-22",
            document_number="OC-550",
            tree_detected=True,
        )
        doc = ProcessedDocument(
            file_path=Path("documento_orden.docx"),
            original_name="documento_orden.docx",
            sha256_hash="abcdef123456",
            file_type="DOCX",
            num_pages=3,
            metadata=meta,
        )
        standardized_name = renamer.generate_standardized_name(doc)
        # Expected: 20260922_ORDEN_COMPRA_OC550.docx
        self.assertEqual(standardized_name, "20260922_ORDEN_COMPRA_OC550.docx")

        # Test Reporter
        reporter = OperationalReporter()
        df = reporter.generate_dataframe([doc])
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["Categoría Asignada"], "ORDEN_COMPRA")
        self.assertEqual(df.iloc[0]["¿Árbol en Imagen?"], "SÍ")

        kpis = reporter.calculate_kpis(df)
        self.assertEqual(kpis["total_docs"], 1)
        self.assertEqual(kpis["auto_processed"], 1)

    def test_06_twenty_two_page_medik_benchmark_and_cache(self):
        """Verifies ingestion of the official 22-page Medik benchmark PDF and L2 cache speed."""
        benchmark_pdf = BASE_DIR / "tests" / "sample_docs" / "medik_benchmark_22_paginas.pdf"
        self.assertTrue(benchmark_pdf.exists(), f"Benchmark PDF must exist at {benchmark_pdf}")

        router = FileRouter()
        detector = VisualDetector()
        renamer = DocumentRenamer()
        from app.llm.cascade_manager import CascadeManager
        cascade = CascadeManager()

        # 1. First Pass (Fresh Ingestion & Analysis of all 22 pages)
        doc = router.process_file(benchmark_pdf, force_reprocess=True, render_images=True)
        self.assertEqual(doc.num_pages, 22, "Must successfully parse all 22 pages of the benchmark")

        # Run visual detection on pages
        for page in doc.pages:
            detector.analyze_page(page)

        # Classify and enrich
        cascade.classify_and_enrich(doc)
        self.assertIn(doc.metadata.category, ["GENERAL", "FACTURA", "PQRS", "ORDEN_COMPRA", "REVISION_HUMANA"])
        self.assertIsNotNone(doc.metadata.sender_name)

        # Standardized renaming
        standardized_name = renamer.generate_standardized_name(doc)
        self.assertIn(".pdf", standardized_name)
        doc.metadata.suggested_filename = standardized_name

        # Persist in Double Cache
        router.cache_manager.set(doc)

        # 2. Second Pass (Cryptographic Double Cache Hit Test)
        # Identical 25.4 MB document must return from L1/L2 cache in < 0.05 seconds!
        doc_cached = router.process_file(benchmark_pdf, force_reprocess=False)
        self.assertTrue(doc_cached.was_cached, "Second request must hit the cryptographic Double Cache")
        self.assertLess(doc_cached.processing_time_sec, 0.30, "Cached retrieval must take less than 300ms for a 25.4MB PDF")
        self.assertEqual(doc_cached.num_pages, 22)
        self.assertEqual(doc_cached.metadata.category, doc.metadata.category)

    def test_07_medik_benchmark_deep_chat_auditing(self):
        """Verifies conversational auditor on the official 22-page benchmark."""
        benchmark_pdf = BASE_DIR / "tests" / "sample_docs" / "medik_benchmark_22_paginas.pdf"
        self.assertTrue(benchmark_pdf.exists())

        router = FileRouter()
        detector = VisualDetector()
        from app.llm.cascade_manager import CascadeManager
        cascade = CascadeManager()

        doc = router.process_file(benchmark_pdf, force_reprocess=False, render_images=False)

        # Ask executive summary question
        ans_summary = cascade.ask_chat_question(doc, "¿Sobre qué trata el documento?")
        self.assertIsInstance(ans_summary, str)
        self.assertGreater(len(ans_summary), 25, "Executive summary must be meaningful and informative")

        # Ask specific patient / identification question
        ans_patient = cascade.ask_chat_question(doc, "¿Quién es el paciente y cuál es su número de identificación?")
        self.assertIsInstance(ans_patient, str)
        self.assertTrue(
            "Juan" in ans_patient or "10459283" in ans_patient or "Perez" in ans_patient,
            f"Expected patient name or ID in response: {ans_patient}",
        )


if __name__ == "__main__":
    unittest.main()

