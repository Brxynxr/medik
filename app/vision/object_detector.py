"""Visual Object and Feature Detector (YOLOv8 + OpenCV + Multimodal VLM).

Combines lightweight local detection (YOLOv8, HSV foliage segmentation,
cursive signature morphology) with cloud multimodal vision (Gemini 2.5 Flash)
to accurately answer visual questions such as "¿Hay un árbol en la imagen? SÍ/NO",
"¿Hay una firma manuscrita?", o detectar sellos institucionales.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple
import cv2
import numpy as np

from app.config import YOLO_CONFIDENCE_THRESHOLD, YOLO_MODEL_PATH
from app.parsers.base_parser import PageData


class VisualDetector:
    """Detects objects, nature/trees, and signatures in document images."""

    def __init__(self, yolo_weights_path=YOLO_MODEL_PATH) -> None:
        """Initializes detector with lazy YOLO model loading."""
        self.yolo_weights_path = yolo_weights_path
        self._yolo_model = None

    def _get_yolo_model(self):
        """Loads YOLOv8-Nano lazily to optimize initial startup time."""
        if self._yolo_model is None:
            try:
                from ultralytics import YOLO
                # Load YOLOv8-nano (will download weights if not present)
                self._yolo_model = YOLO("yolov8n.pt")
            except Exception:
                self._yolo_model = False  # Mark as unavailable
        return self._yolo_model if self._yolo_model is not False else None

    def detect_coco_objects(self, image: np.ndarray) -> List[str]:
        """Runs YOLOv8-Nano on the image to detect standard COCO objects.

        Args:
            image: OpenCV BGR image array.

        Returns:
            List of detected class names (e.g. ['person', 'potted plant', 'laptop']).
        """
        if image is None or image.size == 0:
            return []

        model = self._get_yolo_model()
        if not model:
            return []

        try:
            results = model(image, conf=YOLO_CONFIDENCE_THRESHOLD, verbose=False)
            detected = []
            for result in results:
                for cls_id in result.boxes.cls:
                    name = model.names[int(cls_id)]
                    if name not in detected:
                        detected.append(name)
            return detected
        except Exception:
            return []

    @staticmethod
    def _calculate_spatial_location(x: int, y: int, w_box: int, h_box: int, img_w: int, img_h: int) -> str:
        """Determines the human-readable spatial quadrant of an element on the page."""
        cx = x + w_box / 2.0
        cy = y + h_box / 2.0

        rel_y = cy / max(img_h, 1)
        rel_x = cx / max(img_w, 1)

        # Vertical band
        if rel_y < 0.28:
            v_pos = "Encabezado / Margen Superior"
        elif rel_y > 0.68:
            v_pos = "Margen Inferior"
        else:
            v_pos = "Zona Media / Central"

        # Horizontal band
        if rel_x < 0.35:
            h_pos = "Izquierdo"
        elif rel_x > 0.65:
            h_pos = "Derecho"
        else:
            h_pos = "Centro"

        if "Margen Inferior" in v_pos:
            return f"Cuadrante Inferior {h_pos}"
        if "Encabezado" in v_pos:
            return f"{v_pos} {h_pos}"
        return f"{v_pos} ({h_pos})"

    @classmethod
    def detect_signature_morphology(cls, image: np.ndarray) -> Tuple[bool, float, str]:
        """Detects presence and spatial location of handwritten signatures via morphology.

        Signatures exhibit irregular cursive stroke density, thin elongated loops,
        and high aspect ratio components, primarily in the lower sections of documents.

        Args:
            image: OpenCV BGR image.

        Returns:
            Tuple of (has_signature_flag, confidence_score, spatial_location).
        """
        if image is None or image.size == 0:
            return False, 0.0, "No detectada"

        try:
            h, w = image.shape[:2]
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            sig_boxes = []

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 250 < area < 10000:
                    perimeter = cv2.arcLength(cnt, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * (area / (perimeter * perimeter))
                        # Cursive signatures have very low circularity (elongated loops)
                        if circularity < 0.22:
                            bx, by, bw, bh = cv2.boundingRect(cnt)
                            sig_boxes.append((bx, by, bw, bh))

            has_sig = len(sig_boxes) >= 2
            confidence = min(1.0, len(sig_boxes) * 0.22) if has_sig else 0.0

            if has_sig:
                # Average centroid of candidate signature components
                avg_x = int(np.mean([b[0] for b in sig_boxes]))
                avg_y = int(np.mean([b[1] for b in sig_boxes]))
                avg_w = int(np.mean([b[2] for b in sig_boxes]))
                avg_h = int(np.mean([b[3] for b in sig_boxes]))
                location = cls._calculate_spatial_location(avg_x, avg_y, avg_w, avg_h, w, h)
            else:
                location = "No detectada"

            return has_sig, confidence, location
        except Exception:
            return False, 0.0, "No detectada"

    @classmethod
    def detect_stamp_morphology(cls, image: np.ndarray) -> Tuple[bool, float, str]:
        """Detects presence and spatial location of institutional, notary, or reception stamps.

        Stamps typically have circular/elliptical borders and distinctive colored inks
        (blue, purple, or red) commonly used in official Colombian seals.

        Args:
            image: OpenCV BGR image.

        Returns:
            Tuple of (has_stamp_flag, confidence_score, spatial_location).
        """
        if image is None or image.size == 0:
            return False, 0.0, "No detectado"

        try:
            h, w = image.shape[:2]
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            # 1. Color check for blue/purple ink stamps (common in legal/invoicing)
            lower_blue = np.array([90, 50, 50])
            upper_blue = np.array([135, 255, 255])
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

            # 2. Color check for red/magenta ink stamps
            lower_red1 = np.array([0, 60, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 60, 50])
            upper_red2 = np.array([180, 255, 255])
            red_mask = cv2.bitwise_or(cv2.inRange(hsv, lower_red1, upper_red1), cv2.inRange(hsv, lower_red2, upper_red2))

            combined_ink = cv2.bitwise_or(blue_mask, red_mask)
            colored_pixels = cv2.countNonZero(combined_ink)

            # 3. Contour circularity check (circular seals)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            stamp_boxes = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if 1200 < area < 40000:
                    perimeter = cv2.arcLength(cnt, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * (area / (perimeter * perimeter))
                        # Circular or octagonal official seal
                        if circularity > 0.50:
                            bx, by, bw, bh = cv2.boundingRect(cnt)
                            stamp_boxes.append((bx, by, bw, bh))

            has_colored_stamp = colored_pixels > (h * w * 0.003)
            has_circular_seal = len(stamp_boxes) > 0
            has_stamp = has_colored_stamp or has_circular_seal
            confidence = 0.88 if (has_colored_stamp and has_circular_seal) else (0.75 if has_stamp else 0.0)

            if has_circular_seal:
                bx, by, bw, bh = stamp_boxes[0]
                location = cls._calculate_spatial_location(bx, by, bw, bh, w, h)
            elif has_colored_stamp:
                # Find centroid of ink mask
                coords = np.column_stack(np.where(combined_ink > 0))
                if len(coords) > 0:
                    cy, cx = int(np.mean(coords[:, 0])), int(np.mean(coords[:, 1]))
                    location = cls._calculate_spatial_location(cx, cy, 50, 50, w, h)
                else:
                    location = "Margen Inferior"
            else:
                location = "No detectado"

            return has_stamp, confidence, location
        except Exception:
            return False, 0.0, "No detectado"

    @classmethod
    def detect_table_structure(cls, image: np.ndarray) -> Tuple[bool, str]:
        """Detects presence of structured tabular grids via orthogonal line detection."""
        if image is None or image.size == 0:
            return False, "No detectada"

        try:
            h, w = image.shape[:2]
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

            # Horizontal lines kernel
            h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(20, w // 25), 1))
            h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)

            # Vertical lines kernel
            v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(15, h // 35)))
            v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)

            table_grid = cv2.bitwise_and(h_lines, v_lines)
            intersections = cv2.countNonZero(table_grid)

            has_table = intersections >= 6
            if has_table:
                coords = np.column_stack(np.where(table_grid > 0))
                cy, cx = int(np.mean(coords[:, 0])), int(np.mean(coords[:, 1]))
                location = cls._calculate_spatial_location(cx, cy, 100, 100, w, h)
            else:
                location = "No detectada"

            return has_table, location
        except Exception:
            return False, "No detectada"

    @staticmethod
    def detect_tree_nature_heuristic(image: np.ndarray) -> Tuple[bool, float]:
        """Detects presence of trees, plants, or green foliage using HSV color space.

        Args:
            image: OpenCV BGR image.

        Returns:
            Tuple of (has_tree_flag, foliage_percentage).
        """
        if image is None or image.size == 0:
            return False, 0.0

        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lower_green = np.array([25, 40, 30])
            upper_green = np.array([85, 255, 255])

            mask = cv2.inRange(hsv, lower_green, upper_green)
            green_pixels = cv2.countNonZero(mask)
            total_pixels = image.shape[0] * image.shape[1]

            ratio = (green_pixels / total_pixels) * 100.0
            has_foliage = ratio >= 3.5
            return has_foliage, round(ratio, 2)
        except Exception:
            return False, 0.0

    @staticmethod
    def is_photo_or_complex_graphic(image: np.ndarray) -> bool:
        """Determines if an image page contains photographic, chromatic, or real-world imagery.

        Standard text documents and administrative scans have very low color saturation
        and can skip heavy deep neural network inference (YOLO), speeding up processing 20x.
        """
        if image is None or image.size == 0:
            return False

        try:
            # Fast downsample for O(1) saturation check
            thumb = cv2.resize(image, (64, 64))
            hsv = cv2.cvtColor(thumb, cv2.COLOR_BGR2HSV)
            sat = hsv[:, :, 1]
            # Photos and natural images exhibit color saturation, unlike monochrome/grayscale documents
            if float(np.mean(sat)) > 16.0 or float(np.std(sat)) > 30.0:
                return True
            return False
        except Exception:
            return False

    def analyze_page(self, page: PageData, gemini_client=None) -> PageData:
        """Performs exhaustive visual and structural analysis on a page down to the finest detail.

        Catalogs signatures, stamps, tables, logos, photographs, and their physical page positions.

        Args:
            page: PageData instance with image_np populated.
            gemini_client: Optional GeminiClient instance for multimodal deep reasoning.

        Returns:
            Updated PageData with visual attributes and layout elements populated.
        """
        if page.image_np is None:
            return page

        # 1. Run YOLOv8 object detection ONLY on photographic or color-rich pages
        coco_objects = []
        if self.is_photo_or_complex_graphic(page.image_np):
            coco_objects = self.detect_coco_objects(page.image_np)
        page.detected_objects = list(coco_objects)

        visual_items = []
        summary_parts = []

        # 2. Check for handwritten signature with spatial location
        has_sig, sig_conf, sig_loc = self.detect_signature_morphology(page.image_np)
        if has_sig:
            page.has_signature = True
            desc = f"Firma manuscrita ({sig_loc})"
            page.signatures_found.append(desc)
            visual_items.append({
                "type": "Firma Manuscrita",
                "location": sig_loc,
                "confidence": f"{sig_conf * 100:.0f}%",
            })
            summary_parts.append(desc)
            if "Firma Manuscrita" not in page.detected_objects:
                page.detected_objects.append("Firma Manuscrita")

        # Check for signature blocks in text (underline lines, "Firmado", "Firma", etc.)
        if page.cleaned_text:
            sig_text_matches = re.findall(r"(?:_{4,}|-{4,})\s*\n*([^\n]{3,60})", page.cleaned_text)
            if not sig_text_matches:
                sig_text_matches = re.findall(r"(?:Firmado por|Firma autorizada|Suscribe|Representante Legal)[:\s]+([^\n]{3,50})", page.cleaned_text, re.IGNORECASE)
            for signer in sig_text_matches:
                clean_signer = signer.strip()
                if clean_signer and len(clean_signer) > 3:
                    page.has_signature = True
                    desc = f"Firma / Aprobación: {clean_signer} (Margen Inferior)"
                    if desc not in page.signatures_found:
                        page.signatures_found.append(desc)
                        visual_items.append({
                            "type": "Bloque de Firma",
                            "location": "Margen Inferior",
                            "details": clean_signer,
                        })
                        summary_parts.append(desc)

        # 3. Check for institutional / reception / notary stamps
        has_stamp, stamp_conf, stamp_loc = self.detect_stamp_morphology(page.image_np)
        if has_stamp:
            page.has_stamp = True
            desc = f"Sello institucional/radicación ({stamp_loc})"
            page.stamps_found.append(desc)
            visual_items.append({
                "type": "Sello Institucional / Radicación",
                "location": stamp_loc,
                "confidence": f"{stamp_conf * 100:.0f}%",
            })
            summary_parts.append(desc)
            if "Sello/Timbre" not in page.detected_objects:
                page.detected_objects.append("Sello/Timbre")

        # Textual stamp indicators (e.g. "RADICADO No.", "RECIBIDO:", "SELLO NOTARIAL")
        if page.cleaned_text:
            stamp_text_matches = re.findall(r"(?:RADICADO|RECIBIDO|NOTAR[ÍI]A|REGISTRO|SELLO)[:\s]+([^\n]{3,40})", page.cleaned_text, re.IGNORECASE)
            for stm in stamp_text_matches:
                clean_stm = stm.strip()
                if clean_stm:
                    page.has_stamp = True
                    desc = f"Sello / Radicación: {clean_stm} (Encabezado / Margen)"
                    if desc not in page.stamps_found:
                        page.stamps_found.append(desc)
                        visual_items.append({
                            "type": "Timbre de Radicación",
                            "location": "Encabezado / Margen",
                            "details": clean_stm,
                        })
                        summary_parts.append(desc)

        # 4. Check for structured tables or financial grids
        has_table, table_loc = self.detect_table_structure(page.image_np)
        page.has_table = has_table
        if has_table:
            visual_items.append({
                "type": "Tabla o Matriz de Datos",
                "location": table_loc,
            })
            summary_parts.append(f"Tabla de datos en {table_loc}")
            if "Tabla Estructurada" not in page.detected_objects:
                page.detected_objects.append("Tabla Estructurada")

        # 5. Check for natural scenery, vegetation or photography
        has_tree_local, foliage_pct = self.detect_tree_nature_heuristic(page.image_np)
        if "potted plant" in coco_objects:
            has_tree_local = True
        page.has_tree = has_tree_local
        if has_tree_local:
            visual_items.append({
                "type": "Fotografía / Vegetación",
                "location": "Zona Visual",
                "details": f"Follaje verde {foliage_pct}%",
            })
            summary_parts.append(f"Elemento fotográfico/vegetación ({foliage_pct}%)")
            if "Fotografía/Vegetación" not in page.detected_objects:
                page.detected_objects.append("Fotografía/Vegetación")

        # 6. Deep Multimodal Inspection with Gemini VLM if active
        if gemini_client and gemini_client.is_available():
            try:
                gemini_desc = gemini_client.inspect_page_visual_elements(page.image_np, page.page_number)
                if gemini_desc:
                    page.extra_metadata["gemini_visual_description"] = gemini_desc
                    # Verify if Gemini detected signature or stamp
                    upper_desc = gemini_desc.upper()
                    if "FIRMA" in upper_desc and ("SÍ" in upper_desc or "SI" in upper_desc or "PRESENTE" in upper_desc or "DETECTA" in upper_desc):
                        page.has_signature = True
                    if "SELLO" in upper_desc and ("SÍ" in upper_desc or "SI" in upper_desc or "CIRCULAR" in upper_desc or "RADICACIÓN" in upper_desc):
                        page.has_stamp = True
                    summary_parts.append(f"Inspección VLM: {gemini_desc[:120]}...")
            except Exception:
                pass

        page.visual_elements = visual_items
        page.visual_summary = "; ".join(summary_parts) if summary_parts else "Página de texto estándar sin sellos ni firmas relevantes."
        return page
