from langgraph.graph import START, END, StateGraph
from src.llm.schemas import ChatState
from src.llm.nodes.openai.rag import (
    look_for_context_node,
    generate_reply_node
)


def create_rag_workflow():
    graph = StateGraph(ChatState)

    
    graph.add_node("look_for_context", look_for_context_node)
    graph.add_node("generate_reply", generate_reply_node)

    graph.add_edge(START, "look_for_context")
    graph.add_edge("look_for_context", "generate_reply")
    graph.add_edge("generate_reply", END)

    return graph.compile()