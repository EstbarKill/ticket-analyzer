from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.repositories.ticket_repository import TicketRepository
from app.schemas.tickets import ImportResponse, TicketListResponse, TicketOut
from app.services.enrichment_service import IngestionService
from app.services.providers.factory import get_llm_provider

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.delete("")
def delete_all_tickets(db: Session = Depends(get_db)):
    repo = TicketRepository(db)
    repo.clear_all()
    return {"deleted": True}

@router.post("/import", response_model=ImportResponse)
def import_tickets(db: Session = Depends(get_db)):
    settings = get_settings()
    service = IngestionService(db=db, llm_provider=get_llm_provider())
    try:
        result = service.import_from_csv(settings.dataset_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return result


@router.get("", response_model=TicketListResponse)
def list_tickets(
    category: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    status: str | None = Query(default=None),
    team: str | None = Query(default=None),
    product: str | None = Query(default=None),
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    repo = TicketRepository(db)
    items, total = repo.list_tickets(
        category=category, priority=priority, status=status,
        team=team, product=product, limit=limit, offset=offset,
    )
    return TicketListResponse(
        items=[TicketOut.model_validate(t) for t in items],
        total=total, limit=limit, offset=offset,
    )


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    repo = TicketRepository(db)
    ticket = repo.get_by_id(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    return TicketOut.model_validate(ticket)
