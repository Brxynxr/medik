"""Google Gemini Client utilizing the official modern google-genai SDK.

Handles multimodal visual Q&A (e.g. tree detection, handwritten signature
verification, degraded receipt reading) and deep document understanding.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple
import cv2
import numpy as np

from app.config import DEFAULT_GEMINI_MODEL, GEMINI_API_KEY


class GeminiClient:
    """Manages interactions with the Google Gemini API using the official google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_GEMINI_MODEL) -> None:
        """Initializes the Gemini client.

        Args:
            api_key: Gemini API key. If omitted, uses GEMINI_API_KEY from config or env.
            model: Gemini model identifier (e.g. 'gemini-2.5-flash').
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
        self.model_name = model
        self._client = None

    def _get_client(self):
        """Lazily instantiates the official google.genai.Client."""
        if self._client is None and self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None
        return self._client

    def is_available(self) -> bool:
        """Checks if the client has a configured API key and SDK available."""
        return bool(self.api_key and self._get_client() is not None)

    def _generate_with_fallback(self, contents: Any, config: Any = None) -> Any:
        """Executes generate_content across candidate Gemini models to ensure high availability."""
        client = self._get_client()
        if not client:
            raise RuntimeError("Gemini client not initialized.")

        candidate_models = ["gemini-3.5-flash-lite", self.model_name, "gemini-flash-lite-latest", "gemini-3.6-flash"]
        # De-duplicate while preserving order
        seen = set()
        unique_models = [m for m in candidate_models if not (m in seen or seen.add(m))]

        last_error = None
        for model in unique_models:
            try:
                return client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config,
                )
            except Exception as exc:
                last_error = exc
                continue
        raise last_error or RuntimeError("Todos los modelos de Gemini fallaron.")

    def ask_visual_question(self, image_np: np.ndarray, question: str) -> Tuple[str, str]:
        """Performs multimodal visual reasoning on an image.

        Args:
            image_np: OpenCV BGR image array.
            question: Question to ask about the image.

        Returns:
            Tuple of (short_answer, detailed_description).
        """
        client = self._get_client()
        if not client or image_np is None or image_np.size == 0:
            return "NO_DISPONIBLE", "Cliente Gemini no configurado o imagen vacía."

        try:
            from google.genai import types

            # Encode OpenCV BGR to JPEG bytes
            success, buffer = cv2.imencode(".jpg", image_np, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not success:
                return "ERROR", "Fallo al codificar la imagen en JPEG."
            image_bytes = buffer.tobytes()

            response = self._generate_with_fallback(
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    (
                        f"Instrucción: Analiza minuciosamente esta página o imagen de documento.\n"
                        f"Pregunta: {question}\n"
                        f"Regla: Comienza tu respuesta con 'SÍ' o 'NO' en mayúsculas si es una pregunta de sí o no, "
                        f"y proporciona una explicación detallada indicando ubicación (ej. 'cuadrante inferior derecho', 'encabezado') "
                        f"y cualquier texto, firma, sello, tabla o elemento visible."
                    ),
                ],
                config=types.GenerateContentConfig(temperature=0.1),
            )
            text_resp = response.text.strip()
            first_word = text_resp.split()[0].upper().replace(",", "").replace(".", "") if text_resp else "NO"
            return first_word, text_resp
        except Exception as exc:
            return "ERROR", f"Excepción en consulta Gemini: {str(exc)}"

    def inspect_page_visual_elements(self, image_np: np.ndarray, page_num: int) -> str:
        """Scans page down to the finest detail for signatures, stamps, tables, logos, and handwritten notes."""
        client = self._get_client()
        if not client or image_np is None or image_np.size == 0:
            return ""

        try:
            from google.genai import types
            success, buffer = cv2.imencode(".jpg", image_np, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if not success:
                return ""
            image_bytes = buffer.tobytes()

            prompt = (
                f"Analiza con máximo detalle la página {page_num} de este documento e identifica todos los elementos visuales y estructurales:\n"
                f"- ¿Hay firmas manuscritas? ¿Dónde están ubicadas exactamente (ej. inferior derecha) y de quién son si es legible?\n"
                f"- ¿Hay sellos, timbres de radicación, de recibido o notariales? ¿En qué posición y qué texto o forma tienen?\n"
                f"- ¿Hay tablas, matrices de datos o especificaciones?\n"
                f"- ¿Hay logotipos institucionales, membretes, fotografías o diagramas?\n"
                f"- ¿Hay anotaciones, fechas o correcciones manuscritas a mano?\n"
                f"Responde de manera estructurada y concisa con viñetas para catalogar esta página."
            )

            response = self._generate_with_fallback(
                contents=[
                    types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt,
                ],
                config=types.GenerateContentConfig(temperature=0.1),
            )
            return response.text.strip()
        except Exception:
            return ""

    def classify_and_extract(self, text: str) -> Dict[str, Any]:
        """Classifies document text and extracts fiscal metadata using Gemini.

        Args:
            text: Extracted document text.

        Returns:
            Dictionary matching the DocumentMetadata structure.
        """
        client = self._get_client()
        if not client:
            return {}

        prompt = f"""
Eres el clasificador y extractor oficial del buzón corporativo de RIWI Barranquilla (info@riwi.io).
Analiza el siguiente texto de un documento recibido y clasifícalo estrictamente en una de las siguientes categorías empresariales:
1. FACTURA (Cuentas por pagar, cobros, facturas electrónicas)
2. ORDEN_COMPRA (Adquisición de productos o servicios para la empresa)
3. PQRS (Peticiones, quejas, reclamos, solicitudes de garantía o soporte de clientes)
4. GENERAL (Comunicaciones administrativas, avisos generales)
5. REVISION_HUMANA (Documentos ilegibles, sospechosos, ambiguos o contradictorios)

Devuelve ÚNICAMENTE un objeto JSON válido con la siguiente estructura:
{{
  "category": "FACTURA | ORDEN_COMPRA | PQRS | GENERAL | REVISION_HUMANA",
  "target_department": "Tesorería / Cuentas por Pagar | Servicios Internos | Servicio al Cliente (SAC) | Administración General | Mesa de Control y Excepciones Humanas",
  "confidence_score": 0.95,
  "document_number": "string o null",
  "nit_or_id": "string o null",
  "sender_name": "string o null",
  "issue_date": "YYYY-MM-DD o null",
  "due_date": "YYYY-MM-DD o null",
  "total_amount": 1500000.0,
  "currency": "COP",
  "order_type": "PRODUCTO | SERVICIO | null",
  "is_exception": false,
  "exception_reason": "string o null"
}}

Texto del documento:
\"\"\"{text[:4000]}\"\"\"
"""
        try:
            from google.genai import types
            response = self._generate_with_fallback(
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )
            data = json.loads(response.text)
            return data
        except Exception:
            return {}

    def chat_qa(self, document_context: str, user_question: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """Answers user queries grounded in the extracted document context.

        Args:
            document_context: Full or relevant chunks of document text and visual catalog.
            user_question: The question asked by the user in the UI.
            history: Optional list of previous chat turns.

        Returns:
            Concise, factual answer with page citations.
        """
        client = self._get_client()
        if not client:
            return "Gemini API no está disponible."

        system_instruction = (
            "Eres el Auditor y Asistente Documental de RIWI. "
            "Responde preguntas del usuario basándote en el texto, páginas y catálogo de elementos visuales provistos. "
            "Si te preguntan por firmas, sellos, membretes, fotos, cláusulas, valores o fechas, especifica exactamente "
            "en qué página y en qué ubicación física se encuentran (ej. 'Página 20, esquina inferior derecha'). "
            "Si el documento no contiene el dato consultado, decláralo con claridad."
        )

        prompt = f"""
Contexto del documento analizado (incluye texto por página e inventario visual exhaustivo):
\"\"\"{document_context[:45000]}\"\"\"

Pregunta del usuario:
{user_question}
"""
        try:
            from google.genai import types
            response = self._generate_with_fallback(
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                ),
            )
            return response.text.strip()
        except Exception as exc:
            return f"Error al consultar Gemini: {str(exc)}"
