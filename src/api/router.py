from fastapi import APIRouter
from  src.chats.routes import router as chats_router
from src.auth.routes import router as auth_router
from src.documents.routes import router as documents_router
from src.assistants.routes import router as assistants_router
from src.assistants.assistant_settings.routes import router as assistant_settings_router
router = APIRouter()


router.include_router(auth_router, prefix="/auth")
router.include_router(chats_router, prefix="/chats")
router.include_router(documents_router, prefix="/documents")
router.include_router(assistants_router, prefix="/assistants")
router.include_router(assistant_settings_router, prefix="/assistants")


