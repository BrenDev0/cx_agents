import logging
import secrets
from uuid import UUID
from fastapi import Request, HTTPException, Depends, Header
from httpx import AsyncClient

from src.cache.types import CacheStore
from src.cache.dependencies import get_cache_store
from src.types import ChatMessage
from src.chats.models import ChatContext
from src.assistants.types import GetAssistantByWebhookIdFn
from src.assistants.sqlalchemy.dependencies import provide_get_assistant_by_webhook_id
from src.assistants.assistant_settings.types import GetAssistantSettingByAssistantIdFn
from src.assistants.assistant_settings.sqlalchemy.dependencies import provide_get_assistant_setting_by_assistant_id
from src.chats.cache_keys import get_chat_context_key
from src.cryptography.dependencies import get_cryptography_service
from src.cryptography.encryption import decrypt
from src.cryptography.types import CryptographyService
from src.exceptions import NotFoundException, UnauthorizedException
from src.messaging.credentials.types import GetMessagingCredentialByAssistantAndChannelFn
from src.messaging.credentials.sqlalchemy.dependencies import provide_get_messaging_credential_by_assistant_and_channel
from src.chats.mappers import cache_dict_to_domain, domain_to_cache_dict

from .client import GoHighLevelClient
from .conversations import GHLConversationsClient
from .schemas import GHLChatRequest


logger = logging.getLogger(__name__)


def get_ghl_http(
    request: Request
) -> AsyncClient:
    http = getattr(request.app.state, "ghl_http", None)

    if not http:
        logger.error("No GHL http client configured in app")
        raise HTTPException(status_code=500, detail="Unable to process request at this time")

    return http


def get_ghl_conversations_client(http: AsyncClient, access_token: str) -> GHLConversationsClient:
    return GoHighLevelClient(http=http, pit=access_token).conversations


async def get_chat_context(
    webhook_id: UUID,
    data: GHLChatRequest,
    x_webhook_secret: str = Header(..., alias="X-Webhook-Secret"),
    cache_store: CacheStore = Depends(get_cache_store),
    get_assistant_by_webhook_id: GetAssistantByWebhookIdFn = Depends(provide_get_assistant_by_webhook_id),
    get_credential_by_assistant_and_channel: GetMessagingCredentialByAssistantAndChannelFn = Depends(
        provide_get_messaging_credential_by_assistant_and_channel
    ),
    get_assistant_setting_by_assistant_id: GetAssistantSettingByAssistantIdFn = Depends(
        provide_get_assistant_setting_by_assistant_id
    ),
    cryptography: CryptographyService = Depends(get_cryptography_service)
) -> ChatContext:
    cache_key = get_chat_context_key(webhook_id=str(webhook_id), channel=data.channel)
    cached_context = await cache_store.get_json(cache_key)

    if cached_context:
        chat_context = cache_dict_to_domain(cached_context)
    else:
        assistant = await get_assistant_by_webhook_id(webhook_id=webhook_id)

        if not assistant:
            raise UnauthorizedException

        credential = await get_credential_by_assistant_and_channel(
            assistant_id=assistant.id,
            channel=data.channel
        )

        if not credential:
            raise NotFoundException(f"No {data.channel} credential configured for this assistant")

        assistant_setting = await get_assistant_setting_by_assistant_id(assistant.id)

        if not assistant_setting:
            raise NotFoundException("Assistant setting not found")

        chat_context = ChatContext(
            assistant_id=assistant.id,
            webhook_secret_hash=assistant.webhook_secret_hash,
            credential=credential.credential,
            has_calendar=assistant_setting.has_calendar,
            has_rag=assistant_setting.has_rag
        )

        await cache_store.store_json(
            key=cache_key,
            data=domain_to_cache_dict(chat_context),
            expire_seconds=60 * 5
        )

    if not secrets.compare_digest(cryptography.hash_token(x_webhook_secret), chat_context.webhook_secret_hash):
        raise UnauthorizedException

    return chat_context


async def get_chat_history(
    data: GHLChatRequest,
    chat_context: ChatContext = Depends(get_chat_context),
    ghl_http: AsyncClient = Depends(get_ghl_http)
) -> list[ChatMessage]:
    conversations_client = get_ghl_conversations_client(
        http=ghl_http,
        access_token=decrypt(chat_context.credential)
    )

    return await conversations_client.get_chat_history(
        contact_id=data.contact_id,
        location_id=data.location_id,
        incoming_message=data.incoming_message,
        channel=data.channel
    )

