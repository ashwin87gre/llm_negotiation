from __future__ import annotations

import json

from src.context import (
    build_user_context,
    format_negotiation_history,
    format_negotiation_party_roles_line,
    public_negotiation_payload,
)
from src.models import Action, Negotiation, PartyMove, Round


def test_party_roles_line_substitutes_company_names():
    negotiation = Negotiation(
        case_id="TEST",
        party_a="Summit VI LLC",
        party_b="Samsung Electronics Co., Ltd.",
    )
    line = format_negotiation_party_roles_line(negotiation)
    assert "party_a is Summit VI LLC (patent holder)" in line
    assert "party_b is Samsung Electronics Co., Ltd. (licensee)" in line
    assert "{{party_" not in line


def test_public_negotiation_payload_omits_reason():
    negotiation = Negotiation(
        case_id="TEST",
        party_a="Summit VI LLC",
        party_b="Samsung Electronics Co., Ltd.",
        turns=[
            Round(
                round=1,
                party_a=PartyMove(
                    action=Action.demand,
                    offer=5_000_000,
                    reason="secret",
                    message="Opening demand.",
                ),
                party_b=PartyMove(
                    action=Action.counter,
                    offer=1_000_000,
                    reason="also secret",
                    message="Counter letter.",
                ),
            )
        ],
    )
    payload = public_negotiation_payload(negotiation)
    move_b = payload["turns"][0]["party_b"]
    assert "reason" not in move_b
    assert move_b["offer"] == 1_000_000
    assert "secret" not in json.dumps(payload)


def test_format_negotiation_history_is_json_with_roles_preamble():
    negotiation = Negotiation(
        case_id="TEST",
        party_a="Summit VI LLC",
        party_b="Samsung Electronics Co., Ltd.",
        turns=[],
    )
    text = format_negotiation_history(negotiation)
    assert text.startswith("In this negotiation, JSON key party_a is Summit VI LLC")
    assert "Public negotiation (JSON" in text
    assert '"turns": []' in text
    assert "Reason:" not in text


def test_format_negotiation_history_omits_past_reason():
    negotiation = Negotiation(
        case_id="TEST",
        party_a="Summit VI LLC",
        party_b="Samsung Electronics Co., Ltd.",
        turns=[
            Round(
                round=1,
                party_b=PartyMove(
                    action=Action.counter,
                    offer=1_000_000,
                    reason="Internal strategy note.",
                    message="We counter at one million.",
                ),
            )
        ],
    )
    text = format_negotiation_history(negotiation)
    assert '"offer": 1000000' in text
    assert "We counter at one million." in text
    assert "Reason:" not in text
    assert "Internal strategy note." not in text


def test_build_user_context_keeps_current_turn_reason_block():
    negotiation = Negotiation(
        case_id="TEST",
        party_a="Summit VI LLC",
        party_b="Samsung Electronics Co., Ltd.",
        turns=[],
    )
    text = build_user_context(
        party="B",
        negotiation=negotiation,
        round_number=1,
        opponent_last_offer=5_000_000,
        reason="Internal rationale for this move.",
    )
    assert "Decision rationale (from action step" in text
    assert "Internal rationale for this move." in text
    assert "JSON key party_b is Samsung Electronics Co., Ltd." in text
    assert "Case facts (briefing materials for your side):" not in text
    assert "You are representing" not in text
