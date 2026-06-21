from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.ticket_repository import TicketRepository
from app.schemas.dashboard import AskRequest, AskResponse
from app.services.ask_service import AskService
from app.services.knowledge_base import get_knowledge_base
from app.services.providers.factory import get_llm_provider

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, db: Session = Depends(get_db)):
    repo = TicketRepository(db)
    service = AskService(repo=repo, knowledge_base=get_knowledge_base(), llm_provider=get_llm_provider())
    return service.ask(payload.question)
