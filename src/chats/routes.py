from fastapi import APIRouter, Depends
from .schemas import ChatRequest
from .dependencies import should_reply
from .usecases import handle_chat

router = APIRouter(
    tags=["Chats"]
)


@router.post("/{location_id}", status_code=202)
async def chat(
    location_id: str,
    data: ChatRequest,
    ok_to_reply: bool = Depends(should_reply)
):
    if ok_to_reply:
        return await handle_chat(
            data_in=data,
            location_id=location_id
        )
    
    return {
        "status": "Rejected"
    }

    

