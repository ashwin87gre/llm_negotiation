from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.models import PartyMoveState
from src.nodes.choose_action import choose_action
from src.nodes.validate import route_after_validate, validate_move
from src.nodes.write_message import write_message


def build_party_move_graph():
    graph = StateGraph(PartyMoveState)

    graph.add_node("choose_action", choose_action)
    graph.add_node("write_message", write_message)
    graph.add_node("validate_move", validate_move)

    graph.set_entry_point("choose_action")
    graph.add_edge("choose_action", "write_message")
    graph.add_edge("write_message", "validate_move")
    graph.add_conditional_edges("validate_move", route_after_validate, {
        "choose_action": "choose_action",
        "__end__": END,
    })

    return graph.compile()
