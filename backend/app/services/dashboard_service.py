"""
Cálculo de KPIs y agregados para el dashboard. Toda la lógica de negocio de
"qué significa un buen resumen" vive aquí, no en el router ni en el frontend.
"""
from app.db.models import Ticket
from app.repositories.ticket_repository import TicketRepository


class DashboardService:
    def __init__(self, repo: TicketRepository):
        self._repo = repo

    def summary(self) -> dict:
        total = self._repo.count_all()

        priority_counts = dict(self._repo.group_count(Ticket.ai_priority))
        category_counts = dict(self._repo.group_count(Ticket.ai_category))
        team_counts = dict(self._repo.group_count(Ticket.ai_assigned_team))
        status_counts = dict(self._repo.group_count(Ticket.ticket_status))
        sentiment_counts = dict(self._repo.group_count(Ticket.ai_sentiment))
        product_counts = dict(self._repo.group_count(Ticket.product_purchased))

        critical_or_high = priority_counts.get("Critical", 0) + priority_counts.get("High", 0)

        all_tickets = self._repo.all_for_search()

        rating_values = [t.customer_satisfaction_rating for t in all_tickets if t.customer_satisfaction_rating]
        avg_satisfaction = round(sum(rating_values) / len(rating_values), 2) if rating_values else None

        # Tiempo de resolución = Time to Resolution - First Response Time,
        # solo para tickets que tienen ambas marcas y son temporalmente válidas.
        resolution_hours = [
            (t.time_to_resolution - t.first_response_time).total_seconds() / 3600
            for t in all_tickets
            if t.time_to_resolution and t.first_response_time
            and t.time_to_resolution >= t.first_response_time
        ]
        avg_resolution_hours = round(sum(resolution_hours) / len(resolution_hours), 1) if resolution_hours else None

        top_products = sorted(product_counts.items(), key=lambda kv: kv[1], reverse=True)[:5]

        return {
            "total_tickets": total,
            "critical_or_high_tickets": critical_or_high,
            "open_tickets": status_counts.get("Open", 0),
            "pending_tickets": status_counts.get("Pending Customer Response", 0),
            "closed_tickets": status_counts.get("Closed", 0),
            "avg_satisfaction_rating": avg_satisfaction,
            "avg_resolution_hours": avg_resolution_hours,
            "by_priority": priority_counts,
            "by_category": category_counts,
            "by_team": team_counts,
            "by_sentiment": sentiment_counts,
            "top_products": [{"product": p, "count": c} for p, c in top_products],
        }
