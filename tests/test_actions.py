from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.actions import validate_action_choice, normalize_action_offer
from src.models import AGENT_ACTIONS, Action, allowed_actions, build_action_output_model


def test_allowed_actions_returns_all_agent_actions():
    assert allowed_actions("A", 1) == AGENT_ACTIONS
    assert allowed_actions("A", 2) == AGENT_ACTIONS
    assert allowed_actions("B", 1) == AGENT_ACTIONS
    assert AGENT_ACTIONS == frozenset({Action.counter, Action.accept, Action.break_})
    assert Action.demand not in AGENT_ACTIONS


def test_validate_action_choice_rejects_unknown_action():
    errors = validate_action_choice(
        party="B",
        round_number=1,
        action="demand",
        offer=1000000,
        opponent_last_offer=5000000,
    )
    assert errors


def test_build_action_output_model_rejects_invalid_action():
    model = build_action_output_model("B", 1)
    with pytest.raises(ValidationError):
        model(action="demand", offer=1000000)


def test_build_action_output_model_accepts_counter():
    model = build_action_output_model("B", 1)
    result = model(action="counter", offer=500000, reason="Comparable licenses support this amount.")
    assert result.action == "counter"


def test_build_action_output_model_puts_reason_before_action():
    """Schema property order is generation order, so reason must precede the decision."""
    model = build_action_output_model("B", 1)
    properties = list(model.model_json_schema()["properties"])

    assert properties.index("reason") < properties.index("action")
    assert properties.index("reason") < properties.index("offer")


def test_normalize_action_offer_sets_accept_from_opponent():
    assert normalize_action_offer("accept", None, 3500000) == 3500000
    assert normalize_action_offer("accept", 999999, 3500000) == 3500000
    assert normalize_action_offer("break", 1000000, 3500000) is None


def test_parse_action_accepts_string_and_enum():
    assert Action("break") == Action.break_
    assert Action.break_ == "break"
