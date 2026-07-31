from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.models import (
    Action,
    Negotiation,
    PartyMove,
    PartyPrivateState,
    PrivateStateUpdate,
    Round,
)
from src.nodes.evaluate import evaluate_case


def _llm_update() -> PrivateStateUpdate:
    return PrivateStateUpdate(
        reservation_price=2000000,
        case_strength=0.75,
        opponent_argument_risk=0.3,
        litigation_cost_estimate=1000000,
        evaluation_summary="Test summary.",
        round_assessment="Test round assessment.",
    )


def _base_state(**overrides):
    negotiation = Negotiation(
        case_id="TEST",
        party_a="Patent Holder",
        party_b="Accused Infringer",
        turns=[
            Round(
                round=1,
                party_a=PartyMove(
                    action=Action.demand,
                    offer=5000000,
                    message="Opening demand.",
                ),
            )
        ],
    )
    state = {
        "party": "A",
        "negotiation": negotiation,
        "round_number": 1,
        "opponent_last_offer": None,
        "private_state": None,
        "agent_instructions": "Party A instructions.",
        "case_facts": "Party A case facts.",
        "evaluation_mode": "initial",
    }
    state.update(overrides)
    return state


def _mock_llm(mock_structured_llm: MagicMock) -> MagicMock:
    mock_runnable = MagicMock()
    mock_structured_llm.return_value = mock_runnable
    mock_runnable.invoke.return_value = _llm_update()
    return mock_runnable


@patch("src.nodes.evaluate.structured_llm")
@patch("src.nodes.evaluate.load_prompt")
def test_evaluate_case_initial_loads_evaluate_initial_prompt(
    mock_load_prompt: MagicMock, mock_structured_llm: MagicMock
):
    mock_load_prompt.return_value = "initial system prompt"
    _mock_llm(mock_structured_llm)

    state = _base_state(
        evaluation_mode="initial",
        agent_instructions="Party A instructions from file.",
        case_facts="Party A case facts from file.",
        private_state=None,
    )
    evaluate_case(state)

    mock_load_prompt.assert_called_once_with("A", "evaluate_initial", state["negotiation"])
    mock_structured_llm.assert_called_once_with(PrivateStateUpdate)


@patch("src.nodes.evaluate.structured_llm")
@patch("src.nodes.evaluate.load_prompt")
def test_evaluate_case_incremental_loads_evaluate_incremental_prompt(
    mock_load_prompt: MagicMock, mock_structured_llm: MagicMock
):
    mock_load_prompt.return_value = "incremental system prompt"
    _mock_llm(mock_structured_llm)

    state = _base_state(
        party="B",
        round_number=2,
        evaluation_mode="incremental",
        agent_instructions="Party B instructions.",
        case_facts="Party B case facts.",
        private_state=PartyPrivateState(
            reservation_price=1500000,
            case_strength=0.45,
            opponent_argument_risk=0.7,
            litigation_cost_estimate=900000,
            evaluation_summary="Prior memo.",
            last_updated_round=1,
        ),
    )
    evaluate_case(state)

    mock_load_prompt.assert_called_once_with("B", "evaluate_incremental", state["negotiation"])


@patch("src.nodes.evaluate.structured_llm")
@patch("src.nodes.evaluate.load_prompt")
def test_evaluate_case_initial_rejects_missing_instructions(
    mock_load_prompt: MagicMock, mock_structured_llm: MagicMock
):
    with pytest.raises(ValueError, match="Initial evaluation requires agent instructions"):
        evaluate_case(
            _base_state(
                evaluation_mode="initial",
                agent_instructions=None,
                private_state=None,
            )
        )

    mock_load_prompt.assert_not_called()
    mock_structured_llm.assert_not_called()


@patch("src.nodes.evaluate.structured_llm")
@patch("src.nodes.evaluate.load_prompt")
def test_evaluate_case_initial_rejects_missing_case_facts(
    mock_load_prompt: MagicMock, mock_structured_llm: MagicMock
):
    with pytest.raises(ValueError, match="Initial evaluation requires case facts"):
        evaluate_case(
            _base_state(
                evaluation_mode="initial",
                case_facts=None,
                private_state=None,
            )
        )

    mock_load_prompt.assert_not_called()
    mock_structured_llm.assert_not_called()


@patch("src.nodes.evaluate.structured_llm")
@patch("src.nodes.evaluate.load_prompt")
def test_evaluate_case_incremental_rejects_missing_private_state(
    mock_load_prompt: MagicMock, mock_structured_llm: MagicMock
):
    with pytest.raises(ValueError, match="Incremental evaluation requires existing private state"):
        evaluate_case(
            _base_state(
                round_number=2,
                evaluation_mode="incremental",
                agent_instructions="instructions",
                private_state=None,
            )
        )

    mock_load_prompt.assert_not_called()
    mock_structured_llm.assert_not_called()
