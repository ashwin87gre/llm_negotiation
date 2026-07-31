from __future__ import annotations

from pathlib import Path

from src.models import Negotiation, Party
from src.prompts import render_prompt


def case_facts_path(negotiation_path: str, party: Party) -> Path:
    path = Path(negotiation_path)
    return path.with_name(f"{path.stem}.party_{party.lower()}.case_facts.txt")


def load_case_facts(negotiation_path: str, party: Party, negotiation: Negotiation) -> str:
    path = case_facts_path(negotiation_path, party)
    if not path.exists():
        raise FileNotFoundError(
            f"Case facts file not found for Party {party}: {path}. "
            "Each party requires a party_{a,b}.case_facts.txt file."
        )
    template = path.read_text(encoding="utf-8").strip()
    if not template:
        raise ValueError(f"Case facts file is empty: {path}")
    return render_prompt(
        template,
        party_a=negotiation.party_a,
        party_b=negotiation.party_b,
    )
