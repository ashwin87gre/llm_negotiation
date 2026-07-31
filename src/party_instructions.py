from __future__ import annotations

from pathlib import Path

from src.models import Negotiation, Party
from src.prompts import render_prompt


def party_instructions_path(negotiation_path: str, party: Party) -> Path:
    path = Path(negotiation_path)
    return path.with_name(f"{path.stem}.party_{party.lower()}.instructions.txt")


def load_party_instructions(
    negotiation_path: str,
    party: Party,
    negotiation: Negotiation,
) -> str:
    path = party_instructions_path(negotiation_path, party)
    if not path.exists():
        raise FileNotFoundError(
            f"Agent instructions file not found for Party {party}: {path}. "
            "Each party requires a party_{a,b}.instructions.txt file."
        )
    template = path.read_text(encoding="utf-8").strip()
    if not template:
        raise ValueError(f"Agent instructions file is empty: {path}")
    return render_prompt(
        template,
        party_a=negotiation.party_a,
        party_b=negotiation.party_b,
    )
