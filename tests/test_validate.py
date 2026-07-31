from __future__ import annotations

from src.models import Negotiation
from src.nodes.validate import validate_move


def _base_state(**overrides):
    negotiation = Negotiation(
        case_id="TEST",
        party_a="A",
        party_b="B",
        turns=[],
    )
    state = {
        "party": "A",
        "negotiation": negotiation,
        "round_number": 2,
        "opponent_last_offer": 500000,
        "action": "counter",
        "offer": 1000000,
        "reason": "We counter based on comparable licenses and remaining gap.",
        "message": "We counter at $1,000,000.",
        "validation_errors": [],
        "retry_count": 0,
    }
    state.update(overrides)
    return state


def test_counter_requires_positive_offer():
    result = validate_move(_base_state(offer=0))
    assert result["validation_errors"]


def test_agent_move_requires_reason():
    result = validate_move(_base_state(reason=None, message="Drafted message."))
    assert any("Reason is required" in err for err in result["validation_errors"])


def test_accept_normalizes_to_opponent_offer():
    result = validate_move(
        _base_state(
            party="B",
            round_number=2,
            action="accept",
            offer=999999,
            opponent_last_offer=2000000,
            reason="Accepting Summit's last offer; further negotiation is not worthwhile.",
            message="We accept.",
        )
    )
    assert result["validation_errors"] == []
    assert result["offer"] == 2000000


def test_accept_without_opponent_offer_fails():
    result = validate_move(
        _base_state(
            action="accept",
            offer=None,
            opponent_last_offer=None,
            reason="Accepting.",
            message="We accept.",
        )
    )
    assert any("opponent offer" in err.lower() for err in result["validation_errors"])


def test_valid_accept_passes():
    result = validate_move(
        _base_state(
            party="B",
            round_number=2,
            action="accept",
            offer=None,
            opponent_last_offer=2000000,
            reason="Accepting Summit's last offer; litigation is not justified.",
            message="We accept.",
        )
    )
    assert result["validation_errors"] == []
    assert result["offer"] == 2000000
