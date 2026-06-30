import logging
from fastapi import Request, HTTPException

from .types import ObjectStore

logger = logging.getLogger(__name__)


def get_object_store(request: Request) -> ObjectStore:
    store = getattr(request.app.state, "object_store", None)

    if not store:
        logger.error("No object store configured in app")
        raise HTTPException(status_code=500, detail="Unable to process request at this time")

    return store
