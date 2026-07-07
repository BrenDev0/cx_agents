from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from src.embeddings.types import EmbeddingService
from src.llm.types import Agent
from src.vector_store.types import VectorStore
from ..state import RagState
from ..actions import (
    generate_retrieval_query,
    format_retrieved_context,
    build_rag_prompt,
    generate_rag_reply,
    assess_context_answerability,
    generate_unanswerable_reply
)


def compile_rag_workflow(
    embedding_service: EmbeddingService,
    llm: Agent,
    vector_store: VectorStore
) -> CompiledStateGraph:
    graph = StateGraph(RagState)

    async def generate_query_node(state: RagState):
        try:
            query = await generate_retrieval_query(
                llm=llm,
                incoming_message=state["incoming_message"],
                chat_history=state.get("chat_history", [])
            )
            return {"generated_query": query}

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
        try:
            chunks = await vector_store.query(
                embedding=state["embedded_query"],
                top_k=5,
                filter={"assistant_id": state["assistant_id"]}
            )
            return {"retrieved_context": format_retrieved_context(chunks)}

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error searching for RAG context")
            return {
                "errors": errors,
                "retrieved_context": ""
            }

    async def build_prompt_node(state: RagState):
        prompt = build_rag_prompt(
            incoming_message=state["incoming_message"],
            retrieved_context=state.get("retrieved_context", "")
        )
        return {"prompt": prompt}

    async def assess_answerability_node(state: RagState):
        try:
            assessment = await assess_context_answerability(
                llm=llm,
                incoming_message=state["incoming_message"],
                retrieved_context=state.get("retrieved_context", "")
            )
            return {"answerable": assessment.answerable}

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error assessing retrieved context")
            return {
                "errors": errors,
                "answerable": False
            }

    def answerability_decision(state: RagState):
        return "generate_response" if state.get("answerable", False) else "generate_unanswerable_reply"

    async def generate_response_node(state: RagState):
        try:
            reply = await generate_rag_reply(
                llm=llm,
                prompt=state["prompt"],
                chat_history=state.get("chat_history", []),
                generated_context=state.get("next_agent_context"),
                generated_instructions=state.get("next_agent_instructions")
            )
            return {"generated_reply": reply}

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating RAG response")
            return {
                "errors": errors
            }

    async def generate_unanswerable_reply_node(state: RagState):
        try:
            reply = await generate_unanswerable_reply(
                llm=llm,
                incoming_message=state["incoming_message"],
                chat_history=state.get("chat_history", []),
                generated_context=state.get("next_agent_context"),
                generated_instructions=state.get("next_agent_instructions")
            )
            return {"generated_reply": reply}

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating unanswerable RAG reply")
            return {
                "errors": errors
            }

    graph.add_node("generate_query", generate_query_node)
    graph.add_node("embed_query", embed_query_node)
    graph.add_node("search_for_context", search_for_context_node)
    graph.add_node("build_prompt", build_prompt_node)
    graph.add_node("assess_answerability", assess_answerability_node)
    graph.add_node("generate_response", generate_response_node)
    graph.add_node("generate_unanswerable_reply", generate_unanswerable_reply_node)

    graph.add_edge(START, "generate_query")
    graph.add_edge("generate_query", "embed_query")
    graph.add_edge("embed_query", "search_for_context")
    graph.add_edge("search_for_context", "build_prompt")
    graph.add_edge("build_prompt", "assess_answerability")
    graph.add_conditional_edges(
        "assess_answerability",
        answerability_decision,
        {
            "generate_response": "generate_response",
            "generate_unanswerable_reply": "generate_unanswerable_reply"
        }
    )
    graph.add_edge("generate_response", END)
    graph.add_edge("generate_unanswerable_reply", END)

    return graph.compile()
