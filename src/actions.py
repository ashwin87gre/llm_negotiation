from __future__ import annotations

from src.models import Action, Party, allowed_actions, parse_action


def normalize_action_offer(
    action: Action | str | None,
    offer: int | None,
    opponent_last_offer: int | None,
) -> int | None:
    """Set settlement amount from game state when action implies it (accept/break)."""
    if action is None:
        return offer
    parsed = parse_action(action)
    if parsed == Action.accept:
        return opponent_last_offer
    if parsed == Action.break_:
        return None
    return offer


def validate_action_choice(
    *,
    party: Party,
    round_number: int,
    action: Action | str | None,
    offer: int | None,
    opponent_last_offer: int | None,
    message: str | None = None,
    reason: str | None = None,
    require_reason: bool = False,
) -> list[str]:
    errors: list[str] = []

    if action is None:
        errors.append("Action is required.")
        return errors

    try:
        parsed_action = parse_action(action)
    except ValueError:
        permitted = allowed_actions(party, round_number)
        allowed_desc = ", ".join(sorted(action.value for action in permitted))
        errors.append(
            f"Action '{action}' is not allowed for Party {party} in round {round_number}. "
            f"Allowed actions: {allowed_desc}."
        )
        return errors

    permitted = allowed_actions(party, round_number)
    if parsed_action not in permitted:
        allowed_desc = ", ".join(sorted(action.value for action in permitted))
        errors.append(
            f"Action '{parsed_action.value}' is not allowed for Party {party} in round {round_number}. "
            f"Allowed actions: {allowed_desc}."
        )

    if parsed_action == Action.counter:
        if offer is None or not isinstance(offer, int) or offer <= 0:
            errors.append("Counter action requires a positive integer offer in whole USD dollars.")

    if parsed_action == Action.accept:
        if opponent_last_offer is None:
            errors.append("Accept requires an opponent offer, but none is available.")
        elif offer is None:
            errors.append("Accept requires a settlement amount from the opponent's last offer.")
        elif offer != opponent_last_offer:
            errors.append(
                f"Accept settlement amount must equal opponent's last offer ({opponent_last_offer}), got {offer}."
            )

    if parsed_action == Action.demand:
        if offer is None or not isinstance(offer, int) or offer <= 0:
            errors.append("Demand action requires a positive integer offer in whole USD dollars.")

    if message is not None and not message.strip():
        errors.append("Message is required.")

    if require_reason and (reason is None or not reason.strip()):
        errors.append("Reason is required.")

    return errors
