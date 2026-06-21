"""
Proveedor "mock" de LLM.

No llama a ningún servicio externo: usa reglas y palabras clave para producir
un enriquecimiento razonable. Sirve para desarrollar y probar todo el sistema
sin gastar en una API real, y para que el README pueda decir "clona, corre,
funciona" sin pedir una API key. La interfaz es idéntica a la del proveedor
real, así que cambiar de uno a otro es solo una variable de entorno.
"""
import re

from app.services.providers.base import LLMProvider, TicketEnrichment

TEAM_BY_TYPE = {
    "Technical issue": "Soporte Técnico",
    "Billing inquiry": "Facturación",
    "Refund request": "Facturación",
    "Cancellation request": "Retención de Clientes",
    "Product inquiry": "Ventas y Producto",
}

NEGATIVE_WORDS = [
    "frustrat", "angry", "terrible", "awful", "disappoint", "annoy", "unacceptable",
    "molest", "enojad", "frustrad", "pésimo", "terrible", "decepcion", "no funciona",
]
POSITIVE_WORDS = ["thank", "great", "love", "appreciate", "gracias", "excelente"]
URGENT_WORDS = ["urgent", "immediately", "asap", "right now", "urgente", "inmediato", "ya mismo"]

PRIORITY_ORDER = ["Low", "Medium", "High", "Critical"]


class MockLLMProvider(LLMProvider):
    name = "mock"

    def enrich_ticket(
        self, *, subject: str, description: str, ticket_type: str, original_priority: str | None = None
    ) -> TicketEnrichment:
        text = f"{subject or ''} {description or ''}".lower()

        category = ticket_type or "Product inquiry"

        urgency_hits = sum(1 for w in URGENT_WORDS if w in text)
        negative_hits = sum(1 for w in NEGATIVE_WORDS if w in text)
        positive_hits = sum(1 for w in POSITIVE_WORDS if w in text)

        # Punto de partida: la prioridad reportada originalmente, si es válida.
        # Suele reflejar una evaluación humana real; el contenido del ticket
        # se usa para subirla (nunca silenciosamente para bajarla mucho), no
        # para reemplazarla desde cero con cada llamada.
        base_idx = PRIORITY_ORDER.index(original_priority) if original_priority in PRIORITY_ORDER else 1
        if negative_hits >= 2 and urgency_hits >= 1:
            base_idx = min(base_idx + 2, 3)
        elif negative_hits >= 1 or urgency_hits >= 1:
            base_idx = min(base_idx + 1, 3)
        priority = PRIORITY_ORDER[base_idx]

        if negative_hits > positive_hits:
            sentiment = "Negativo"
        elif positive_hits > negative_hits:
            sentiment = "Positivo"
        else:
            sentiment = "Neutral"

        urgency = {"Low": "Baja", "Medium": "Media", "High": "Alta", "Critical": "Alta"}[priority]

        summary = self._summarize(description)
        team = TEAM_BY_TYPE.get(ticket_type, "Soporte Técnico")

        return TicketEnrichment(
            ai_category=category,
            ai_priority=priority,
            ai_summary=summary,
            ai_sentiment=sentiment,
            ai_urgency=urgency,
            ai_assigned_team=team,
        )

    def answer_question(self, *, question: str, context: str) -> str:
        if not context.strip():
            return (
                "No encontré información suficiente en los tickets ni en la base de "
                "conocimiento para responder esa pregunta con confianza."
            )
        lines = [
            "(respuesta generada en modo mock, sin LLM real — solo para probar la "
            "arquitectura sin gastar en una API)"
        ]
        for block in context.split("\n\n"):
            if block.startswith("Conteos agregados"):
                lines.append(block)
            elif block.startswith("Notas:"):
                lines.append(block)
        if len(lines) == 1:
            first_ticket_line = next(
                (l for l in context.splitlines() if l.startswith("- #")), None
            )
            lines.append(
                f"Tickets de referencia encontrados para tu pregunta. Ejemplo: {first_ticket_line}"
                if first_ticket_line
                else "No se encontraron tickets puntuales relacionados; revisa la base de conocimiento adjunta."
            )
        return "\n".join(lines)

    @staticmethod
    def _summarize(description: str, max_len: int = 140) -> str:
        if not description:
            return "Sin descripción disponible."
        # Quita el preámbulo repetitivo típico del dataset ("I'm having an issue with...").
        cleaned = re.sub(r"^I'?m having an issue with[^.]*\.\s*", "", description.strip())
        first_sentence = re.split(r"(?<=[.!?])\s", cleaned)[0]
        text = first_sentence if first_sentence else cleaned
        return text[:max_len].rstrip() + ("…" if len(text) > max_len else "")
