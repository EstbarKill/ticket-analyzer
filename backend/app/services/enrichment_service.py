"""
Orquesta el pipeline completo de importación:
CSV -> validación/limpieza -> enriquecimiento IA -> persistencia.
"""
import csv
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.repositories.ticket_repository import TicketRepository
from app.services.data_cleaning import clean_dataset
from app.services.providers.base import LLMProvider

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, db: Session, llm_provider: LLMProvider):
        self._repo = TicketRepository(db)
        self._llm = llm_provider

    def import_from_csv(self, csv_path: str) -> dict:
        rows = self._read_csv(csv_path)
        cleaned = clean_dataset(rows)

        self._repo.clear_all()

        imported = 0
        enrichment_errors = 0
        orm_tickets = []

        for ticket in cleaned:
            if ticket.is_duplicate or ticket.source_ticket_id is None:
                continue
            try:
                enrichment = self._llm.enrich_ticket(
                    subject=ticket.ticket_subject or "",
                    description=ticket.ticket_description or "",
                    ticket_type=ticket.ticket_type or "",
                    original_priority=ticket.ticket_priority,
                )
            except Exception as exc:  # noqa: BLE001 - el enriquecimiento nunca debe tumbar la importación
                logger.warning("Error enriqueciendo ticket %s: %s", ticket.source_ticket_id, exc)
                enrichment_errors += 1
                enrichment = {
                    "ai_category": ticket.ticket_type or "Product inquiry",
                    "ai_priority": ticket.ticket_priority or "Medium",
                    "ai_summary": "No se pudo generar el resumen.",
                    "ai_sentiment": "Neutral",
                    "ai_urgency": "Media",
                    "ai_assigned_team": "Soporte Técnico",
                }
            orm_tickets.append(self._repo.to_orm(ticket, enrichment, provider_name=self._llm.name))
            imported += 1

        self._repo.bulk_create(orm_tickets)

        duplicates = sum(1 for t in cleaned if t.is_duplicate)
        run = self._repo.create_import_run(
            total_rows=len(rows),
            imported_rows=imported,
            duplicate_rows=duplicates,
            enrichment_errors=enrichment_errors,
            llm_provider_used=self._llm.name,
        )

        return {
            "total_rows": len(rows),
            "imported_rows": imported,
            "duplicate_rows": duplicates,
            "enrichment_errors": enrichment_errors,
            "llm_provider_used": self._llm.name,
            "import_run_id": run.id,
        }

    @staticmethod
    def _read_csv(csv_path: str) -> list[dict]:
        path = Path(csv_path)
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el archivo de tickets en {csv_path}")
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)
