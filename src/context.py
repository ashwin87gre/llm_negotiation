from __future__ import annotations

import json

from src.models import Action, Negotiation, Party, PartyMove, Round
from src.prompts import render_prompt

PARTY_ROLES_LINE_TEMPLATE = (
    "In this negotiation, JSON key party_a is {{party_a}} (patent holder) "
    "and JSON key party_b is {{party_b}} (licensee)."
)


def format_offer(offer: int | None) -> str:
    if offer is None:
        return "none"
    return f"${offer:,}"


def format_negotiation_party_roles_line(negotiation: Negotiation) -> str:
    return render_prompt(
        PARTY_ROLES_LINE_TEMPLATE,
        party_a=negotiation.party_a,
        party_b=negotiation.party_b,
    )


def public_move_for_prompt(move: PartyMove) -> dict:
    """Public move fields for LLM history; excludes internal choose_action reason."""
    action = move.action.value if isinstance(move.action, Action) else move.action
    return {
        "action": action,
        "offer": move.offer,
        "message": move.message,
    }


def public_negotiation_payload(negotiation: Negotiation) -> dict:
    settlement_value = (
        negotiation.settlement_value if negotiation.settlement_value != -1 else None
    )
    turns: list[dict] = []
    for turn in negotiation.turns:
        entry: dict = {"round": turn.round}
        if turn.party_a is not None:
            entry["party_a"] = public_move_for_prompt(turn.party_a)
        if turn.party_b is not None:
            entry["party_b"] = public_move_for_prompt(turn.party_b)
        turns.append(entry)

    return {
        "case_id": negotiation.case_id,
        "party_a": negotiation.party_a,
        "party_b": negotiation.party_b,
        "status": negotiation.status,
        "settlement_value": settlement_value,
        "turns": turns,
    }


def format_negotiation_history(negotiation: Negotiation) -> str:
    roles_line = format_negotiation_party_roles_line(negotiation)
    payload = public_negotiation_payload(negotiation)
    json_block = json.dumps(payload, indent=2)
    return (
        f"{roles_line}\n\n"
        "Public negotiation (JSON; visible to both parties; reason fields omitted):\n"
        f"{json_block}"
    )


def build_user_context(
    *,
    party: Party,
    negotiation: Negotiation,
    round_number: int,
    opponent_last_offer: int | None,
    current_round: Round | None = None,
    action: str | None = None,
    offer: int | None = None,
    reason: str | None = None,
    validation_errors: list[str] | None = None,
) -> str:
    del current_round
    sections: list[str] = []

    if reason:
        sections.extend(
            [
                "Decision rationale (from action step — basis for the public message):",
                reason,
                "",
                "",
            ]
        )

    sections.extend(
        [
            format_negotiation_history(negotiation),
            "",
            f"Current round number: {round_number}",
            f"Opponent's last negotiated offer: {format_offer(opponent_last_offer)}",
        ]
    )

    if party == "B" and round_number == 1:
        sections.append(
            f"Round 1: respond to {negotiation.party_a}'s opening demand shown above."
        )

    if action:
        sections.extend(
            [
                "",
                f"Chosen action: {action}",
                f"Chosen offer: {format_offer(offer)}",
            ]
        )

    if validation_errors:
        sections.extend(
            [
                "",
                "Previous decision was invalid. Fix the action/offer:",
                *[f"- {err}" for err in validation_errors],
            ]
        )

    return "\n".join(sections)


def negotiation_to_json(negotiation: Negotiation) -> str:
    return json.dumps(negotiation.model_dump(), indent=2)
