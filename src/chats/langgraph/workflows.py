from langgraph.graph import StateGraph, START, END

from src.rag.schemas import RagState
from src.rag.langgraph.workflows import compile_rag_workflow

from ..intents import format_intents_for_prompt
from ..schemas import ChatState, MessageRole, ChatMessage


def compile_chat_workflow(llm):
    graph = StateGraph(ChatState)

    async def identify_intent_node(state: ChatState):
        available_intents = state["available_intents"]
        intent_options = format_intents_for_prompt(available_intents)
        system_prompt = f"""
        Classify the user's latest message using the chat history if available.

        Return exactly one of these labels:

        {intent_options}

        Do not explain your choice.
        Return only the label.
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
            response = await llm.ainvoke(messages)
            content = str(response.content).strip().lower()
            intent = content.split()[0] if content else "fallback"

            if intent not in available_intents:
                intent = "fallback"

            return {"identified_intent": intent}

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

        workflow = compile_rag_workflow(llm)

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
        messages = []

        for msg in state.get("chat_history", []):
            messages.append(msg)

        messages.append(ChatMessage(role=MessageRole.HUMAN, content=state["incoming_message"]))

        try:
            response = await llm.ainvoke(messages)
            content = str(response.content).strip()

            return {"final_response": content}
            

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating plain LLM response")
            return {
                "errors": errors,
                "identified_intent": "error"
            }

    async def fallback_node(state: ChatState):
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

        messages.append(ChatMessage(role=MessageRole.HUMAN, content=state["incoming_message"]))

        try:
            response = await llm.ainvoke(messages)
            content = str(response.content).strip()

            return {"final_response": content}
            

        except Exception:
            errors = state.get("errors", [])
            errors.append("Error generating fallback response")
            return {
                "errors": errors,
                "identified_intent": "error"
            }

    async def send_response_node(state: ChatState):
        return {}

    async def handle_errors_node(state: ChatState):
        return {}


    graph.add_node("identify_intent", identify_intent_node)
    graph.add_node("rag", rag_workflow)
    graph.add_node("appointments", appointments_workflow)
    graph.add_node("plain_llm", plain_llm_node)
    graph.add_node("fallback", fallback_node)
    graph.add_node("reply", send_response_node)
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
    graph.add_edge("reply", END)
    graph.add_edge("error", END)


    return graph.compile()
