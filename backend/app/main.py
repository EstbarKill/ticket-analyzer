import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ask, dashboard, health, tickets
from app.core.config import get_settings
from app.db.session import init_db
from app.services.knowledge_base import get_knowledge_base

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="API para ingerir, enriquecer con IA y analizar tickets de soporte.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(tickets.router)
app.include_router(dashboard.router)
app.include_router(ask.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    # Construye el índice de la base de conocimiento una sola vez al iniciar,
    # para que la primera llamada a /ask no pague ese costo.
    get_knowledge_base()
    logging.info(
        "Iniciado con llm_provider=%s embedding_provider=%s",
        settings.active_llm_provider,
        settings.active_embedding_provider,
    )
