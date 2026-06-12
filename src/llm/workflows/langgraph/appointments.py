from langgraph.graph import START, END, StateGraph
from src.llm.nodes.gohighlevel.appointments import (
    check_for_existing_appointment_node,
    orchestrator_node,
    gather_info_node,
    get_slots_node,
    check_availability_node,
    book_appointment_node,
    update_appointment_node,
    cancel_appointment_node,
    generate_reply_node
)

def create_appointments_workflow():
    graph = StateGraph()

    

    graph.add_node("check_for_existing_appointment", check_for_existing_appointment_node)
    graph.add_node("orchestrate", orchestrator_node)
    graph.add_node("gather_info", gather_info_node)
    graph.add_node("get_slots", get_slots_node)
    graph.add_node("check_availability", check_availability_node)
    graph.add_node("book_appointment", book_appointment_node)
    graph.add_node("update_appointment", update_appointment_node)
    graph.add_node("cancel_appointment", cancel_appointment_node)
    graph.add_node("generate_reply", generate_reply_node)

    return graph.compile()