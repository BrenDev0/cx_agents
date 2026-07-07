from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from src.types import ChatMessage, MessageRole
from src.llm.types import Agent


class AppointmentExtraction(BaseModel):
    action: str = Field(
        description=(
            "What the user wants to do. Must be exactly one of: book, reschedule, cancel, "
            "check_slots, unclear. Use unclear only if none of the others plausibly fit."
        )
    )
    requested_date: str | None = Field(
        description=(
            "A specific date the user asked about, as YYYY-MM-DD, resolved against today if they said "
            "something relative like 'tomorrow' or 'next Tuesday'. Null if no specific date was mentioned."
        )
    )
    selected_slot: str | None = Field(
        description=(
            "If the user is confirming one of the previously offered time slots (given below), the exact "
            "matching ISO timestamp from that list. Null if they haven't picked one of the offered slots."
        )
    )
    collected_fields: dict[str, str] = Field(
        description=(
            "Any of the requested contact fields the user has provided so far, across this message and the "
            "chat history, keyed by field name. Omit fields that were not provided."
        )
    )


def build_extraction_prompt(
    required_fields: list[str],
    offered_slots: list[str]
) -> str:
    required_fields_text = ", ".join(required_fields) if required_fields else "none"
    offered_slots_text = "\n".join(f"- {slot}" for slot in offered_slots) if offered_slots else "(none offered yet)"

    return f"""
    You are handling an appointment-related request for a customer messaging agent.

    Determine what the user wants to do (book, reschedule, cancel, check_slots, or unclear), any specific
    date they mentioned, whether they are confirming one of the previously offered time slots, and any of
    the following contact fields they have provided: {required_fields_text}.

    Previously offered time slots:
    {offered_slots_text}

    Rules:
    - Only set selected_slot to one of the exact timestamps listed above -- never invent one.
    - Use the chat history to resolve follow-ups (e.g. "the second one", "2pm works").
    - Do not answer the user or generate a reply here.
    - collected_fields should only include fields the user actually stated, not guesses.
    """


async def extract_appointment_request(
    llm: Agent,
    incoming_message: str,
    required_fields: list[str],
    offered_slots: list[str],
    chat_history: list[ChatMessage] | None = None,
    generated_context: str | None = None,
    generated_instructions: str | None = None
) -> AppointmentExtraction:
    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content=build_extraction_prompt(required_fields, offered_slots))
    ]

    if generated_instructions:
        messages.append(ChatMessage(
            role=MessageRole.SYSTEM,
            content=f"\nINSTRUCTIONS\n{generated_instructions}"
        ))

    if generated_context:
        messages.append(ChatMessage(
            role=MessageRole.SYSTEM,
            content=f"\nCONVERSATION CONTEXT\n{generated_context}"
        ))

    messages.extend(chat_history or [])

    messages.append(ChatMessage(role=MessageRole.HUMAN, content=incoming_message))

    llm.set_temperature(0.0)

    return await llm.invoke_structured(messages, AppointmentExtraction)


def render_title(template: str | None, fields: dict[str, str]) -> str:
    if not template:
        name = fields.get("name", "").strip()
        return f"Appointment - {name}" if name else "Appointment"

    class _DefaultDict(dict):
        def __missing__(self, key):
            return ""

    return template.format_map(_DefaultDict(fields))


def format_slots_reply(slots: list[str], timezone: str, max_slots: int = 5) -> str:
    if not slots:
        return "I don't see any openings for that day -- would you like to try another day?"

    formatted = []
    for slot in slots[:max_slots]:
        parsed = datetime.fromisoformat(slot)
        formatted.append(parsed.strftime("%A, %B %d at %I:%M %p"))

    options = "\n".join(f"- {option}" for option in formatted)
    return f"Here are some available times ({timezone}):\n{options}\n\nWhich one works for you?"


def format_missing_fields_reply(missing_fields: list[str]) -> str:
    fields_text = " and ".join(missing_fields) if len(missing_fields) <= 2 else ", ".join(missing_fields)
    return f"Sure -- can I get your {fields_text} to continue?"


async def generate_clarify_reply(
    llm: Agent,
    incoming_message: str,
    reason: str,
    chat_history: list[ChatMessage] | None = None,
    generated_context: str | None = None,
    generated_instructions: str | None = None
) -> str:
    system_prompt = f"""
    You are handling an appointment-related request, but it can't be completed as asked: {reason}

    Explain this to the user briefly and, if it makes sense, ask what they'd like to do instead.
    Do not mention internal systems, calendars, appointment IDs, or workflows.
    Keep the response friendly and under 30 words.
    Only respond in the language of the conversation.
    """

    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)
    ]

    if generated_instructions:
        messages.append(ChatMessage(
            role=MessageRole.SYSTEM,
            content=f"\nINSTRUCTIONS\n{generated_instructions}"
        ))

    if generated_context:
        messages.append(ChatMessage(
            role=MessageRole.SYSTEM,
            content=f"\nCONVERSATION CONTEXT\n{generated_context}"
        ))

    messages.extend(chat_history or [])

    messages.append(ChatMessage(role=MessageRole.HUMAN, content=incoming_message))

    llm.set_temperature(0.0)

    return await llm.invoke(messages)


def extract_existing_appointment_id(response: dict) -> str | None:
    events = response.get("events") or response.get("appointments") or []

    if not isinstance(events, list) or not events:
        return None

    active = next(
        (event for event in events if event.get("appointmentStatus") not in ("cancelled", "invalid")),
        events[0]
    )

    return active.get("id")
