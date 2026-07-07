from typing_extensions import NotRequired

from src.states import BaseState, AgentHandoffState


class AppointmentsState(BaseState, AgentHandoffState):
    action: NotRequired[str]
    requested_date: NotRequired[str | None]
    selected_slot: NotRequired[str | None]
    collected_fields: NotRequired[dict[str, str]]
    missing_required_fields: NotRequired[list[str]]
    existing_appointment_id: NotRequired[str | None]
    offered_slots: NotRequired[list[str]]
    generated_reply: NotRequired[str]
