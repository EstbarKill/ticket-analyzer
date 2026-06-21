"""
Factory de proveedores.

Único lugar del código que sabe qué implementación concreta existe detrás de
cada interfaz. El resto de servicios solo pide get_llm_provider() /
get_embedding_provider() y trabaja contra la interfaz abstracta.
"""
from functools import lru_cache

from app.core.config import get_settings
from app.services.providers.base import EmbeddingProvider, LLMProvider
from app.services.providers.gemini_embeddings import GeminiEmbeddingProvider
from app.services.providers.gemini_llm import GeminiLLMProvider
from app.services.providers.mock_embeddings import MockEmbeddingProvider
from app.services.providers.mock_llm import MockLLMProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.active_llm_provider == "gemini":
        return GeminiLLMProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)
    return MockLLMProvider()


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.active_embedding_provider == "gemini":
        return GeminiEmbeddingProvider(api_key=settings.gemini_api_key, model=settings.gemini_embedding_model)
    return MockEmbeddingProvider()
