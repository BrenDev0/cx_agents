from fastapi import APIRouter, Depends

from src.messaging.credentials.models import MessagingChannel

from .models import ChatContext
from .schemas import ChatRequest
from .dependencies import get_chat_context, should_reply
from .usecases import handle_chat

router = APIRouter(
    tags=["Chats"]
)


@router.post("/{webhook_id}/{channel}", status_code=202)
async def chat(
    channel: MessagingChannel,
    data: ChatRequest,
    chat_context: ChatContext = Depends(get_chat_context),
    ok_to_reply: bool = Depends(should_reply)
):
    if ok_to_reply:
        return await handle_chat(
            data_in=data,
            channel=channel,
            chat_context=chat_context
        )

    return {
        "status": "Rejected"
    }
