from fastapi import APIRouter

from .schemas import ChatRequest, ChatState, ChatTaskPayload, LLMConfig
from .intents import build_available_intents
from .celery.tasks import invoke_chat_workflow

router = APIRouter(
    tags=["Chats"]
)


@router.post("", status_code=202)
async def chat(
    data: ChatRequest
):
    
    state = ChatState(
        contact_id=data.contact_id,
        incoming_message=data.incoming_message,
        chat_history=data.chat_history,
        available_intents=build_available_intents(has_appointments=data.activate_appointments, has_rag=data.activate_rag)
    )

    task_payload = ChatTaskPayload(
        state=state,
        llm=LLMConfig(
            llm_provider=data.llm_provider,
            llm_model=data.llm_model,
            api_key=data.api_key
        )
    )

    task = invoke_chat_workflow.delay(task_payload)

    return {
        "status": "Accepted",
        "task_id": task.id 
    }

    

