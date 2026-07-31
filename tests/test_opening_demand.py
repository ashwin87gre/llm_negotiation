from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.models import Action, Negotiation, PartyMove, Round
from src.nodes.persist import load_negotiation_file, save_negotiation_file, start_round_one


def _sample_negotiation(*, turns: list[Round] | None = None) -> Negotiation:
    return Negotiation(
        case_id="TEST",
        party_a="Patent Holder",
        party_b="Accused Infringer",
        turns=turns or [],
    )


def test_start_round_one_creates_empty_round_without_party_a():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "negotiation.json"
        negotiation = _sample_negotiation()
        save_negotiation_file(str(path), negotiation)

        result = start_round_one({"file_path": str(path), "negotiation": negotiation})
        saved = load_negotiation_file(str(path))

        assert len(saved.turns) == 1
        assert saved.turns[0].round == 1
        assert saved.turns[0].party_a is None
        assert saved.turns[0].party_b is None
        assert result["current_round"] == saved.turns[0]


def test_start_round_one_rejects_when_rounds_exist():
    negotiation = _sample_negotiation(
        turns=[
            Round(
                round=1,
                party_b=PartyMove(
                    action="counter",
                    offer=500000,
                    message="We counter.",
                ),
            )
        ]
    )

    with pytest.raises(ValueError, match="only be started when no rounds exist"):
        start_round_one({"file_path": "unused.json", "negotiation": negotiation})
