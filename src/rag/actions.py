from src.types import ChatMessage, MessageRole
from src.llm.types import Agent
from src.vector_store.models import DocumentChunk


async def generate_retrieval_query(
    llm: Agent,
    incoming_message: str,
    chat_history: list[ChatMessage] | None = None
) -> str:
    system_prompt = """
    You generate retrieval queries for a RAG system.

    Given the chat history and the user's latest message, produce one concise search query that will find the most relevant context.

    Rules:
    - Use chat history only to resolve references and follow-up questions.
    - Preserve important names, services, products, policies, dates, locations, IDs, error codes, and quoted text.
    - Remove filler words and conversational phrasing.
    - Do not answer the user.
    - Do not explain your reasoning.
    - Do not add facts not present in the conversation.
    - Return only the query text.
    """

    messages = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content=system_prompt
        )
    ]

    messages.extend(chat_history or [])

    messages.append(ChatMessage(role=MessageRole.HUMAN, content=incoming_message))

    llm.set_temperature(0.0)

    return await llm.invoke(messages)


def format_retrieved_context(chunks: list[DocumentChunk]) -> str:
    if not chunks:
        return ""

    return "\n\n".join(chunk.content for chunk in chunks)


def build_rag_prompt(
    incoming_message: str,
    retrieved_context: str
) -> str:
    if not retrieved_context:
        return incoming_message

    return (
        "Use the following retrieved context to answer the user's message. "
        "If the context does not contain the answer, say you don't know rather than guessing.\n\n"
        f"CONTEXT\n{retrieved_context}\n\n"
        f"USER MESSAGE\n{incoming_message}"
    )


async def generate_rag_reply(
    llm: Agent,
    prompt: str,
    chat_history: list[ChatMessage] | None = None,
    generated_context: str | None = None,
    generated_instructions: str | None = None
) -> str:
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

    messages.append(ChatMessage(role=MessageRole.HUMAN, content=prompt))

    llm.set_temperature(0.3)

    return await llm.invoke(messages)
