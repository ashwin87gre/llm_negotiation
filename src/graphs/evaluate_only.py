from __future__ import annotations

from langgraph.graph import END, StateGraph

from src.models import PartyMoveState
from src.nodes.evaluate import evaluate_case


def build_evaluate_only_graph():
    graph = StateGraph(PartyMoveState)
    graph.add_node("evaluate_case", evaluate_case)
    graph.set_entry_point("evaluate_case")
    graph.add_edge("evaluate_case", END)
    return graph.compile()
