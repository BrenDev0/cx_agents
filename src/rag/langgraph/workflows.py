from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph

from ..schemas import RagState


def compile_rag_workflow() -> CompiledStateGraph:
    graph = StateGraph(RagState)

    async def generate_query_node(state: RagState):
        pass

    async def embed_query_node(state: RagState):
        pass

    async def search_for_context_node(state: RagState):
        pass 

    async def build_prompt_node(state: RagState):
        pass

    async def generate_response_node(state: RagState):
        pass
    

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