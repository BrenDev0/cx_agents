import logging
from fastapi import Request, HTTPException

from .types import EmbeddingService


logger = logging.getLogger(__name__)


def get_embedding_service(
    request: Request
) -> EmbeddingService:
    service = getattr(request.app.state, "embedding_service", None)

    if not service:
        logging.error("No embedding service configured in app")
        raise HTTPException(status_code=500, detail="Unable to process request at this time")
    
    return service