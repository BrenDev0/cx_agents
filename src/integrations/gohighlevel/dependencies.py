from fastapi import Request, HTTPException, Depends
from httpx import AsyncClient
import logging

from .client import GoHighLevelClient
from ..protocols import ConversationClient

logger = logging.getLogger(__name__)

def get_ghl_http(
    request: Request
) -> AsyncClient:
    http = getattr(request.app.state, "ghl_http", None)

    if not http:
        logger.error("No GHL http client configured in app")
        raise HTTPException(status_code=500, detail="Unable to process request at this time")
    

def get_ghl_client(
    http: AsyncClient = Depends(get_ghl_http)
):
    return GoHighLevelClient(
        http=http
    )
    

def get_ghl_conversations_client(
    client: GoHighLevelClient = Depends(get_ghl_http)
) -> ConversationClient:
    
    return client.conversations
    