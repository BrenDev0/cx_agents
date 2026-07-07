import logging
from datetime import datetime, timedelta, UTC

from langgraph.graph import StateGraph, START, END

from src.integrations.types import AppointmentsBookingClient
from src.cache.types import CacheStore
from src.llm.types import Agent

from ..state import AppointmentsState
from ..cache_keys import get_appointment_session_key
from ..actions import (
    extract_appointment_request,
    render_title,
    format_slots_reply,
    format_missing_fields_reply,
    generate_clarify_reply,
    extract_existing_appointment_id
)

logger = logging.getLogger(__name__)

SLOT_SEARCH_WINDOW_DAYS = 7
SESSION_TTL_SECONDS = 15 * 60


def compile_appointments_workflow(
    llm: Agent,
    appointments_client: AppointmentsBookingClient,
    cache_store: CacheStore,
    calendar_id: str | None,
    timezone: str | None,
    required_fields: list[str] | None,
    title_template: str | None
):
    graph = StateGraph(AppointmentsState)
    resolved_timezone = timezone or "UTC"
    resolved_required_fields = required_fields or []

    def route_entry(state: AppointmentsState):
        return "calendar_not_configured" if not calendar_id else "load_session"

    async def load_session_node(state: AppointmentsState):
        session = await cache_store.get_json(get_appointment_session_key(state["contact_id"])) or {}
        return {
            "offered_slots": session.get("offered_slots", []),
            "collected_fields": session.get("collected_fields", {})
        }

    async def extract_request_node(state: AppointmentsState):
        try:
            extraction = await extract_appointment_request(
                llm=llm,
                incoming_message=state["incoming_message"],
                required_fields=resolved_required_fields,
                offered_slots=state.get("offered_slots", []),
                chat_history=state.get("chat_history", []),
                generated_context=state.get("next_agent_context"),
                generated_instructions=state.get("next_agent_instructions")
            )

            collected_fields = {**state.get("collected_fields", {}), **extraction.collected_fields}
            missing_required_fields = [
                field for field in resolved_required_fields if field not in collected_fields
            ]
            offered_slots = state.get("offered_slots", [])
            selected_slot = extraction.selected_slot if extraction.selected_slot in offered_slots else None

            return {
                "action": extraction.action,
                "requested_date": extraction.requested_date,
                "selected_slot": selected_slot,
                "collected_fields": collected_fields,
                "missing_required_fields": missing_required_fields
            }

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error extracting appointment request")
            return {"errors": errors, "action": "unclear"}

    async def check_existing_appointment_node(state: AppointmentsState):
        try:
            response = await appointments_client.check_for_existing_appointment(contact_id=state["contact_id"])
            return {"existing_appointment_id": extract_existing_appointment_id(response)}

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error checking for existing appointment")
            return {"errors": errors, "existing_appointment_id": None}

    def route_action(state: AppointmentsState):
        action = state.get("action", "unclear")

        if action in ("book", "reschedule") and state.get("missing_required_fields"):
            return "request_missing_fields"

        if action == "cancel":
            return "cancel_appointment" if state.get("existing_appointment_id") else "clarify"

        if action == "reschedule":
            if not state.get("existing_appointment_id"):
                return "clarify"
            return "update_appointment" if state.get("selected_slot") else "get_slots"

        if action == "book":
            return "book_appointment" if state.get("selected_slot") else "get_slots"

        if action == "check_slots":
            return "get_slots"

        return "clarify"

    async def get_slots_node(state: AppointmentsState):
        try:
            requested_date = state.get("requested_date")
            start = datetime.fromisoformat(requested_date) if requested_date else datetime.now(UTC)
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1 if requested_date else SLOT_SEARCH_WINDOW_DAYS)

            response = await appointments_client.get_slots(
                calendar_id=calendar_id,
                start_date=int(start.timestamp() * 1000),
                end_date=int(end.timestamp() * 1000),
                timezone=resolved_timezone
            )

            slots = [
                slot
                for day in response.values() if isinstance(day, dict)
                for slot in day.get("slots", [])
            ]

            await cache_store.store_json(
                key=get_appointment_session_key(state["contact_id"]),
                data={"offered_slots": slots, "collected_fields": state.get("collected_fields", {})},
                expire_seconds=SESSION_TTL_SECONDS
            )

            return {
                "offered_slots": slots,
                "generated_reply": format_slots_reply(slots, resolved_timezone)
            }

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error fetching available slots")
            return {
                "errors": errors,
                "generated_reply": "I wasn't able to check availability just now -- could you try again in a moment?"
            }

    async def book_appointment_node(state: AppointmentsState):
        try:
            await appointments_client.book(
                calendar_id=calendar_id,
                contact_id=state["contact_id"],
                start_time=state["selected_slot"],
                title=render_title(title_template, state.get("collected_fields", {}))
            )

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error booking appointment")
            return {
                "errors": errors,
                "generated_reply": "That time may no longer be available -- would you like to try another slot?"
            }

        await _clear_session(cache_store, state["contact_id"])

        confirmed_time = datetime.fromisoformat(state["selected_slot"]).strftime("%A, %B %d at %I:%M %p")
        return {"generated_reply": f"You're booked for {confirmed_time}. See you then!"}

    async def update_appointment_node(state: AppointmentsState):
        try:
            await appointments_client.update_appointment(
                appointment_id=state["existing_appointment_id"],
                calendar_id=calendar_id,
                start_time=state["selected_slot"]
            )

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error rescheduling appointment")
            return {
                "errors": errors,
                "generated_reply": "I wasn't able to reschedule to that time -- would you like to try another slot?"
            }

        await _clear_session(cache_store, state["contact_id"])

        confirmed_time = datetime.fromisoformat(state["selected_slot"]).strftime("%A, %B %d at %I:%M %p")
        return {"generated_reply": f"You're all set -- rescheduled to {confirmed_time}."}

    async def cancel_appointment_node(state: AppointmentsState):
        try:
            await appointments_client.cancel_appointment(appointment_id=state["existing_appointment_id"])

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error cancelling appointment")
            return {
                "errors": errors,
                "generated_reply": "I wasn't able to cancel that just now -- could you try again in a moment?"
            }

        await _clear_session(cache_store, state["contact_id"])

        return {"generated_reply": "Your appointment has been cancelled."}

    async def request_missing_fields_node(state: AppointmentsState):
        await cache_store.store_json(
            key=get_appointment_session_key(state["contact_id"]),
            data={
                "offered_slots": state.get("offered_slots", []),
                "collected_fields": state.get("collected_fields", {})
            },
            expire_seconds=SESSION_TTL_SECONDS
        )
        return {"generated_reply": format_missing_fields_reply(state.get("missing_required_fields", []))}

    async def clarify_node(state: AppointmentsState):
        action = state.get("action", "unclear")

        if action == "cancel":
            reason = "there's no appointment on file to cancel"
        elif action == "reschedule":
            reason = "there's no existing appointment on file to reschedule"
        else:
            reason = "it's not clear what they'd like to do"

        try:
            reply = await generate_clarify_reply(
                llm=llm,
                incoming_message=state["incoming_message"],
                reason=reason,
                chat_history=state.get("chat_history", []),
                generated_context=state.get("next_agent_context"),
                generated_instructions=state.get("next_agent_instructions")
            )
            return {"generated_reply": reply}

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating appointments clarification")
            return {
                "errors": errors,
                "generated_reply": "Could you tell me a bit more about what you'd like to do with your appointment?"
            }

    async def calendar_not_configured_node(state: AppointmentsState):
        return {
            "generated_reply": "I'm not able to check appointments right now -- someone from our team will follow up with you shortly."
        }

    graph.add_node("load_session", load_session_node)
    graph.add_node("extract_request", extract_request_node)
    graph.add_node("check_existing_appointment", check_existing_appointment_node)
    graph.add_node("get_slots", get_slots_node)
    graph.add_node("book_appointment", book_appointment_node)
    graph.add_node("update_appointment", update_appointment_node)
    graph.add_node("cancel_appointment", cancel_appointment_node)
    graph.add_node("request_missing_fields", request_missing_fields_node)
    graph.add_node("clarify", clarify_node)
    graph.add_node("calendar_not_configured", calendar_not_configured_node)

    graph.add_conditional_edges(
        START,
        route_entry,
        {
            "calendar_not_configured": "calendar_not_configured",
            "load_session": "load_session"
        }
    )
    graph.add_edge("load_session", "extract_request")
    graph.add_edge("extract_request", "check_existing_appointment")
    graph.add_conditional_edges(
        "check_existing_appointment",
        route_action,
        {
            "get_slots": "get_slots",
            "book_appointment": "book_appointment",
            "update_appointment": "update_appointment",
            "cancel_appointment": "cancel_appointment",
            "request_missing_fields": "request_missing_fields",
            "clarify": "clarify"
        }
    )
    graph.add_edge("get_slots", END)
    graph.add_edge("book_appointment", END)
    graph.add_edge("update_appointment", END)
    graph.add_edge("cancel_appointment", END)
    graph.add_edge("request_missing_fields", END)
    graph.add_edge("clarify", END)
    graph.add_edge("calendar_not_configured", END)

    return graph.compile()


async def _clear_session(cache_store: CacheStore, contact_id: str) -> None:
    try:
        await cache_store.remove(get_appointment_session_key(contact_id))
    except Exception:
        logger.warning("Failed to clear appointment session cache for %s", contact_id)
