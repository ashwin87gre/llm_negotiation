from __future__ import annotations

import json
from pathlib import Path

from src.models import Party, PartyPrivateState


def private_state_path(negotiation_path: str, party: Party) -> Path:
    path = Path(negotiation_path)
    return path.with_name(f"{path.stem}.party_{party.lower()}.private.json")


def load_private_state(path: Path) -> PartyPrivateState | None:
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return PartyPrivateState.model_validate(data)


def save_private_state(path: Path, state: PartyPrivateState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.model_dump(), indent=2) + "\n", encoding="utf-8")
