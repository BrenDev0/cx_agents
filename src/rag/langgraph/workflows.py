from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.types import ChatMessage, MessageRole
from src.embeddings.types import EmbeddingService
from src.llm.types import Agent
from ..state import RagState


def compile_rag_workflow(embedding_service: EmbeddingService, llm: Agent) -> CompiledStateGraph:
    graph = StateGraph(RagState)

    async def generate_query_node(state: RagState, ):
        system_prompt = """
        You generate retrieval queries for a RAG system.

        Given the chat history and the user's latest message, produce one concise search query that will find the most relevant context.

        Rules:
        - Use chat history only to resolve references and follow-up questions.
        - Preserve important names, services, products, policies, dates, locations, IDs, error codes, and quoted text.
        - Remove filler words and conversational phrasing.
        - Do not answer the user.
        - Do not explain your reasoning.s
        - Do not add facts not present in the conversation.
        - Return only the query text.
        """
        messages = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=system_prompt
            )
        ]

        for msg in state.get("chat_history", []):
            messages.append(msg)

        messages.append(ChatMessage(role=MessageRole.HUMAN, content=state["incoming_message"]))

        try:
            response = await llm.invoke(messages)
            return {"generated_query": response}

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating generating query for RAG context lookup")
            return {
                "errors": errors
            }

    async def embed_query_node(state: RagState):
        embeddings = await embedding_service.embed_query(query=state["generated_query"])
        return {"embedded_query": embeddings}

    async def search_for_context_node(state: RagState):
        return {}

    async def build_prompt_node(state: RagState):
        return {}

    async def generate_response_node(state: RagState):
        return {}
    

    graph.add_node("generate_query", generate_query_node)
    graph.add_node("embed_query", embed_query_node)
    graph.add_node("search_for_context", search_for_context_node)
    graph.add_node("build_prompt", build_prompt_node)
    graph.add_node("generate_response", generate_response_node)

    graph.add_edge(START, "generate_query")
    graph.add_edge("generate_query", "embed_query")
    graph.add_edge("embed_query", "search_for_context")
    graph.add_edge("search_for_context", "build_prompt")
    graph.add_edge("build_prompt", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()