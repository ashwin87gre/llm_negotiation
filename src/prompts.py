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


def party_display_name(negotiation: Negotiation, party: str) -> str:
    return negotiation.party_a if party == "A" else negotiation.party_b


def build_system_prompt(
    party: str,
    node: str,
    negotiation: Negotiation,
    agent_instructions: str | None = None,
    case_facts: str | None = None,
) -> str:
    """Party briefing (instructions, case facts, identity) + per-node system prompt."""
    sections: list[str] = []

    if agent_instructions and agent_instructions.strip():
        sections.append(agent_instructions.strip())

    if case_facts and case_facts.strip():
        sections.extend(
            [
                "Case facts (briefing materials for your side):",
                case_facts.strip(),
            ]
        )

    sections.append(
        f"You are representing {party_display_name(negotiation, party)}."
    )

    sections.append(load_prompt(party, node, negotiation))

    return "\n\n---\n\n".join(sections)
