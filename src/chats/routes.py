from fastapi import APIRouter, Request, Depends

from .schemas import ChatRequest, ChatState
from .intents import build_available_intents
from .dependencies import get_chat_workflow

router = APIRouter(
    tags=["Chats"]
)


@router.post("", status_code=202)
async def chat(
    request: Request,
    data: ChatRequest,
    workflow = Depends(get_chat_workflow)
):
    
    state = ChatState(
        contact_id=data.contact_id,
        llm_provider=data.llm_provider,
        llm_model=data.llm_model,
        api_key=data.api_key,
        incoming_message=data.incoming_message,
        chat_history=data.chat_history,
        available_intents=build_available_intents(has_appointments=data.activate_appointments, has_rag=data.activate_rag)
    )

    

