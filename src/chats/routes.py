from fastapi import APIRouter
from celery import chain

from .schemas import ChatRequest, ChatState, ChatTaskPayload
from .intents import build_available_intents
from .celery.tasks import invoke_chat_workflow, should_reply

router = APIRouter(
    tags=["Chats"]
)


@router.post("", status_code=202)
async def chat(
    data: ChatRequest
):
    
    state = ChatState(
        contact_id=data.contact_id,
        pit=data.pit,
        incoming_message=data.incoming_message,
        chat_history=data.chat_history,
        available_intents=build_available_intents(has_appointments=data.activate_appointments, has_rag=data.activate_rag)
    )

    job_payload = ChatTaskPayload(
        state=state,
        should_reply=True
    )

    job = chain(
        should_reply.s(job_payload),
        invoke_chat_workflow.s()
    ).apply_async()

    return {
        "status": "Accepted",
        "task_id": job.id 
    }

    

