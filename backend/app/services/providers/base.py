"""
Interfaces (puertos) que cualquier proveedor de IA debe cumplir.

Todo el resto del sistema depende de estas interfaces, nunca de una
implementación concreta. Cambiar de proveedor (mock <-> Gemini <-> cualquier
otro) es agregar una clase nueva aquí y una línea en el factory, sin tocar
servicios ni endpoints.
"""
from abc import ABC, abstractmethod
from typing import TypedDict


class TicketEnrichment(TypedDict):
    ai_category: str
    ai_priority: str
    ai_summary: str
    ai_sentiment: str
    ai_urgency: str
    ai_assigned_team: str


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def enrich_ticket(
        self, *, subject: str, description: str, ticket_type: str, original_priority: str | None = None
    ) -> TicketEnrichment:
        """Genera categoría, prioridad, resumen, sentimiento, urgencia y equipo.

        `original_priority` es la prioridad reportada en el sistema de origen
        (puede ser None si vino vacía/inválida); se usa como punto de partida
        razonable, ya que normalmente refleja una evaluación humana real, y se
        ajusta según el contenido del ticket en vez de ignorarla por completo.
        """

    @abstractmethod
    def answer_question(self, *, question: str, context: str) -> str:
        """Responde una pregunta en lenguaje natural usando SOLO el contexto dado."""


class EmbeddingProvider(ABC):
    name: str

    @abstractmethod
    def fit(self, documents: list[str]) -> None:
        """Ajusta el modelo de embeddings sobre el corpus completo (si aplica)."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Devuelve un vector por cada texto de entrada."""
