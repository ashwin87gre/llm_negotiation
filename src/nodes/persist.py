from __future__ import annotations

import json
from pathlib import Path

from src.context import negotiation_to_json
from src.actions import validate_action_choice
from src.case_facts import load_case_facts
from src.party_instructions import load_party_instructions
from src.opening_demand_file import load_opening_demand_file
from src.private_state import private_state_path, save_private_state
from src.models import (
    Action,
    Negotiation,
    NegotiationState,
    Party,
    PartyMove,
    Round,
    is_terminal_action,
    needs_party_a_demand_publish,
    needs_start_round_one,
    next_round_number,
    opponent_offer_for_party,
)


def load_negotiation_file(path: str) -> Negotiation:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Negotiation.model_validate(data)


def save_negotiation_file(path: str, negotiation: Negotiation) -> None:
    Path(path).write_text(negotiation_to_json(negotiation) + "\n", encoding="utf-8")


def load_negotiation(state: NegotiationState) -> dict:
    path = state["file_path"]
    negotiation = load_negotiation_file(path)
    current_round = _in_progress_round(negotiation)
    return {
        "negotiation": negotiation,
        "current_round": current_round,
        "done": negotiation.status != "in_progress",
    }


def _in_progress_round(negotiation: Negotiation) -> Round | None:
    if not negotiation.turns:
        return None
    last = negotiation.turns[-1]
    if last.party_b is None:
        return last
    return None


def _build_base_move_input(state: NegotiationState, party: Party) -> dict:
    negotiation = state["negotiation"]
    current_round = state.get("current_round")
    round_number = next_round_number(negotiation)
    opponent_last_offer = opponent_offer_for_party(negotiation, party, current_round)
    negotiation_file_path = state["file_path"]

    return {
        "party": party,
        "negotiation": negotiation,
        "negotiation_file_path": negotiation_file_path,
        "agent_instructions": load_party_instructions(
            negotiation_file_path, party, negotiation
        ),
        "case_facts": load_case_facts(negotiation_file_path, party, negotiation),
        "round_number": round_number,
        "opponent_last_offer": opponent_last_offer,
        "action": None,
        "offer": None,
        "reason": None,
        "message": None,
        "validation_errors": [],
        "retry_count": 0,
    }


def build_party_move_input(state: NegotiationState, party: str) -> dict:
    return _build_base_move_input(state, party)


def build_initial_evaluation_input(state: NegotiationState, party: str) -> dict:
    """Legacy helper for evaluate-only graph; not used in the main negotiation flow."""
    return _build_base_move_input(state, party)


def publish_party_a_opening_demand(state: NegotiationState) -> dict:
    negotiation = state["negotiation"]
    current_round = state.get("current_round")
    if current_round is None:
        raise ValueError("No in-progress round for Party A demand publish.")
    if not needs_party_a_demand_publish(negotiation):
        raise ValueError("Party A demand can only be published once for round 1.")

    demand = load_opening_demand_file(state["file_path"])
    current_round.party_a = PartyMove(
        action=Action.demand,
        offer=demand.offer,
        reason=demand.reason,
        message=demand.message,
    )
    negotiation.turns[-1] = current_round
    save_negotiation_file(state["file_path"], negotiation)
    return {"negotiation": negotiation, "current_round": current_round}


def needs_party_a_initial_evaluation(state: NegotiationState) -> bool:
    path = private_state_path(state["file_path"], "A")
    return not path.exists()


def save_agent_private_state(move_state: dict) -> None:
    """Persist private state when present (evaluate-only path). No-op otherwise."""
    private_state = move_state.get("private_state")
    private_state_path_str = move_state.get("private_state_path")
    if private_state is None or not private_state_path_str:
        return
    save_private_state(Path(private_state_path_str), private_state)


def party_move_to_model(state: dict) -> PartyMove:
    return PartyMove(
        action=state["action"],
        offer=state.get("offer"),
        reason=state.get("reason"),
        message=state["message"],
    )


def _assert_valid_party_move(
    party_move: PartyMove,
    *,
    party: str,
    round_number: int,
    opponent_last_offer: int | None,
) -> None:
    errors = validate_action_choice(
        party=party,
        round_number=round_number,
        action=party_move.action,
        offer=party_move.offer,
        opponent_last_offer=opponent_last_offer,
        message=party_move.message,
        reason=party_move.reason,
        require_reason=True,
    )
    if errors:
        raise ValueError("; ".join(errors))


def start_round_one(state: NegotiationState) -> dict:
    negotiation = state["negotiation"]
    if not needs_start_round_one(negotiation):
        raise ValueError("Round 1 can only be started when no rounds exist yet.")

    current_round = Round(round=1, party_a=None, party_b=None)
    negotiation.turns.append(current_round)
    save_negotiation_file(state["file_path"], negotiation)

    return {
        "negotiation": negotiation,
        "current_round": current_round,
    }


def persist_party_a(state: NegotiationState, party_move: PartyMove) -> dict:
    negotiation = state["negotiation"]
    round_number = next_round_number(negotiation)
    if round_number == 1:
        raise ValueError(
            "Round 1 Party A opening is published programmatically with action 'demand', "
            "not persisted as an agent move."
        )

    _assert_valid_party_move(
        party_move,
        party="A",
        round_number=round_number,
        opponent_last_offer=opponent_offer_for_party(negotiation, "A", None),
    )
    current_round = Round(round=round_number, party_a=party_move)
    negotiation.turns.append(current_round)

    save_negotiation_file(state["file_path"], negotiation)

    return {
        "negotiation": negotiation,
        "current_round": current_round,
        "last_party_move": party_move,
    }


def persist_party_b(state: NegotiationState, party_move: PartyMove) -> dict:
    negotiation = state["negotiation"]
    current_round = state.get("current_round")
    if current_round is None:
        raise ValueError("No in-progress round for Party B move")

    _assert_valid_party_move(
        party_move,
        party="B",
        round_number=current_round.round,
        opponent_last_offer=opponent_offer_for_party(negotiation, "B", current_round),
    )

    current_round.party_b = party_move
    negotiation.turns[-1] = current_round

    save_negotiation_file(state["file_path"], negotiation)

    return {
        "negotiation": negotiation,
        "current_round": current_round,
        "last_party_move": party_move,
    }


def finalize_negotiation(state: NegotiationState) -> dict:
    negotiation = state["negotiation"]
    last_move = state.get("last_party_move")
    if last_move is None:
        raise ValueError("No last party move to finalize")

    if last_move.action == Action.accept:
        negotiation.settlement_value = last_move.offer or -1
        negotiation.status = "agreed"
    elif last_move.action == Action.break_:
        negotiation.settlement_value = -1
        negotiation.status = "breakdown"
    else:
        raise ValueError(f"Cannot finalize on action: {last_move.action}")

    save_negotiation_file(state["file_path"], negotiation)
    return {"negotiation": negotiation, "done": True}


def should_continue(state: NegotiationState) -> bool:
    if state.get("done"):
        return False
    negotiation = state["negotiation"]
    if negotiation.status != "in_progress":
        return False
    max_rounds = state.get("max_rounds")
    if max_rounds is not None and negotiation.turns:
        completed = sum(1 for t in negotiation.turns if t.party_b is not None)
        if completed >= max_rounds:
            return False
    return True


def has_pending_party_b(state: NegotiationState) -> bool:
    current_round = state.get("current_round")
    return current_round is not None and current_round.party_b is None


def party_a_terminated(state: NegotiationState) -> bool:
    move = state.get("last_party_move")
    return move is not None and is_terminal_action(move.action)


def party_b_terminated(state: NegotiationState) -> bool:
    move = state.get("last_party_move")
    return move is not None and is_terminal_action(move.action)
