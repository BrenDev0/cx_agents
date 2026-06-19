from fastapi import APIRouter, Depends, Body
import json
from .schemas import ChatRequest, ChatState, ChatMessage, MessageRole
from .intents import build_available_intents
from .celery.tasks import invoke_chat_workflow
from .dependencies import should_reply

router = APIRouter(
    tags=["Chats"]
)


@router.post("", status_code=202)
async def chat(
    data: ChatRequest,
    ok_to_reply: bool = Depends(should_reply)
):
    print(data)
    print(f"ok to reply?{ok_to_reply}")
    
    if ok_to_reply:
        formated_chat_history = []
        for message in data.chat_history:
            formated_chat_history.append(ChatMessage(
                    role=MessageRole.AI if message["direction"] == "outbound" else MessageRole.HUMAN,
                    content=message["body"]
                ) 
            )
        
        state = ChatState(
            contact_id=data.contact_id,
            pit=data.pit,
            incoming_message=data.incoming_message,
            chat_history=formated_chat_history,
            available_intents=build_available_intents(has_appointments=data.activate_appointments, has_rag=data.activate_rag)
        )

        print(state)
        print(f"should reply:::{ok_to_reply}")


        task = invoke_chat_workflow.delay(state)

        return {
            "status": "Accepted",
            "task_id": task.id
        }
    
    return {
        "status": "Rejected"
    }

    

