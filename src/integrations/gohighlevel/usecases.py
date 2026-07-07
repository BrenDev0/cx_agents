from src.types import ChatMessage
from ...chats.models import ChatContext
from ...chats.state import ChatState
from ...chats.intents import build_available_intents
from .celery.tasks import invoke_chat_workflow


async def handle_chat(
    channel: str,
    contact_id: str,
    location_id: str,
    incoming_message: str,
    chat_context: ChatContext,
    chat_history: list[ChatMessage]
):
    state = ChatState(
        assistant_id=str(chat_context.assistant_id),
        contact_id=contact_id,
        channel=channel,
        credential=chat_context.credential,
        incoming_message=incoming_message,
        chat_history=chat_history,
        available_intents=build_available_intents(has_appointments=chat_context.has_calendar, has_rag=chat_context.has_rag),
        calendar_id=chat_context.calendar_id,
        timezone=chat_context.timezone,
        required_fields=chat_context.required_fields,
        title_template=chat_context.title_template
    )

    task = invoke_chat_workflow.delay(state, location_id=location_id)

    return {
        "status": "Accepted",
        "task_id": task.id
    }
