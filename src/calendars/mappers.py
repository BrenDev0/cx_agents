from .models import Calendar
from .schemas import CalendarResponse

def domain_to_public_schema(domain: Calendar) -> CalendarResponse:
    return CalendarResponse.model_validate(domain, from_attributes=True)
