from langgraph.graph import StateGraph, START, END

from src.rag.schemas import RagState
from src.rag.langgraph.workflows import compile_rag_workflow
from src.llm.langchain.models import get_model

from ..schemas import ChatState, MessageRole, ChatMessage


def chat_workflow():
    graph = StateGraph(ChatState)

    async def get_chat_history_node(state: ChatState):
        pass
    
    async def identify_intent_node(state: ChatState):
        llm = get_model(model=state["llm_model"], provider=state["llm_provider"], api_key=state["api_key"])
        system_prompt = """
        classify the users latest message using the chat history.

        return only ONE label:
        APPOINTMENTS = the user is expressing intest in booking, canceling, or updating an appointment
        QUERY = the user looking for general information about services, products, ect
        FALLBACK = you cannot accuratley classify the intent and need more info

        Do not explain your choice. Return only the label.
        """
        messages = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=system_prompt
            )
        ]

        for msg in state.get("chat_history", []):
            messages.append(msg)

        messages.append(ChatMessage(role=MessageRole.HUMAN, content=state["incomming_message"]))

        try:
            response = await llm.ainvoke(messages)
            content = str(response.content).strip().lower()
            intent = content.split()[0] if content else "fallback"

            if intent not in {"appointments", "query", "fallback"}:
                intent = "fallback"

            return {"intent": intent}

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating llm response")
            return {
                "errors": errors,
                "intent": "error"
            }


    def intent_decision(state: ChatState):
        match state["intent"]:
            case "appointments":
                return "appointments"
            case "query":
                return "rag"
            case "fallback":
                return "fallback"
            case "error":
                return "error"
            case _: 
                return "fallback"


    async def rag_workflow(state: ChatState):
        rag_state = RagState(
            contact_id=state["contact_id"],
            user_input=state["incomming_message"],
            chat_history=state.get("chat_history", [])
        )

        workflow = compile_rag_workflow()

        final_rag_state: RagState = await workflow.ainvoke(rag_state)
        
        final_response = final_rag_state.get("generated_reply")

        if not final_response:
            errors = state.get("errors", [])
            errors.append("RAG workflow did not generate a response")
            return {"errors": errors}
        
        if final_rag_state.get("errors"):
            rag_errors = final_rag_state["errors"]
            state.get("errors", []).append(rag_errors)
        
        return {"final_response": final_rag_state["generated_reply"]}

    async def appointments_workflow(state: ChatState):
        pass

    async def fallback_node(state: ChatState):
        llm = get_model(model=state["llm_model"], provider=state["llm_provider"], api_key=state["api_key"])
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

        for msg in state.get("chat_history", []):
            messages.append(msg)

        messages.append(ChatMessage(role=MessageRole.HUMAN, content=state["incomming_message"]))

        try:
            response = await llm.ainvoke(messages)
            content = str(response.content).strip()

            return {"final_response": content}
            

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating llm response")
            return {
                "errors": errors,
                "intent": "error"
            }

    async def send_response_node(state: ChatState):
        pass

    async def handle_errors_node(state: ChatState):
        pass


    graph.add_node("get_chat_history", get_chat_history_node)
    graph.add_node("identify_intent", identify_intent_node)
    graph.add_node("rag", rag_workflow)
    graph.add_node("appointments", appointments_workflow)
    graph.add_node("fallback", fallback_node)
    graph.add_node("reply", send_response_node)
    graph.add_node("error", handle_errors_node)

    graph.add_edge(START, "get_chat_history")
    graph.add_edge("get_chat_history", "identify_intent")
    graph.add_conditional_edges(
        "identify_intent",
        intent_decision,
        {
            "appointments": "appointments",
            "rag": "rag",
            "fallback": "fallback",
            "error": "error" 
        }
    )
    graph.add_edge("appointments", "reply")
    graph.add_edge("rag", "reply")
    graph.add_edge("fallback", "reply")
    graph.add_edge("reply", END)
    graph.add_edge("error", END)


    return graph.compile()