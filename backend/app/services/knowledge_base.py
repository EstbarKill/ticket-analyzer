"""
Base de conocimiento: carga los markdown, los divide en fragmentos (chunks)
y permite buscar los más relevantes para una pregunta usando el proveedor de
embeddings activo (mock con TF-IDF, o Gemini).

Se mantiene todo en memoria (no se usa pgvector ni una base vectorial
externa): para 5 documentos cortos esto es simple, rápido y suficiente. El
índice se reconstruye al iniciar la app.
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from app.core.config import get_settings
from app.services.providers.base import EmbeddingProvider
from app.services.providers.factory import get_embedding_provider


@dataclass
class KnowledgeChunk:
    source: str
    text: str
    vector: list[float] | None = None


def _split_into_chunks(text: str, source: str) -> list[KnowledgeChunk]:
    """Divide un markdown por secciones (##) para tener chunks con contexto propio."""
    chunks: list[KnowledgeChunk] = []
    current = []
    for line in text.splitlines():
        if line.startswith("## ") and current:
            chunks.append(KnowledgeChunk(source=source, text="\n".join(current).strip()))
            current = []
        current.append(line)
    if current:
        chunks.append(KnowledgeChunk(source=source, text="\n".join(current).strip()))
    return [c for c in chunks if c.text]


class KnowledgeBase:
    def __init__(self, kb_dir: str, embedding_provider: EmbeddingProvider):
        self._kb_dir = Path(kb_dir)
        self._embedding_provider = embedding_provider
        self._chunks: list[KnowledgeChunk] = []

    def build_index(self) -> None:
        self._chunks = []
        for md_file in sorted(self._kb_dir.glob("*.md")):
            text = md_file.read_text(encoding="utf-8")
            self._chunks.extend(_split_into_chunks(text, source=md_file.stem))

        if not self._chunks:
            return

        self._embedding_provider.fit([c.text for c in self._chunks])
        vectors = self._embedding_provider.embed([c.text for c in self._chunks])
        for chunk, vector in zip(self._chunks, vectors):
            chunk.vector = vector

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeChunk]:
        if not self._chunks:
            return []
        query_vector = np.array(self._embedding_provider.embed([query])[0])
        scored = []
        for chunk in self._chunks:
            doc_vector = np.array(chunk.vector)
            denom = (np.linalg.norm(query_vector) * np.linalg.norm(doc_vector)) or 1e-9
            score = float(np.dot(query_vector, doc_vector) / denom)
            scored.append((score, chunk))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]


@lru_cache
def get_knowledge_base() -> KnowledgeBase:
    settings = get_settings()
    kb = KnowledgeBase(settings.knowledge_base_dir, get_embedding_provider())
    kb.build_index()
    return kb
