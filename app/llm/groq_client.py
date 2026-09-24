"""Groq Cloud Client for Ultra-Fast (0.2s) LLaMA 3.3 70B Document Reasoning.

Provides high-speed text categorization and information extraction at zero
monetary cost using Groq's high-throughput LPU cloud infrastructure.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from app.config import DEFAULT_GROQ_MODEL, GROQ_API_KEY


class GroqClient:
    """Manages text inference with Groq Cloud."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_GROQ_MODEL) -> None:
        """Initializes the Groq client.

        Args:
            api_key: Groq API key. If omitted, uses GROQ_API_KEY from config or env.
            model: Groq model identifier (e.g. 'llama-3.3-70b-versatile').
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or GROQ_API_KEY
        self.model_name = model
        self._client = None

    def _get_client(self):
        """Lazily instantiates the groq.Groq client."""
        if self._client is None and self.api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except Exception:
                self._client = None
        return self._client

    def is_available(self) -> bool:
        """Checks if Groq API key is present and client initialized."""
        return bool(self.api_key and self._get_client() is not None)

    def classify_and_extract(self, text: str) -> Dict[str, Any]:
        """Classifies document text and extracts fiscal fields using Groq.

        Args:
            text: Document text snippet.

        Returns:
            Dictionary with classification and metadata fields.
        """
        client = self._get_client()
        if not client:
            return {}

        prompt = f"""
Clasifica este texto para el buzón de RIWI Barranquilla en una de las siguientes categorías:
FACTURA, ORDEN_COMPRA, PQRS, GENERAL, REVISION_HUMANA.

Responde ÚNICAMENTE un JSON válido con este formato exacto:
{{
  "category": "FACTURA | ORDEN_COMPRA | PQRS | GENERAL | REVISION_HUMANA",
  "target_department": "Tesorería / Cuentas por Pagar | Servicios Internos | Servicio al Cliente (SAC) | Administración General | Mesa de Control y Excepciones Humanas",
  "confidence_score": 0.95,
  "document_number": "string o null",
  "nit_or_id": "string o null",
  "sender_name": "string o null",
  "issue_date": "YYYY-MM-DD o null",
  "due_date": "YYYY-MM-DD o null",
  "total_amount": 100000.0,
  "currency": "COP",
  "order_type": "PRODUCTO | SERVICIO | null",
  "is_exception": false,
  "exception_reason": "string o null"
}}

Texto a analizar:
\"\"\"{text[:4000]}\"\"\"
"""
        candidate_models = [self.model_name, "qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
        for model in candidate_models:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Eres un asistente de clasificación empresarial que responde exclusivamente en JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    model=model,
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )
                content = chat_completion.choices[0].message.content
                return json.loads(content)
            except Exception:
                continue
        return {}

    def chat_qa(self, document_context: str, user_question: str) -> str:
        """Answers queries using Groq cloud models with automatic fallback."""
        client = self._get_client()
        if not client:
            return "Groq API no disponible."

        candidate_models = [self.model_name, "qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
        for model in candidate_models:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Eres el Asistente Experto de Auditoría Documental de RIWI. Responde preguntas "
                                "con base en el contexto y metadatos provistos. Sé exhaustivo, minucioso y cita las páginas y ubicaciones físicas exactas."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Contexto:\n\"\"\"{document_context[:25000]}\"\"\"\n\nPregunta: {user_question}",
                        },
                    ],
                    model=model,
                    temperature=0.2,
                )
                return chat_completion.choices[0].message.content.strip()
            except Exception:
                continue
        return "No fue posible obtener respuesta de Groq."
