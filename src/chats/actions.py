from src.integrations.protocols import ConversationClient
from src.cache.protocols import CacheStore
from src.llm.protocols import Agent

from src.types import ChatMessage, MessageRole
from .intents import format_intents_for_prompt, build_intent_classifier_prompt, IntentStructure, IntentDefinition
from .cache_keys import get_last_message_id_key


async def identify_intent(
    llm: Agent,
    available_intents: dict[str, IntentDefinition],
    incoming_message: str,
    chat_history: list[ChatMessage] = None
):
    available_intents = available_intents
    intent_options = format_intents_for_prompt(available_intents)
    system_prompt = build_intent_classifier_prompt(intent_options=intent_options)
    messages = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=system_prompt
        )
    ]

    messages.extend(chat_history or [])

    messages.append(ChatMessage(role=MessageRole.HUMAN, content=incoming_message))

    llm.set_temperature(0.0)

    response = await llm.invoke_structured(messages, IntentStructure)

    intent = response.intent if response.intent else "fallback"

    if intent.lower() not in available_intents:
        intent = "fallback"

    response.intent = intent
    return response


async def generate_plain_llm_reply(
    llm: Agent,
    incoming_message: str,
    chat_history: list[ChatMessage] = None,
    generated_context: str = None,
    generated_instructions: str = None
):
    messages = []
    

    if generated_instructions:
        messages.append(ChatMessage(
            role=MessageRole.SYSTEM,
            content=f"\nINSTRUCTIONS\n{generated_instructions}"
    ))


    if generated_context:
        messages.append(ChatMessage(
            role=MessageRole.SYSTEM,
            content=f"\nCONVERSATION CONTEXT\n{generated_context}"
        ))
        
    messages.extend(chat_history or [])

    messages.append(ChatMessage(role=MessageRole.HUMAN, content=incoming_message))

    llm.set_temperature(0.5)
    response = await llm.invoke(messages)

    return response
    
        
async def generate_fallback_reply(
    llm: Agent,
    incoming_message: str,
    chat_history: list[ChatMessage] = [],
    generated_context: str = None,
    generated_instructions: str = None
):
    system_prompt = """
    The user's intent could not be confidently classified.

    Use the chat history and the user's latest message to ask one concise clarification question.
    Do not answer the user's request yet.
    Do not mention internal labels, routing, classification, agents, or workflows.
    If the message appears related to appointments, ask for the missing appointment detail.
    If the message appears related to general business information, ask what specific service, product, policy, or topic they mean.
    If the message is too vague, ask what they would like help with.

    Keep the response friendly and under 30 words.
    Only respond in the language of the conversation
    """

    messages = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=system_prompt
        )
    ]

    if generated_instructions:
        messages.append(ChatMessage(
            role=MessageRole.SYSTEM,
            content=f"\nINSTRUCTIONS\n{generated_instructions}"
        ))

    if generated_context:
        messages.append(ChatMessage(
            role=MessageRole.SYSTEM,
            content=f"\nCONVERSATION CONTEXT\n{generated_context}"
        ))
        
    messages.extend(chat_history or [])

    messages.append(ChatMessage(role=MessageRole.HUMAN, content=incoming_message))

    llm.set_temperature(0.0)
    response = await llm.invoke(messages)

    return response
        
        
async def send_reply(
    channel: str,
    contact_id: str,
    message: str,
    conversation_client: ConversationClient
):
    message = await conversation_client.send_message(
        channel=channel,
        contact_id=contact_id,
        message=message
    )

    return message["id"]


async def cache_outgoing_message_id(
    contact_id: str,
    outgoing_message_id: str,
    channel: str,
    cache_store: CacheStore
):
    if outgoing_message_id != "error":
        key = get_last_message_id_key(
            contact_id=contact_id,
            channel=channel
        )
        await cache_store.store(key=key, data=outgoing_message_id, expire_seconds=60*60*24)
        
    return {}
    