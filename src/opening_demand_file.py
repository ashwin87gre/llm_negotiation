from __future__ import annotations

import json
from pathlib import Path

from src.models import OpeningDemand


def render_opening_demand_message(message: str, offer: int) -> str:
    formatted = f"${offer:,}"
    return message.replace("{{offer}}", formatted)


def opening_demand_path(negotiation_path: str) -> Path:
    path = Path(negotiation_path)
    return path.with_name(f"{path.stem}.party_a.opening_demand.json")


def load_opening_demand_file(negotiation_path: str) -> OpeningDemand:
    path = opening_demand_path(negotiation_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Party A opening demand file not found: {path}. "
            "Round 1 opening must be supplied in this JSON file."
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    return OpeningDemand.model_validate(data)
