from __future__ import annotations

import tempfile
from pathlib import Path

from src.case_facts import case_facts_path
from src.models import (
    Action,
    Negotiation,
    PartyMove,
    PartyPrivateState,
    PrivateStateUpdate,
    Round,
    format_evaluation_for_action,
)
from src.nodes.persist import build_party_move_input
from src.party_instructions import party_instructions_path
from src.private_state import load_private_state, private_state_path, save_private_state


def test_private_state_path():
    path = private_state_path("/data/case.json", "A")
    assert path.name == "case.party_a.private.json"


def test_save_and_load_private_state():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation_path.write_text("{}", encoding="utf-8")
        path = private_state_path(str(negotiation_path), "B")
        state = PartyPrivateState(
            reservation_price=1500000,
            case_strength=0.4,
            opponent_argument_risk=0.7,
            litigation_cost_estimate=900000,
            evaluation_summary="Defenses are moderate.",
            last_updated_round=1,
        )
        save_private_state(path, state)
        loaded = load_private_state(path)
        assert loaded == state


def test_build_party_move_input_does_not_load_private_state():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation = Negotiation(
            case_id="TEST",
            party_a="A",
            party_b="B",
            turns=[
                Round(
                    round=1,
                    party_a=PartyMove(
                        action=Action.demand,
                        offer=5000000,
                        message="Opening.",
                    ),
                )
            ],
        )
        negotiation_path.write_text("{}", encoding="utf-8")
        party_instructions_path(str(negotiation_path), "B").write_text(
            "Party B instructions.",
            encoding="utf-8",
        )
        case_facts_path(str(negotiation_path), "B").write_text(
            "Party B case facts.",
            encoding="utf-8",
        )
        private_path = private_state_path(str(negotiation_path), "B")
        save_private_state(
            private_path,
            PartyPrivateState(
                reservation_price=1500000,
                case_strength=0.4,
                opponent_argument_risk=0.7,
                litigation_cost_estimate=900000,
                evaluation_summary="Prior memo.",
                last_updated_round=1,
            ),
        )

        move_input = build_party_move_input(
            {"negotiation": negotiation, "file_path": str(negotiation_path)},
            "B",
        )
        assert "private_state" not in move_input


def test_private_state_update_to_private_state():
    update = PrivateStateUpdate(
        reservation_price=2000000,
        case_strength=0.8,
        opponent_argument_risk=0.3,
        litigation_cost_estimate=1000000,
        evaluation_summary="Strong case.",
        round_assessment="Gap remains wide.",
    )
    state = update.to_private_state(2)
    assert state.last_updated_round == 2
    evaluation = format_evaluation_for_action(state, update.round_assessment)
    assert "Gap remains wide." in evaluation
