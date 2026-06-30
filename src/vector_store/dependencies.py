import logging
from fastapi import Request, HTTPException

from .types import VectorStore

logger = logging.getLogger(__name__)


def get_vector_store(request: Request) -> VectorStore:
    store = getattr(request.app.state, "vector_store", None)

    if not store:
        logger.error("No vector store configured in app")
        raise HTTPException(status_code=500, detail="Unable to process request at this time")

    return store
