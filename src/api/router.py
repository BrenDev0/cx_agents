from fastapi import APIRouter
from  src.chats.routes import router as chats_router
router = APIRouter()

router.include_router(chats_router, prefix="/chats")


