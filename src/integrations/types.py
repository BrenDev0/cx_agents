from typing import Protocol

class ConversationClient(Protocol):
    async def send_message(
        self,
        channel: str,
        contact_id: str,
        message: str
    ):
        ...


class AppointmentsBookingClient(Protocol):
    async def check_for_existing_appointment(
        self,
        contact_id: str
    ):
        ...

    async def get_slots(
        self,
        calendar_id: str,
        start_date: int,
        end_date: int,
        timezone: str
    ):
        ...

    async def check_availability(
        self,
        calendar_id: str,
        start_time: str,
        timezone: str
    ) -> bool:
        ...

    async def book(
        self,
        calendar_id: str,
        contact_id: str,
        start_time: str,
        title: str | None = None
    ):
        ...

    async def update_appointment(
        self,
        appointment_id: str,
        calendar_id: str,
        start_time: str
    ):
        ...

    async def cancel_appointment(
        self,
        appointment_id: str
    ):
        ...
