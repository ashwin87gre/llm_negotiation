from __future__ import annotations

from src.models import Negotiation
from src.prompts import build_system_prompt, load_prompt, render_prompt


def test_render_prompt_substitutes_party_names():
    template = "Counsel for {{party_a}} negotiating with {{party_b}}"
    rendered = render_prompt(
        template,
        party_a="Summit VI LLC",
        party_b="Samsung Electronics Co., Ltd.",
    )
    assert rendered == "Counsel for Summit VI LLC negotiating with Samsung Electronics Co., Ltd."


def test_load_prompt_substitutes_names_from_negotiation():
    negotiation = Negotiation(
        case_id="TEST",
        party_a="Summit VI LLC",
        party_b="Samsung Electronics Co., Ltd.",
    )
    prompt = load_prompt("A", "write_message", negotiation)
    assert "Samsung Electronics Co., Ltd." in prompt
    assert "{{party_b}}" not in prompt


def test_build_system_prompt_combines_instructions_node_prompt_and_case_facts():
    negotiation = Negotiation(
        case_id="TEST",
        party_a="Summit VI LLC",
        party_b="Samsung Electronics Co., Ltd.",
    )
    system = build_system_prompt(
        "B",
        "choose_action",
        negotiation,
        "Represent Samsung in licensing discussions.",
        "Injunction likelihood is high.",
    )
    assert system.startswith("Represent Samsung in licensing discussions.")
    assert "Case facts (briefing materials for your side):" in system
    assert "Injunction likelihood is high." in system
    assert "You are representing Samsung Electronics Co., Ltd." in system
    assert "---" in system
    assert "decision only" in system.lower()
    assert "{{party_a}}" not in system
    assert "Summit VI LLC" in system
