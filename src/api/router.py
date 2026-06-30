from fastapi import APIRouter
from  src.chats.routes import router as chats_router
from src.auth.routes import router as auth_router
from src.documents.routes import router as documents_router
router = APIRouter()


router.include_router(auth_router, prefix="/auth")
router.include_router(chats_router, prefix="/chats")
router.include_router(documents_router, prefix="/documents")


