from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.case_facts import case_facts_path
from src.models import Negotiation
from src.party_instructions import load_party_instructions, party_instructions_path
from src.nodes.persist import build_initial_evaluation_input, build_party_move_input


def _write_party_files(negotiation_path: Path, party: str, instructions: str, facts: str) -> None:
    party_instructions_path(str(negotiation_path), party).write_text(instructions, encoding="utf-8")
    case_facts_path(str(negotiation_path), party).write_text(facts, encoding="utf-8")


def test_party_instructions_path():
    path = party_instructions_path("/data/negotiation_new.json", "A")
    assert path.name == "negotiation_new.party_a.instructions.txt"


def test_load_party_instructions_substitutes_party_names():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation = Negotiation(
            case_id="TEST",
            party_a="Summit VI LLC",
            party_b="Samsung Electronics Co., Ltd.",
        )
        negotiation_path.write_text("{}", encoding="utf-8")
        instructions_path = party_instructions_path(str(negotiation_path), "B")
        instructions_path.write_text(
            "Represent {{party_b}} against {{party_a}}.",
            encoding="utf-8",
        )

        text = load_party_instructions(str(negotiation_path), "B", negotiation)
        assert text == "Represent Samsung Electronics Co., Ltd. against Summit VI LLC."


def test_load_party_instructions_missing_file_raises():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation_path.write_text("{}", encoding="utf-8")
        negotiation = Negotiation(case_id="TEST", party_a="A", party_b="B")

        with pytest.raises(FileNotFoundError, match="Agent instructions file not found"):
            load_party_instructions(str(negotiation_path), "A", negotiation)


def test_build_party_move_input_includes_instructions_and_case_facts():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation = Negotiation(case_id="TEST", party_a="A", party_b="B", turns=[])
        negotiation_path.write_text("{}", encoding="utf-8")
        _write_party_files(
            negotiation_path,
            "B",
            "Party B instructions.",
            "Party B case facts.",
        )

        move_input = build_party_move_input(
            {"negotiation": negotiation, "file_path": str(negotiation_path)},
            "B",
        )

        assert move_input["agent_instructions"] == "Party B instructions."
        assert move_input["case_facts"] == "Party B case facts."
        assert "private_state" not in move_input
        assert "evaluation_mode" not in move_input


def test_build_initial_evaluation_input_loads_same_files():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation = Negotiation(case_id="TEST", party_a="A", party_b="B", turns=[])
        negotiation_path.write_text("{}", encoding="utf-8")
        _write_party_files(
            negotiation_path,
            "A",
            "Party A instructions.",
            "Party A case facts.",
        )

        move_input = build_initial_evaluation_input(
            {"negotiation": negotiation, "file_path": str(negotiation_path)},
            "A",
        )

        assert move_input["party"] == "A"
        assert move_input["agent_instructions"] == "Party A instructions."
        assert move_input["case_facts"] == "Party A case facts."
