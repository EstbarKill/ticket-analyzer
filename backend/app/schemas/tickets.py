from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_ticket_id: int
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_age: Optional[int] = None
    customer_gender: Optional[str] = None
    product_purchased: Optional[str] = None
    date_of_purchase: Optional[datetime] = None
    ticket_type: Optional[str] = None
    ticket_subject: Optional[str] = None
    ticket_description: Optional[str] = None
    ticket_status: Optional[str] = None
    ticket_priority: Optional[str] = None
    ticket_channel: Optional[str] = None
    first_response_time: Optional[datetime] = None
    time_to_resolution: Optional[datetime] = None
    customer_satisfaction_rating: Optional[float] = None
    ai_category: Optional[str] = None
    ai_priority: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_sentiment: Optional[str] = None
    ai_urgency: Optional[str] = None
    ai_assigned_team: Optional[str] = None
    ai_provider_used: Optional[str] = None


class TicketListResponse(BaseModel):
    items: list[TicketOut]
    total: int
    limit: int
    offset: int


class ImportResponse(BaseModel):
    total_rows: int
    imported_rows: int
    duplicate_rows: int
    enrichment_errors: int
    llm_provider_used: str
    import_run_id: int
