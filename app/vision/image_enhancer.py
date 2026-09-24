"""OpenCV Preprocessing and Image Restoration Pipeline for Degraded Scans.

Applies Laplacian blur detection, Unsharp Masking, Contrast Limited Adaptive
Histogram Equalization (CLAHE), and Deskewing to dramatically increase OCR and
vision accuracy on low-quality or mobile-scanned documents.
"""

from __future__ import annotations

import cv2
import numpy as np
from app.config import BLUR_VARIANCE_THRESHOLD


class ImageEnhancer:
    """Provides modular image restoration and quality assessment methods."""

    @staticmethod
    def calculate_blur_variance(image: np.ndarray) -> float:
        """Calculates the Laplacian variance of an image to measure sharpness.

        Args:
            image: Input image as a NumPy array (BGR or Grayscale).

        Returns:
            Float representing sharpness variance (e.g. < 100 indicates blurriness).
        """
        if image is None or image.size == 0:
            return 0.0

        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return float(laplacian.var())

    @classmethod
    def is_blurry(cls, image: np.ndarray, threshold: float = BLUR_VARIANCE_THRESHOLD) -> bool:
        """Determines if the image is considered blurry based on Laplacian variance.

        Args:
            image: Input image as NumPy array.
            threshold: Variance cutoff score.

        Returns:
            True if image is blurry, False if sharp.
        """
        variance = cls.calculate_blur_variance(image)
        return variance < threshold

    @staticmethod
    def apply_unsharp_mask(image: np.ndarray, sigma: float = 1.0, strength: float = 1.5) -> np.ndarray:
        """Sharpens blurred edges using an Unsharp Masking filter.

        Args:
            image: Input image (BGR or Grayscale).
            sigma: Standard deviation for Gaussian kernel.
            strength: Multiplier for the high-frequency edge component.

        Returns:
            Sharpened image.
        """
        blurred = cv2.GaussianBlur(image, (0, 0), sigma)
        sharpened = cv2.addWeighted(image, 1.0 + strength, blurred, -strength, 0)
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    @staticmethod
    def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple[int, int] = (8, 8)) -> np.ndarray:
        """Applies Contrast Limited Adaptive Histogram Equalization.

        Rescues faded text, washed-out ink, and irregular scan illumination.

        Args:
            image: Input image (BGR or Grayscale).
            clip_limit: Threshold for contrast limiting.
            tile_grid_size: Size of local contextual grid.

        Returns:
            Contrast-enhanced image.
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

        if len(image.shape) == 3:
            # Convert to LAB color space and equalize the L (Luminance) channel
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lab)
            l_equalized = clahe.apply(l_channel)
            lab_merged = cv2.merge((l_equalized, a_channel, b_channel))
            return cv2.cvtColor(lab_merged, cv2.COLOR_LAB2BGR)
        else:
            return clahe.apply(image)

    @staticmethod
    def deskew(image: np.ndarray) -> np.ndarray:
        """Detects document tilt angle and rotates the image back to horizontal orientation.

        Args:
            image: Input image array.

        Returns:
            Deskewed image array.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Invert colors: text as foreground (white) on black background
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Find all foreground pixels
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 100:
            return image  # Insufficient text to reliably determine tilt angle

        # Calculate minimum bounding rectangle around all text pixels
        angle = cv2.minAreaRect(coords)[-1]

        # Adjust angle range
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle

        # If tilt is negligible (< 0.5 degrees), avoid interpolation degradation
        if abs(angle) < 0.5 or abs(angle) > 45.0:
            return image

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image,
            matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
        return rotated

    @classmethod
    def enhance_document_page(cls, image: np.ndarray, force_enhance: bool = False) -> tuple[np.ndarray, float, bool]:
        """Runs the complete restoration pipeline on a single document page or image.

        Args:
            image: Raw image array from PDF or disk.
            force_enhance: If True, applies sharpening even if variance looks adequate.

        Returns:
            Tuple of (enhanced_image, blur_variance, was_blurry_flag).
        """
        if image is None or image.size == 0:
            return image, 0.0, False

        initial_variance = cls.calculate_blur_variance(image)
        was_blurry = initial_variance < BLUR_VARIANCE_THRESHOLD

        output_image = image.copy()

        # Step 1: Deskew document orientation
        output_image = cls.deskew(output_image)

        # Step 2: If blurry or forced, apply sharpening and contrast boost
        if was_blurry or force_enhance:
            output_image = cls.apply_unsharp_mask(output_image, sigma=1.2, strength=1.8)
            output_image = cls.apply_clahe(output_image, clip_limit=2.5)

        final_variance = cls.calculate_blur_variance(output_image)
        return output_image, final_variance, was_blurry
