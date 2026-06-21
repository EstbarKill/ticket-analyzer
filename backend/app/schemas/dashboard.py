from pydantic import BaseModel


class ProductCount(BaseModel):
    product: str
    count: int


class DashboardSummary(BaseModel):
    total_tickets: int
    critical_or_high_tickets: int
    open_tickets: int
    pending_tickets: int
    closed_tickets: int
    avg_satisfaction_rating: float | None
    avg_resolution_hours: float | None
    by_priority: dict[str, int]
    by_category: dict[str, int]
    by_team: dict[str, int]
    by_sentiment: dict[str, int]
    top_products: list[ProductCount]


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    supporting_tickets: list[int]
    supporting_documents: list[str]
