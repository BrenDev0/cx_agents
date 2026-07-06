from src.types import ChatMessage
from .models import ChatContext
from .state import ChatState
from .intents import build_available_intents
from .celery.tasks import invoke_chat_workflow


async def handle_chat(
    channel: str,
    contact_id: str,
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
        available_intents=build_available_intents(has_appointments=chat_context.has_calendar, has_rag=chat_context.has_rag)
    )

    task = invoke_chat_workflow.delay(state)

    return {
        "status": "Accepted",
        "task_id": task.id
    }
