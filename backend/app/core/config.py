"""
Configuración central de la aplicación.

Toda variable de entorno se lee en un solo lugar. El resto del código nunca
llama a os.environ directamente: depende de esta clase Settings, lo que hace
fácil testear y cambiar de proveedor sin tocar lógica de negocio.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- App ---
    app_name: str = "AI Support Ticket Analyzer"
    environment: str = "development"
    cors_origins: str = "http://localhost:3000"

    # --- Base de datos ---
    # SQLite por defecto: cero infraestructura para levantar el proyecto.
    # Para escalar a Postgres, basta cambiar esta URL (SQLAlchemy se encarga).
    database_url: str = f"sqlite:///{BASE_DIR / 'data' / 'tickets.db'}"

    # --- Dataset ---
    dataset_path: str = str(BASE_DIR / "dataset" / "tickets.csv")
    knowledge_base_dir: str = str(BASE_DIR / "knowledge_base")
    embeddings_cache_path: str = str(BASE_DIR / "data" / "kb_embeddings.json")

    # --- Proveedor de LLM ---
    # "mock"   -> heurística local, sin costo ni internet, útil para probar.
    # "gemini" -> usa la API real de Google Gemini.
    llm_provider: str = "mock"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash"

    # --- Proveedor de embeddings (para la base de conocimiento) ---
    # "mock"   -> TF-IDF local (scikit-learn), sin internet ni costo.
    # "gemini" -> embeddings reales de la API de Gemini.
    embedding_provider: str = "mock"
    gemini_embedding_model: str = "gemini-embedding-001"

    @property
    def active_llm_provider(self) -> str:
        """Si hay API key configurada y se pidió gemini, se usa; si no, mock."""
        if self.llm_provider == "gemini" and self.gemini_api_key:
            return "gemini"
        return "mock"

    @property
    def active_embedding_provider(self) -> str:
        if self.embedding_provider == "gemini" and self.gemini_api_key:
            return "gemini"
        return "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()
