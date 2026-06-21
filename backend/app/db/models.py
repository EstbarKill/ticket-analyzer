"""
Modelos de base de datos (SQLAlchemy).

Se mantiene un único modelo Ticket que combina los campos originales del CSV
con los campos enriquecidos por IA (prefijo ai_). Separar esto en dos tablas
(tickets / ticket_analysis) es razonable en un sistema más grande, pero para
este alcance una sola tabla ancha es más simple de consultar y de mantener,
sin perder la trazabilidad de qué fue generado por IA.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Ticket(Base):
    __tablename__ = "tickets"

    # --- Identidad ---
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_ticket_id = Column(Integer, index=True, nullable=False)

    # --- Campos originales (normalizados) ---
    customer_name = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    customer_age = Column(Integer, nullable=True)
    customer_gender = Column(String, nullable=True)
    product_purchased = Column(String, nullable=True, index=True)
    date_of_purchase = Column(DateTime, nullable=True)
    ticket_type = Column(String, nullable=True, index=True)
    ticket_subject = Column(String, nullable=True)
    ticket_description = Column(Text, nullable=True)
    ticket_status = Column(String, nullable=True, index=True)
    ticket_priority = Column(String, nullable=True, index=True)
    ticket_channel = Column(String, nullable=True)
    first_response_time = Column(DateTime, nullable=True)
    time_to_resolution = Column(DateTime, nullable=True)
    customer_satisfaction_rating = Column(Float, nullable=True)

    # --- Enriquecimiento IA ---
    ai_category = Column(String, nullable=True, index=True)
    ai_priority = Column(String, nullable=True, index=True)
    ai_summary = Column(Text, nullable=True)
    ai_sentiment = Column(String, nullable=True)
    ai_urgency = Column(String, nullable=True)
    ai_assigned_team = Column(String, nullable=True, index=True)
    ai_provider_used = Column(String, nullable=True)

    # --- Calidad de datos (trazabilidad de la limpieza) ---
    data_quality_notes = Column(Text, nullable=True)  # JSON serializado (lista de strings)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class ImportRun(Base):
    """Registro de cada corrida de importación, para trazabilidad."""

    __tablename__ = "import_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_rows = Column(Integer)
    imported_rows = Column(Integer)
    duplicate_rows = Column(Integer)
    enrichment_errors = Column(Integer)
    llm_provider_used = Column(String)
    created_at = Column(DateTime, default=utcnow)
