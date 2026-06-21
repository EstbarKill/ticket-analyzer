"""
Proveedor "mock" de embeddings: TF-IDF local con scikit-learn.

Para un puñado de documentos markdown (la base de conocimiento), TF-IDF da
una búsqueda semántica razonable sin pagar por una API ni descargar un modelo
de cientos de MB. La interfaz es la misma que la del proveedor real de
Gemini, así que sirve de reemplazo directo y demuestra que la arquitectura
permite intercambiar el motor de embeddings sin tocar el resto del código.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.services.providers.base import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    name = "mock"

    def __init__(self):
        self._vectorizer = TfidfVectorizer(stop_words=None, max_features=2048)
        self._fitted = False

    def fit(self, documents: list[str]) -> None:
        self._vectorizer.fit(documents)
        self._fitted = True

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not self._fitted:
            # Si no se ajustó antes (por ejemplo, una sola pregunta suelta),
            # se ajusta sobre la marcha con lo que haya disponible.
            self._vectorizer.fit(texts)
            self._fitted = True
        matrix = self._vectorizer.transform(texts)
        return matrix.toarray().astype(np.float32).tolist()
