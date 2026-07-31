from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.case_facts import case_facts_path, load_case_facts
from src.models import Negotiation


def test_case_facts_path():
    path = case_facts_path("/data/negotiation_new.json", "A")
    assert path.name == "negotiation_new.party_a.case_facts.txt"


def test_load_case_facts_reads_party_file():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation = Negotiation(
            case_id="TEST",
            party_a="Summit VI LLC",
            party_b="Samsung Electronics Co., Ltd.",
        )
        negotiation_path.write_text("{}", encoding="utf-8")
        facts_path = case_facts_path(str(negotiation_path), "A")
        facts_path.write_text(
            "Patent owned by {{party_a}}; accused infringer is {{party_b}}",
            encoding="utf-8",
        )

        text = load_case_facts(str(negotiation_path), "A", negotiation)
        assert text == (
            "Patent owned by Summit VI LLC; accused infringer is Samsung Electronics Co., Ltd."
        )


def test_load_case_facts_missing_file_raises():
    with tempfile.TemporaryDirectory() as tmp:
        negotiation_path = Path(tmp) / "negotiation.json"
        negotiation_path.write_text("{}", encoding="utf-8")
        negotiation = Negotiation(case_id="TEST", party_a="A", party_b="B")

        with pytest.raises(FileNotFoundError, match="Case facts file not found"):
            load_case_facts(str(negotiation_path), "A", negotiation)
