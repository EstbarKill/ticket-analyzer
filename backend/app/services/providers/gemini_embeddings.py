"""
Proveedor real de embeddings: Google Gemini (modelo gemini-embedding-001).

Se hace una llamada por texto a embedContent. Para el tamaño de esta base de
conocimiento (un puñado de documentos markdown) esto es más que suficiente;
si la base creciera mucho, lo natural sería migrar a batchEmbedContents.
"""
import logging

import httpx

from app.services.providers.base import EmbeddingProvider

logger = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiEmbeddingProvider(EmbeddingProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str):
        self._api_key = api_key
        self._model = model
        self._client = httpx.Client(timeout=30.0)

    def fit(self, documents: list[str]) -> None:
        # Gemini embeddings no requieren ajuste previo: cada texto se embebe
        # de forma independiente. Se mantiene el método por compatibilidad
        # con la interfaz EmbeddingProvider.
        return None

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = []
        url = f"{GEMINI_BASE_URL}/{self._model}:embedContent"
        for text in texts:
            try:
                response = self._client.post(
                    url,
                    headers={"x-goog-api-key": self._api_key, "Content-Type": "application/json"},
                    json={"model": f"models/{self._model}", "content": {"parts": [{"text": text}]}},
                )
                response.raise_for_status()
                vectors.append(response.json()["embedding"]["values"])
            except (httpx.HTTPError, KeyError) as exc:
                logger.warning("Fallo al generar embedding con Gemini: %s", exc)
                vectors.append([0.0] * 768)
        return vectors
