from __future__ import annotations

from typing import Literal

from langgraph.graph import END, StateGraph

from src.graphs.party_move import build_party_move_graph
from src.models import NegotiationState, needs_party_a_demand_publish, needs_start_round_one, next_round_number
from src.nodes.persist import (
    build_party_move_input,
    finalize_negotiation,
    has_pending_party_b,
    load_negotiation,
    party_a_terminated,
    party_b_terminated,
    party_move_to_model,
    persist_party_a,
    persist_party_b,
    publish_party_a_opening_demand,
    should_continue,
    start_round_one,
)

_party_agent_graphs = {
    "A": build_party_move_graph(),
    "B": build_party_move_graph(),
}


def run_party_a(state: NegotiationState) -> dict:
    round_number = next_round_number(state["negotiation"])
    if round_number == 1:
        raise RuntimeError(
            "Round 1 Party A opening offer is LLM-generated; message text comes from party_a.opening_demand.json."
        )

    move_state = _party_agent_graphs["A"].invoke(build_party_move_input(state, "A"))
    party_move = party_move_to_model(move_state)
    updates = persist_party_a(state, party_move)
    return {**updates, "last_party_move": party_move}


def run_party_b(state: NegotiationState) -> dict:
    move_state = _party_agent_graphs["B"].invoke(build_party_move_input(state, "B"))
    party_move = party_move_to_model(move_state)
    updates = persist_party_b(state, party_move)
    return {**updates, "last_party_move": party_move}


def route_after_load(
    state: NegotiationState,
) -> Literal["start_round_one", "publish_opening_demand", "run_party_a", "run_party_b", "__end__"]:
    if not should_continue(state):
        return "__end__"
    negotiation = state["negotiation"]
    if needs_start_round_one(negotiation):
        return "start_round_one"
    if needs_party_a_demand_publish(negotiation):
        return "publish_opening_demand"
    if has_pending_party_b(state):
        return "run_party_b"
    return "run_party_a"


def route_after_start_round_one(
    state: NegotiationState,
) -> Literal["publish_opening_demand"]:
    return "publish_opening_demand"


def route_after_publish_opening(
    state: NegotiationState,
) -> Literal["run_party_b"]:
    return "run_party_b"


def route_after_party_a(state: NegotiationState) -> Literal["finalize_negotiation", "run_party_b"]:
    if party_a_terminated(state):
        return "finalize_negotiation"
    return "run_party_b"


def route_after_party_b(state: NegotiationState) -> Literal["finalize_negotiation", "run_party_a", "__end__"]:
    if party_b_terminated(state):
        return "finalize_negotiation"
    if should_continue(state):
        return "run_party_a"
    return "__end__"


def build_negotiation_graph():
    graph = StateGraph(NegotiationState)

    graph.add_node("load_negotiation", load_negotiation)
    graph.add_node("start_round_one", start_round_one)
    graph.add_node("publish_opening_demand", publish_party_a_opening_demand)
    graph.add_node("run_party_a", run_party_a)
    graph.add_node("run_party_b", run_party_b)
    graph.add_node("finalize_negotiation", finalize_negotiation)

    graph.set_entry_point("load_negotiation")
    graph.add_conditional_edges("load_negotiation", route_after_load, {
        "start_round_one": "start_round_one",
        "publish_opening_demand": "publish_opening_demand",
        "run_party_a": "run_party_a",
        "run_party_b": "run_party_b",
        "__end__": END,
    })
    graph.add_conditional_edges("start_round_one", route_after_start_round_one, {
        "publish_opening_demand": "publish_opening_demand",
    })
    graph.add_edge("publish_opening_demand", "run_party_b")
    graph.add_conditional_edges("run_party_a", route_after_party_a, {
        "finalize_negotiation": "finalize_negotiation",
        "run_party_b": "run_party_b",
    })
    graph.add_conditional_edges("run_party_b", route_after_party_b, {
        "finalize_negotiation": "finalize_negotiation",
        "run_party_a": "run_party_a",
        "__end__": END,
    })
    graph.add_edge("finalize_negotiation", END)

    return graph.compile()
