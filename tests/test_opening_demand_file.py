from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.models import Action, Negotiation, OpeningDemand, PartyMove, Round
from src.opening_demand_file import load_opening_demand_file, opening_demand_path
from src.nodes.persist import (
    load_negotiation_file,
    needs_party_a_initial_evaluation,
    publish_party_a_opening_demand,
    save_negotiation_file,
    start_round_one,
)


def test_opening_demand_path():
    path = opening_demand_path("/data/negotiation_new.json")
    assert path.name == "negotiation_new.party_a.opening_demand.json"


def test_load_opening_demand_file():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation_path.write_text("{}", encoding="utf-8")
        demand_path = opening_demand_path(str(negotiation_path))
        demand_path.write_text(
            json.dumps({"offer": 5000000, "message": "Opening demand from file."}),
            encoding="utf-8",
        )

        demand = load_opening_demand_file(str(negotiation_path))
        assert demand == OpeningDemand(offer=5000000, message="Opening demand from file.")


def test_publish_party_a_opening_demand_writes_demand_move_to_round_one():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation = Negotiation(case_id="TEST", party_a="A", party_b="B", turns=[])
        save_negotiation_file(str(negotiation_path), negotiation)
        opening_demand_path(str(negotiation_path)).write_text(
            json.dumps({"offer": 4200000, "message": "Programmatic opening."}),
            encoding="utf-8",
        )

        started = start_round_one({"file_path": str(negotiation_path), "negotiation": negotiation})
        result = publish_party_a_opening_demand(
            {
                "file_path": str(negotiation_path),
                "negotiation": started["negotiation"],
                "current_round": started["current_round"],
            }
        )
        saved = load_negotiation_file(str(negotiation_path))

        party_a = result["negotiation"].turns[0].party_a
        assert party_a is not None
        assert party_a.action == Action.demand
        assert party_a.offer == 4200000
        assert saved.turns[0].party_a.message == "Programmatic opening."


def test_needs_party_a_initial_evaluation():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation_path.write_text("{}", encoding="utf-8")
        state = {"file_path": str(negotiation_path)}

        assert needs_party_a_initial_evaluation(state) is True

        private_path = Path(tmp) / "negotiation.party_a.private.json"
        private_path.write_text("{}", encoding="utf-8")

        assert needs_party_a_initial_evaluation(state) is False


def test_load_opening_demand_file_missing_raises():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation_path.write_text("{}", encoding="utf-8")

        with pytest.raises(FileNotFoundError, match="opening demand file not found"):
            load_opening_demand_file(str(negotiation_path))
