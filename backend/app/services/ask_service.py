"""
Orquestación de /ask (RAG).

Pregunta -> (a) búsqueda semántica en la base de conocimiento,
            (b) filtrado estructurado sobre los tickets ya enriquecidos, y
            (c) agregados simples (conteos por producto/categoría/equipo)
         -> se construye un contexto con las tres fuentes
         -> se llama al LLM con ese contexto, nunca se responde "a pelo".

La recuperación sobre tickets es estructurada (por fecha/categoría/prioridad/
producto) en vez de vectorial: los tickets ya tienen campos categóricos
limpios gracias al pipeline de enriquecimiento, así que filtrar por esos
campos da mejores resultados que buscar por similitud de texto libre, y es
mucho más simple. Los agregados cubren preguntas tipo "qué producto/categoría
genera más quejas", donde la respuesta depende de contar sobre todo el
dataset, no de mirar un puñado de tickets individuales.
"""
import re
from collections import Counter
from datetime import datetime, timedelta, timezone

from app.db.models import Ticket
from app.repositories.ticket_repository import TicketRepository
from app.services.knowledge_base import KnowledgeBase
from app.services.providers.base import LLMProvider

PRIORITY_WORDS = {
    "crítico": "Critical", "critico": "Critical", "critical": "Critical",
    "alta": "High", "high": "High",
    "media": "Medium", "medium": "Medium",
    "baja": "Low", "low": "Low",
}
COMPLAINT_WORDS = ["queja", "quejas", "molesto", "negativo", "negativos", "reclamo", "reclamos"]
RANKING_WORDS = ["más", "mas", "mayor", "top", "ranking", "cuáles", "cuales"]


def _filter_with_fallback(candidates: list[Ticket], predicate) -> tuple[list[Ticket], bool]:
    """Aplica un filtro; si no deja nada, devuelve la lista original sin tocar
    (con un flag para que el contexto pueda avisar que no hubo coincidencias)."""
    filtered = [t for t in candidates if predicate(t)]
    if filtered:
        return filtered, True
    return candidates, False


def _find_relevant_tickets(question: str, tickets: list[Ticket], max_results: int = 8) -> tuple[list[Ticket], list[str]]:
    q = question.lower()
    candidates = tickets
    notes: list[str] = []

    now = datetime.now(timezone.utc)
    if "esta semana" in q or "última semana" in q or "ultima semana" in q:
        cutoff = now - timedelta(days=7)
        candidates, matched = _filter_with_fallback(
            candidates, lambda t: t.date_of_purchase and t.date_of_purchase.replace(tzinfo=timezone.utc) >= cutoff
        )
        if not matched:
            notes.append("No hay tickets de los últimos 7 días en el dataset; se muestran los más relevantes en general.")
    elif "este mes" in q or "último mes" in q or "ultimo mes" in q:
        cutoff = now - timedelta(days=30)
        candidates, matched = _filter_with_fallback(
            candidates, lambda t: t.date_of_purchase and t.date_of_purchase.replace(tzinfo=timezone.utc) >= cutoff
        )
        if not matched:
            notes.append("No hay tickets del último mes en el dataset; se muestran los más relevantes en general.")

    for word, priority in PRIORITY_WORDS.items():
        if word in q:
            candidates, _ = _filter_with_fallback(candidates, lambda t: t.ai_priority == priority)
            break

    if any(w in q for w in COMPLAINT_WORDS):
        candidates, matched = _filter_with_fallback(candidates, lambda t: t.ai_sentiment == "Negativo")
        if matched:
            notes.append("Se priorizaron tickets con sentimiento negativo, asociado a quejas.")

    products = {t.product_purchased for t in tickets if t.product_purchased}
    for product in products:
        if product.lower() in q:
            candidates, _ = _filter_with_fallback(candidates, lambda t: t.product_purchased == product)
            break

    # Si después de filtrar sigue habiendo muchos candidatos empatados (p. ej.
    # ningún filtro aplicó), se priorizan los tickets más recientes en vez de
    # devolver siempre el mismo orden arbitrario de la base de datos.
    candidates = sorted(candidates, key=lambda t: t.date_of_purchase or datetime.min, reverse=True)
    return candidates[:max_results], notes


def _build_aggregates(question: str, tickets: list[Ticket]) -> str:
    """Agregados simples, útiles para preguntas tipo ranking ('qué producto
    genera más quejas', 'qué categoría es más frecuente')."""
    q = question.lower()
    if not any(w in q for w in RANKING_WORDS) and not any(w in q for w in COMPLAINT_WORDS):
        return ""

    is_complaint_question = any(w in q for w in COMPLAINT_WORDS)
    subset = [t for t in tickets if t.ai_sentiment == "Negativo"] if is_complaint_question else tickets

    def top(counter: Counter, n: int = 5) -> str:
        return ", ".join(f"{k} ({v})" for k, v in counter.most_common(n)) or "sin datos"

    by_product = Counter(t.product_purchased for t in subset if t.product_purchased)
    by_category = Counter(t.ai_category for t in subset if t.ai_category)
    by_team = Counter(t.ai_assigned_team for t in subset if t.ai_assigned_team)

    label = "con sentimiento negativo (quejas)" if is_complaint_question else "en total"
    return (
        f"Conteos agregados sobre tickets {label}:\n"
        f"- Por producto: {top(by_product)}\n"
        f"- Por categoría: {top(by_category)}\n"
        f"- Por equipo asignado: {top(by_team)}"
    )


def _format_tickets_context(tickets: list[Ticket]) -> str:
    if not tickets:
        return "No se encontraron tickets relevantes para esta pregunta."
    lines = ["Tickets relevantes (muestra, no es la totalidad):"]
    for t in tickets:
        lines.append(
            f"- #{t.source_ticket_id} | producto: {t.product_purchased} | "
            f"categoría IA: {t.ai_category} | prioridad IA: {t.ai_priority} | "
            f"sentimiento: {t.ai_sentiment} | equipo: {t.ai_assigned_team} | "
            f"resumen: {t.ai_summary}"
        )
    return "\n".join(lines)


def _format_kb_context(chunks) -> str:
    if not chunks:
        return "No se encontró documentación relevante en la base de conocimiento."
    lines = ["Documentos de la base de conocimiento:"]
    for chunk in chunks:
        lines.append(f"[{chunk.source}]\n{chunk.text}")
    return "\n\n".join(lines)


class AskService:
    def __init__(self, repo: TicketRepository, knowledge_base: KnowledgeBase, llm_provider: LLMProvider):
        self._repo = repo
        self._kb = knowledge_base
        self._llm = llm_provider

    def ask(self, question: str) -> dict:
        question = re.sub(r"\s+", " ", question).strip()
        if not question:
            return {"answer": "Por favor escribe una pregunta.", "supporting_tickets": [], "supporting_documents": []}

        all_tickets = self._repo.all_for_search()
        if not all_tickets:
            return {
                "answer": "Todavía no hay tickets importados. Ejecuta primero POST /tickets/import.",
                "supporting_tickets": [],
                "supporting_documents": [],
            }

        relevant_tickets, notes = _find_relevant_tickets(question, all_tickets)
        aggregates = _build_aggregates(question, all_tickets)
        kb_chunks = self._kb.search(question, top_k=3)

        context_parts = [_format_tickets_context(relevant_tickets)]
        if aggregates:
            context_parts.append(aggregates)
        if notes:
            context_parts.append("Notas: " + " ".join(notes))
        context_parts.append(_format_kb_context(kb_chunks))
        context = "\n\n".join(context_parts)

        answer = self._llm.answer_question(question=question, context=context)

        return {
            "answer": answer,
            "supporting_tickets": [t.source_ticket_id for t in relevant_tickets],
            "supporting_documents": [c.source for c in kb_chunks],
        }
