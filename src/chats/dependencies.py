import secrets
from uuid import UUID

from fastapi import Depends, Header

from src.assistants.types import GetAssistantByWebhookIdFn
from src.assistants.sqlalchemy.dependencies import provide_get_assistant_by_webhook_id
from src.assistants.assistant_settings.types import GetAssistantSettingByAssistantIdFn
from src.assistants.assistant_settings.sqlalchemy.dependencies import provide_get_assistant_setting_by_assistant_id
from src.cache.dependencies import get_cache_store
from src.cache.types import CacheStore
from src.cryptography.dependencies import get_cryptography_service
from src.cryptography.types import CryptographyService
from src.exceptions import NotFoundException, UnauthorizedException
from src.messaging.credentials.models import MessagingChannel
from src.messaging.credentials.types import GetMessagingCredentialByAssistantAndChannelFn
from src.messaging.credentials.sqlalchemy.dependencies import provide_get_messaging_credential_by_assistant_and_channel

from .schemas import ChatRequest
from .models import ChatContext
from .mappers import domain_to_cache_dict, cache_dict_to_domain
from .cache_keys import get_chat_context_key, get_blocked_channel_key, get_last_message_id_key


async def get_chat_context(
    webhook_id: UUID,
    channel: MessagingChannel,
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
    cache_key = get_chat_context_key(webhook_id=str(webhook_id), channel=channel)
    cached_context = await cache_store.get_json(cache_key)

    if cached_context:
        chat_context = cache_dict_to_domain(cached_context)
    else:
        assistant = await get_assistant_by_webhook_id(webhook_id=webhook_id)

        if not assistant:
            raise UnauthorizedException

        credential = await get_credential_by_assistant_and_channel(
            assistant_id=assistant.id,
            channel=channel
        )

        if not credential:
            raise NotFoundException(f"No {channel} credential configured for this assistant")

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


async def is_channel_blocked(
    data: ChatRequest,
    channel: MessagingChannel,
    cache_store: CacheStore = Depends(get_cache_store)
) -> bool:
    key = get_blocked_channel_key(contact_id=data.contact_id, channel=channel)

    return bool(await cache_store.get_bool(key))


async def _block_channel(
    cache_store: CacheStore,
    contact_id: str,
    channel: str,
) -> None:
    key = get_blocked_channel_key(contact_id=contact_id, channel=channel)

    await cache_store.store_bool(
        key,
        data=True,
        expire_seconds=3500,
    )


async def should_reply(
    data: ChatRequest,
    channel: MessagingChannel,
    channel_is_blocked: bool = Depends(is_channel_blocked),
    cache_store: CacheStore = Depends(get_cache_store)
):
    if channel_is_blocked:
        return False

    key = get_last_message_id_key(contact_id=data.contact_id, channel=channel)
    last_sent_id = await cache_store.get_str(key)

    if not last_sent_id:
        return True

    outbound_messages = [
        message["id"] for message in data.chat_history if message.get("direction", "") == "outbound"
    ]

    if outbound_messages and str(last_sent_id) == str(outbound_messages[-1]):
        return True

    await _block_channel(
        cache_store=cache_store,
        channel=channel,
        contact_id=data.contact_id
    )

    return False

    

    