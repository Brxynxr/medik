"""Configuration settings for the SmartDoc Engine application.

Centralizes paths, environment variables, AI model selections, and threshold
constants for OCR, computer vision, and document routing.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

# Base project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "output"
CACHE_DB_PATH = DATA_DIR / "cache.db"
YOLO_MODEL_PATH = DATA_DIR / "models" / "yolov8n.pt"

# Ensure runtime directories exist
for directory in [DATA_DIR, UPLOADS_DIR, OUTPUT_DIR, YOLO_MODEL_PATH.parent]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys & Endpoints (Handled internally)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Model configurations
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
DEFAULT_GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Vision & OCR thresholds
# Images with Laplacian variance below this value will be flagged as blurry
# and enhanced using Unsharp Masking + CLAHE + Sauvola binarization
BLUR_VARIANCE_THRESHOLD = float(os.getenv("BLUR_VARIANCE_THRESHOLD", "120.0"))
YOLO_CONFIDENCE_THRESHOLD = float(os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.35"))

# Max pages to process for preview / deep OCR
MAX_PAGES_LIMIT = 50

# Supported mime extensions
SUPPORTED_EXTENSIONS = {
    ".pdf": "PDF Document",
    ".docx": "Word Document",
    ".zip": "DIAN Compressed Archive / ZIP",
    ".png": "Image (PNG)",
    ".jpg": "Image (JPEG)",
    ".jpeg": "Image (JPEG)",
    ".tiff": "Image (TIFF)",
    ".tif": "Image (TIFF)",
    ".bmp": "Image (BMP)",
    ".webp": "Image (WEBP)",
}

# RIWI Business categories and target routing departments
BUSINESS_CATEGORIES = {
    "FACTURA": "Tesorería / Cuentas por Pagar",
    "ORDEN_COMPRA": "Servicios Internos",
    "PQRS": "Servicio al Cliente (SAC)",
    "GENERAL": "Administración General",
    "REVISION_HUMANA": "Mesa de Control y Excepciones Humanas",
}
