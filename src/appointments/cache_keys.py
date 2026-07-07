from enum import StrEnum

class AppointmentsCacheKey(StrEnum):
    SESSION = "appointments:session"


def get_appointment_session_key(contact_id: str) -> str:
    return f"{contact_id}:{AppointmentsCacheKey.SESSION}"
