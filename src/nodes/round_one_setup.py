from __future__ import annotations

from src.models import NegotiationState, needs_party_a_demand_publish
from src.nodes.persist import (
    build_initial_evaluation_input,
    build_party_move_input,
    needs_party_a_initial_evaluation,
    publish_party_a_opening_demand,
    save_agent_private_state,
    start_round_one,
)


def run_start_round_one(state: NegotiationState) -> dict:
    return start_round_one(state)


def run_publish_opening_demand(state: NegotiationState) -> dict:
    return publish_party_a_opening_demand(state)


def run_initialize_party_a_evaluation(state: NegotiationState) -> dict:
    from src.graphs.evaluate_only import build_evaluate_only_graph

    graph = build_evaluate_only_graph()
    move_state = graph.invoke(build_initial_evaluation_input(state, "A"))
    save_agent_private_state(move_state)
    return {}


def needs_round_one_setup(state: NegotiationState) -> bool:
    negotiation = state["negotiation"]
    return len(negotiation.turns) == 0 or needs_party_a_demand_publish(negotiation)
