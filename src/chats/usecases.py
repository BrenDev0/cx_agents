from src.types import MessageRole, ChatMessage
from src.messaging.credentials.models import MessagingChannel
from .models import ChatContext
from .schemas import ChatRequest
from .state import ChatState
from .intents import build_available_intents
from .celery.tasks import invoke_chat_workflow


async def handle_chat(
    data_in: ChatRequest,
    channel: MessagingChannel,
    chat_context: ChatContext
):
    formatted_chat_history = []
    for message in data_in.chat_history:
        formatted_chat_history.append(ChatMessage(
                role=MessageRole.AI if message["direction"] == "outbound" else MessageRole.HUMAN,
                content=message["body"]
            )
        )

    state = ChatState(
        assistant_id=str(chat_context.assistant_id),
        contact_id=data_in.contact_id,
        channel=channel,
        credential=chat_context.credential,
        incoming_message=data_in.incoming_message,
        chat_history=formatted_chat_history,
        available_intents=build_available_intents(has_appointments=chat_context.has_calendar, has_rag=chat_context.has_rag)
    )

    task = invoke_chat_workflow.delay(state)

    return {
        "status": "Accepted",
        "task_id": task.id
    }
