from src.integrations.protocols import ConversationClient

from src.types import MessageRole, ChatMessage
from .schemas import ChatRequest
from .state import ChatState
from .intents import build_available_intents
from .celery.tasks import invoke_chat_workflow


async def handle_chat(
    data_in: ChatRequest,
    location_id: str
):
    formatted_chat_history = []
    for message in data_in.chat_history:
        formatted_chat_history.append(ChatMessage(
                role=MessageRole.AI if message["direction"] == "outbound" else MessageRole.HUMAN,
                content=message["body"]
            ) 
        )
    
    state = ChatState(
        contact_id=data_in.contact_id,
        channel=data_in.channel,
        incoming_message=data_in.incoming_message,
        chat_history=formatted_chat_history,
        available_intents=build_available_intents(has_appointments=data_in.activate_appointments, has_rag=data_in.activate_rag)
    )

    task = invoke_chat_workflow.delay(state, location_id)

    return {
        "status": "Accepted",
        "task_id": task.id
    }