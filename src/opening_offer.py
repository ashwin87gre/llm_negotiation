from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.case_facts import load_case_facts
from src.llm import structured_llm
from src.models import Negotiation, OpeningOfferOutput
from src.party_instructions import load_party_instructions
from src.prompts import build_system_prompt


def build_opening_offer_user_context(*, round_number: int = 1) -> str:
    return "\n".join(
        [
            "This is the opening move before any public negotiation history exists.",
            f"Current round number: {round_number}",
            "Propose your opening lump-sum settlement offer.",
        ]
    )


def generate_opening_offer(
    *,
    negotiation_path: str,
    negotiation: Negotiation,
    party_a_case_facts_path: str | None = None,
) -> int:
    instructions = load_party_instructions(negotiation_path, "A", negotiation)
    case_facts = load_case_facts(
        negotiation_path,
        "A",
        negotiation,
        case_facts_file=party_a_case_facts_path,
    )
    system_prompt = build_system_prompt(
        "A",
        "opening_offer",
        negotiation,
        instructions,
        case_facts,
    )
    user_content = build_opening_offer_user_context()

    llm = structured_llm(OpeningOfferOutput)
    result: OpeningOfferOutput = llm.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
    )
    return result.offer
