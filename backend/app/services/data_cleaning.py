"""
Limpieza y normalización de los datos crudos del CSV.

El dataset viene de una exportación real, así que aquí se concentra todo el
trabajo "feo" de producción: formatos de prioridad/tipo inconsistentes,
fechas en varios formatos (incluido texto en español), emails con espacios o
mayúsculas, y filas duplicadas. Cada fila normalizada lleva una lista de
`notes` con lo que se tuvo que corregir o lo que quedó faltante, para que el
reporte de importación sea transparente en vez de "limpiar en silencio".
"""
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

MONTHS_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}

# Nota sobre prioridades numéricas ("1".."4", "P1".."P4"): se asume la
# convención más común en sistemas de ticketing, donde 1/P1 es la más urgente
# y 4/P4 la menos urgente. Este supuesto queda documentado en el README.
PRIORITY_MAP = {
    "low": "Low", "baja": "Low", "p4": "Low", "4": "Low",
    "medium": "Medium", "med": "Medium", "media": "Medium", "p3": "Medium", "3": "Medium",
    "high": "High", "alta": "High", "p2": "High", "2": "High",
    "critical": "Critical", "urgent": "Critical", "urgente": "Critical",
    "critica": "Critical", "crítica": "Critical", "p1": "Critical", "1": "Critical",
}

VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}

TICKET_TYPE_MAP = {
    "technical issue": "Technical issue", "technical_issue": "Technical issue",
    "billing inquiry": "Billing inquiry", "billing_inquiry": "Billing inquiry",
    "billing": "Billing inquiry",
    "refund request": "Refund request", "refund_request": "Refund request",
    "refund": "Refund request",
    "cancellation request": "Cancellation request", "cancellation_request": "Cancellation request",
    "cancel request": "Cancellation request",
    "product inquiry": "Product inquiry", "product_inquiry": "Product inquiry",
}

VALID_STATUSES = {"Open", "Pending Customer Response", "Closed"}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class CleanedTicket:
    source_ticket_id: Optional[int]
    customer_name: Optional[str]
    customer_email: Optional[str]
    customer_age: Optional[int]
    customer_gender: Optional[str]
    product_purchased: Optional[str]
    date_of_purchase: Optional[datetime]
    ticket_type: Optional[str]
    ticket_subject: Optional[str]
    ticket_description: Optional[str]
    ticket_status: Optional[str]
    ticket_priority: Optional[str]
    ticket_channel: Optional[str]
    first_response_time: Optional[datetime]
    time_to_resolution: Optional[datetime]
    customer_satisfaction_rating: Optional[float]
    notes: list[str] = field(default_factory=list)
    is_duplicate: bool = False


def _clean_str(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_flexible_date(raw: Optional[str]) -> tuple[Optional[datetime], Optional[str]]:
    """Intenta parsear fechas en varios formatos, incluyendo texto en español."""
    raw = _clean_str(raw)
    if not raw:
        return None, None

    # Formatos directos más comunes en el dataset.
    formats = [
        "%Y-%m-%d", "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y", "%d-%m-%Y",
        "%m/%d/%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt), None
        except ValueError:
            continue

    # Formato en español: "19 de diciembre 2020" / "6 de marzo 2021"
    match = re.match(r"^(\d{1,2}) de ([a-záéíóú]+) (\d{4})$", raw.lower())
    if match:
        day, month_name, year = match.groups()
        month = MONTHS_ES.get(month_name)
        if month:
            try:
                return datetime(int(year), month, int(day)), None
            except ValueError:
                pass

    return None, f"fecha con formato no reconocido: '{raw}'"


def normalize_priority(raw: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    raw = _clean_str(raw)
    if not raw:
        return None, "prioridad faltante"
    key = raw.strip().lower()
    mapped = PRIORITY_MAP.get(key)
    if mapped:
        note = None if raw in VALID_PRIORITIES else f"prioridad normalizada desde '{raw}'"
        return mapped, note
    if raw in VALID_PRIORITIES:
        return raw, None
    return None, f"prioridad no reconocida: '{raw}'"


def normalize_ticket_type(raw: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    raw = _clean_str(raw)
    if not raw:
        return None, "tipo de ticket faltante"
    key = raw.strip().lower()
    mapped = TICKET_TYPE_MAP.get(key)
    if mapped:
        note = None if raw == mapped else f"tipo normalizado desde '{raw}'"
        return mapped, note
    return raw, f"tipo de ticket no reconocido, se deja tal cual: '{raw}'"


def normalize_email(raw: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    raw = _clean_str(raw)
    if not raw:
        return None, "email faltante"
    cleaned = raw.strip().lower()
    if not EMAIL_RE.match(cleaned):
        return cleaned, f"email con formato inválido: '{raw}'"
    return cleaned, None


def normalize_status(raw: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    raw = _clean_str(raw)
    if not raw:
        return None, "estado faltante"
    if raw in VALID_STATUSES:
        return raw, None
    for valid in VALID_STATUSES:
        if raw.lower() == valid.lower():
            return valid, f"estado normalizado desde '{raw}'"
    return raw, f"estado no reconocido: '{raw}'"


def normalize_age(raw: Optional[str]) -> tuple[Optional[int], Optional[str]]:
    raw = _clean_str(raw)
    if not raw:
        return None, None
    try:
        age = int(float(raw))
    except ValueError:
        return None, f"edad no numérica: '{raw}'"
    if not (0 < age < 120):
        return None, f"edad fuera de rango razonable: {age}"
    return age, None


def normalize_rating(raw: Optional[str]) -> tuple[Optional[float], Optional[str]]:
    raw = _clean_str(raw)
    if not raw:
        return None, None
    try:
        rating = float(raw)
    except ValueError:
        return None, f"calificación no numérica: '{raw}'"
    if not (1 <= rating <= 5):
        return None, f"calificación fuera de rango (1-5): {rating}"
    return rating, None


def clean_row(row: dict) -> CleanedTicket:
    notes: list[str] = []

    def track(value, note):
        if note:
            notes.append(note)
        return value

    try:
        source_id = int(float(row.get("Ticket ID", "").strip()))
    except (ValueError, AttributeError):
        source_id = None
        notes.append("Ticket ID inválido o faltante")

    priority, note = normalize_priority(row.get("Ticket Priority"))
    track(None, note)
    ticket_type, note = normalize_ticket_type(row.get("Ticket Type"))
    track(None, note)
    email, note = normalize_email(row.get("Customer Email"))
    track(None, note)
    status, note = normalize_status(row.get("Ticket Status"))
    track(None, note)
    age, note = normalize_age(row.get("Customer Age"))
    track(None, note)
    rating, note = normalize_rating(row.get("Customer Satisfaction Rating"))
    track(None, note)

    purchase_date, note = parse_flexible_date(row.get("Date of Purchase"))
    track(None, note)
    first_response, _ = parse_flexible_date(row.get("First Response Time"))
    resolution, _ = parse_flexible_date(row.get("Time to Resolution"))

    return CleanedTicket(
        source_ticket_id=source_id,
        customer_name=_clean_str(row.get("Customer Name")),
        customer_email=email,
        customer_age=age,
        customer_gender=_clean_str(row.get("Customer Gender")),
        product_purchased=_clean_str(row.get("Product Purchased")),
        date_of_purchase=purchase_date,
        ticket_type=ticket_type,
        ticket_subject=_clean_str(row.get("Ticket Subject")),
        ticket_description=_clean_str(row.get("Ticket Description")),
        ticket_status=status,
        ticket_priority=priority,
        ticket_channel=_clean_str(row.get("Ticket Channel")),
        first_response_time=first_response,
        time_to_resolution=resolution,
        customer_satisfaction_rating=rating,
        notes=notes,
    )


def clean_dataset(rows: list[dict]) -> list[CleanedTicket]:
    """Limpia todas las filas y marca duplicados por Ticket ID (se conserva la primera)."""
    cleaned = [clean_row(row) for row in rows]
    seen: set[int] = set()
    for ticket in cleaned:
        if ticket.source_ticket_id is None:
            continue
        if ticket.source_ticket_id in seen:
            ticket.is_duplicate = True
            ticket.notes.append(f"Ticket ID duplicado: {ticket.source_ticket_id}")
        else:
            seen.add(ticket.source_ticket_id)
    return cleaned
