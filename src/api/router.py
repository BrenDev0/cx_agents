from fastapi import APIRouter
from src.auth.routes import router as auth_router
from src.documents.routes import router as documents_router
from src.assistants.routes import router as assistants_router
from src.assistants.assistant_settings.routes import router as assistant_settings_router
from src.knowledge_base.routes import router as knowledge_base_router
from src.messaging.credentials.routes import router as messaging_credentials_router
from src.integrations.gohighlevel.routes import router as ghl_router
router = APIRouter()


router.include_router(auth_router, prefix="/auth")
router.include_router(documents_router, prefix="/documents")
router.include_router(assistants_router, prefix="/assistants")
router.include_router(assistant_settings_router, prefix="/assistants")
router.include_router(knowledge_base_router, prefix="/knowledge-base")
router.include_router(messaging_credentials_router, prefix="/messaging/credentials")

router.include_router(ghl_router, prefix="/ghl")


