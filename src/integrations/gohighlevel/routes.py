from fastapi import APIRouter, Depends
from src.chats.usecases import handle_chat
from src.types import ChatMessage
from src.chats.models import ChatContext
from .schemas import GHLChatRequest
from .dependencies import get_chat_context, get_chat_history

router = APIRouter(
    tags=["GHL"]
)

@router.post("/{webhook_id}")
async def handle_post(
    data: GHLChatRequest,
    chat_context: ChatContext = Depends(get_chat_context),
    chat_history: list[ChatMessage] = Depends(get_chat_history)
):
    
    return await handle_chat(
        channel=data.channel,
        contact_id=data.contact_id,
        incoming_message=data.incoming_message,
        chat_context=chat_context,
        chat_history=chat_history
    )