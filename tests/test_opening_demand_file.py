from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.models import Action, Negotiation, OpeningDemand
from src.opening_demand_file import (
    load_opening_demand_file,
    opening_demand_path,
    render_opening_demand_message,
)
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
            json.dumps({"message": "Opening demand of {{offer}}."}),
            encoding="utf-8",
        )

        demand = load_opening_demand_file(str(negotiation_path))
        assert demand == OpeningDemand(message="Opening demand of {{offer}}.")


def test_render_opening_demand_message_substitutes_offer():
    rendered = render_opening_demand_message("Lump sum of {{offer}}.", 29_000_000)
    assert rendered == "Lump sum of $29,000,000."


@patch("src.nodes.persist.generate_opening_offer", return_value=4_200_000)
def test_publish_party_a_opening_demand_writes_demand_move_to_round_one(
    mock_generate_opening_offer,
):
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation = Negotiation(case_id="TEST", party_a="A", party_b="B", turns=[])
        save_negotiation_file(str(negotiation_path), negotiation)
        opening_demand_path(str(negotiation_path)).write_text(
            json.dumps({"message": "Programmatic opening of {{offer}}."}),
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

        mock_generate_opening_offer.assert_called_once()
        party_a = result["negotiation"].turns[0].party_a
        assert party_a is not None
        assert party_a.action == Action.demand
        assert party_a.offer == 4_200_000
        assert party_a.message == "Programmatic opening of $4,200,000."
        assert saved.turns[0].party_a.message == "Programmatic opening of $4,200,000."


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
