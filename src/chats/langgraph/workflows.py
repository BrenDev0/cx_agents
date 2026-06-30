import logging
from langgraph.graph import StateGraph, START, END

from src.rag.state import RagState
from src.rag.langgraph.workflows import compile_rag_workflow
from src.integrations.types import ConversationClient
from src.cache.types import CacheStore
from src.llm.types import Agent
from src.embeddings.types import EmbeddingService

from ..state import ChatState
from ..actions import (
    identify_intent, 
    generate_fallback_reply, 
    generate_plain_llm_reply, 
    send_reply,
    cache_outgoing_message_id
)

logger = logging.getLogger(__name__)

def compile_chat_workflow(
    llm: Agent, 
    cache_store: CacheStore, 
    conversation_client: ConversationClient,
    embedding_service: EmbeddingService
):
    graph = StateGraph(ChatState)

    async def identify_intent_node(state: ChatState):
        try:
            intent_response = await identify_intent(
                llm=llm, 
                available_intents=state["available_intents"],
                incoming_message=state["incoming_message"],
                chat_history=state.get("chat_history", [])
            )
            return {
                "identified_intent": intent_response.intent,
                "next_agent_instructions": intent_response.instructions,
                "next_agent_context": intent_response.context
            }
        
        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating intent response")
            return {
                "errors": errors,
                "identified_intent": "error"
            }


    def intent_decision(state: ChatState):
        intent = state.get("identified_intent", "fallback")

        if intent == "error":
            return "error"

        if intent not in state["available_intents"]:
            return "fallback"

        return intent


    async def rag_workflow(state: ChatState):
        rag_state = RagState(
            contact_id=state["contact_id"],
            incoming_message=state["incoming_message"],
            chat_history=state.get("chat_history", [])
        )

        workflow = compile_rag_workflow(llm=llm, embedding_service=embedding_service)

        final_rag_state = await workflow.ainvoke(rag_state)
        
        final_response = final_rag_state.get("generated_reply")

        if not final_response:
            errors = state.get("errors", [])
            errors.append("RAG workflow did not generate a response")
            return {"errors": errors}
        
        if final_rag_state.get("errors"):
            errors = state.get("errors", [])
            errors.extend(final_rag_state["errors"])
            return {
                "errors": errors,
                "final_response": final_response,
            }
        
        return {"final_response": final_rag_state["generated_reply"]}


    async def appointments_workflow(state: ChatState):
        return {}


    async def plain_llm_node(state: ChatState):
        try:
            content = await generate_plain_llm_reply(
                llm=llm,
                incoming_message=state["incoming_message"],
                chat_history=state.get("chat_history", []),
                generated_context=state.get("next_agent_context", None),
                generated_instructions=state.get("next_agent_instructions", None)
            )

            return {"final_response": content}
            

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating plain LLM response")
            return {
                "errors": errors,
                "identified_intent": "error"
            }


    async def fallback_node(state: ChatState):
        try:
            content = await generate_fallback_reply( 
                llm=llm,
                incoming_message=state["incoming_message"],
                chat_history=state.get("chat_history", []),
                generated_context=state.get("next_agent_context", None),
                generated_instructions=state.get("next_agent_instructions", None)
            )

            return {"final_response": content}
            
        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating fallback response")
            return {
                "errors": errors,
                "identified_intent": "error"
            }


    async def send_response_node(state: ChatState):
        try:
            message_id = await send_reply(
                channel=state["channel"],
                contact_id=state["contact_id"],
                message=state["final_response"],
                conversation_client=conversation_client
            )

            return {"outgoing_message_id": message_id}
        
        except Exception as e:
            logger.error(e)
            return {"outgoing_message_id": "error"}


    async def cache_outgoing_message_id_node(state: ChatState):
        try:
            if state["outgoing_message_id"] != "error":
                await cache_outgoing_message_id(
                    contact_id=state["contact_id"],
                    outgoing_message_id=state["outgoing_message_id"],
                    channel=state["channel"],
                    cache_store=cache_store
                )

            return {}
        
        except Exception: 
            logger.error("Error caching message id")
            return {}

    async def handle_errors_node(state: ChatState):
        return {}


    graph.add_node("identify_intent", identify_intent_node)
    graph.add_node("rag", rag_workflow)
    graph.add_node("appointments", appointments_workflow)
    graph.add_node("plain_llm", plain_llm_node)
    graph.add_node("fallback", fallback_node)
    graph.add_node("reply", send_response_node)
    graph.add_node("cache_outgoing_message_id", cache_outgoing_message_id_node)
    graph.add_node("error", handle_errors_node)

    graph.add_edge(START, "identify_intent")
    graph.add_conditional_edges(
        "identify_intent",
        intent_decision,
        {
            "appointments": "appointments",
            "rag": "rag",
            "plain_llm": "plain_llm",
            "fallback": "fallback",
            "error": "error" 
        }
    )
    graph.add_edge("appointments", "reply")
    graph.add_edge("rag", "reply")
    graph.add_edge("plain_llm", "reply")
    graph.add_edge("fallback", "reply")
    graph.add_edge("reply", "cache_outgoing_message_id")
    graph.add_edge("cache_outgoing_message_id", END)
    graph.add_edge("error", END)


    return graph.compile()