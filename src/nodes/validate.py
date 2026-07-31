from __future__ import annotations

from typing import Literal

from src.actions import normalize_action_offer, validate_action_choice
from src.models import PartyMoveState

MAX_RETRIES = 3


def validate_move(state: PartyMoveState) -> dict:
    party = state["party"]
    round_number = state["round_number"]
    action = state.get("action")
    opponent_last_offer = state.get("opponent_last_offer")
    offer = normalize_action_offer(action, state.get("offer"), opponent_last_offer)
    retry_count = state.get("retry_count", 0)
    message = state.get("message")
    reason = state.get("reason")

    errors = validate_action_choice(
        party=party,
        round_number=round_number,
        action=action,
        offer=offer,
        opponent_last_offer=opponent_last_offer,
        message=message,
        reason=reason,
        require_reason=True,
    )

    if errors:
        if retry_count >= MAX_RETRIES:
            raise ValueError(
                f"Validation failed after {MAX_RETRIES} retries: {'; '.join(errors)}"
            )
        return {
            "validation_errors": errors,
            "retry_count": retry_count + 1,
            "reason": None,
            "message": None,
        }

    return {"validation_errors": [], "retry_count": retry_count, "offer": offer}


def route_after_validate(state: PartyMoveState) -> Literal["choose_action", "__end__"]:
    if state.get("validation_errors"):
        return "choose_action"
    return "__end__"
