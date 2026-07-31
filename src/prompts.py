from __future__ import annotations

from pathlib import Path

from src.models import Negotiation

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def render_prompt(template: str, *, party_a: str, party_b: str) -> str:
    return template.replace("{{party_a}}", party_a).replace("{{party_b}}", party_b)


def load_prompt(party: str, node: str, negotiation: Negotiation) -> str:
    path = PROMPTS_DIR / party.lower() / f"{node}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    template = path.read_text(encoding="utf-8").strip()
    return render_prompt(
        template,
        party_a=negotiation.party_a,
        party_b=negotiation.party_b,
    )


def build_system_prompt(
    party: str,
    node: str,
    negotiation: Negotiation,
    agent_instructions: str | None = None,
) -> str:
    """Global agent instructions + per-node system prompt."""
    node_prompt = load_prompt(party, node, negotiation)
    if agent_instructions and agent_instructions.strip():
        return f"{agent_instructions.strip()}\n\n---\n\n{node_prompt}"
    return node_prompt
