import logging
from fastapi import Request, HTTPException

from .protocols import CacheStore

logger = logging.getLogger(__name__)

def get_cache_store(request:  Request) -> CacheStore:
    store = getattr(request.app.state, "cache_store", None) 

    if not store:
        logger.error("No cache store configured in app")
        raise HTTPException(status_code=500, detail="Unable to process request at this time")
    
    return store