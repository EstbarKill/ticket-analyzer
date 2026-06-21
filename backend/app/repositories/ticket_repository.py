"""
Repository Pattern: encapsula todas las consultas SQL para tickets.

Los servicios y los endpoints nunca construyen queries SQLAlchemy
directamente, siempre pasan por aquí. Esto facilita testear los servicios con
un repositorio falso y mantiene el ORM en una sola capa.
"""
import json
from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import ImportRun, Ticket
from app.services.data_cleaning import CleanedTicket


class TicketRepository:
    def __init__(self, db: Session):
        self._db = db

    def clear_all(self) -> None:
        self._db.query(Ticket).delete()
        self._db.commit()

    def bulk_create(self, tickets: list[Ticket]) -> None:
        self._db.add_all(tickets)
        self._db.commit()

    def to_orm(self, cleaned: CleanedTicket, enrichment: dict, provider_name: str) -> Ticket:
        return Ticket(
            source_ticket_id=cleaned.source_ticket_id,
            customer_name=cleaned.customer_name,
            customer_email=cleaned.customer_email,
            customer_age=cleaned.customer_age,
            customer_gender=cleaned.customer_gender,
            product_purchased=cleaned.product_purchased,
            date_of_purchase=cleaned.date_of_purchase,
            ticket_type=cleaned.ticket_type,
            ticket_subject=cleaned.ticket_subject,
            ticket_description=cleaned.ticket_description,
            ticket_status=cleaned.ticket_status,
            ticket_priority=cleaned.ticket_priority,
            ticket_channel=cleaned.ticket_channel,
            first_response_time=cleaned.first_response_time,
            time_to_resolution=cleaned.time_to_resolution,
            customer_satisfaction_rating=cleaned.customer_satisfaction_rating,
            ai_category=enrichment.get("ai_category"),
            ai_priority=enrichment.get("ai_priority"),
            ai_summary=enrichment.get("ai_summary"),
            ai_sentiment=enrichment.get("ai_sentiment"),
            ai_urgency=enrichment.get("ai_urgency"),
            ai_assigned_team=enrichment.get("ai_assigned_team"),
            ai_provider_used=provider_name,
            data_quality_notes=json.dumps(cleaned.notes, ensure_ascii=False),
        )

    def create_import_run(self, **kwargs) -> ImportRun:
        run = ImportRun(**kwargs)
        self._db.add(run)
        self._db.commit()
        return run

    def list_tickets(
        self,
        *,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        team: Optional[str] = None,
        product: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Ticket], int]:
        query = self._db.query(Ticket)
        if category:
            query = query.filter(Ticket.ai_category == category)
        if priority:
            query = query.filter(Ticket.ai_priority == priority)
        if status:
            query = query.filter(Ticket.ticket_status == status)
        if team:
            query = query.filter(Ticket.ai_assigned_team == team)
        if product:
            query = query.filter(Ticket.product_purchased == product)
        if date_from:
            query = query.filter(Ticket.date_of_purchase >= date_from)
        if date_to:
            query = query.filter(Ticket.date_of_purchase <= date_to)

        total = query.count()
        items = query.order_by(Ticket.id.desc()).offset(offset).limit(limit).all()
        return items, total

    def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        return self._db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def count_all(self) -> int:
        return self._db.query(Ticket).count()

    def group_count(self, column) -> list[tuple[str, int]]:
        rows = (
            self._db.query(column, func.count(Ticket.id))
            .filter(column.isnot(None))
            .group_by(column)
            .order_by(func.count(Ticket.id).desc())
            .all()
        )
        return [(value, count) for value, count in rows]

    def all_for_search(self) -> list[Ticket]:
        """Devuelve todos los tickets; usado por el servicio de /ask para
        filtrado estructurado en memoria (volumen bajo, no requiere índice)."""
        return self._db.query(Ticket).all()
