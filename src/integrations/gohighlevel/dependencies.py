import json
from fastapi import Request, HTTPException, Depends
from httpx import AsyncClient
import logging

from src.cryptography.dependencies import get_cryptography_service
from src.cryptography.types import CryptographyService
from src.credentials.sqlalchemy.dependencies import get_agent_credential
from src.credentials.models import Credential

from .client import GoHighLevelClient
from ..types import ConversationClient

logger = logging.getLogger(__name__)

def get_ghl_http(
    request: Request
) -> AsyncClient:
    http = getattr(request.app.state, "ghl_http", None)

    if not http:
        logger.error("No GHL http client configured in app")
        raise HTTPException(status_code=500, detail="Unable to process request at this time")
    
    return http

def get_ghl_client(
    http: AsyncClient = Depends(get_ghl_http),
    credential: Credential = Depends(get_agent_credential),
    cryptography_service: CryptographyService = Depends(get_cryptography_service)
):
    payload = json.loads(cryptography_service.decrypt(credential.payload))

    return GoHighLevelClient(
        http=http,
        pit=payload["access_token"]
    )
    

def get_ghl_conversations_client(
    client: GoHighLevelClient = Depends(get_ghl_client)
) -> ConversationClient:
    
    return client.conversations
    