from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.context import (
    format_agent_instructions,
    format_case_facts,
    format_negotiation_history,
    party_display_name,
)
from src.llm import structured_llm
from src.models import PartyMoveState, PartyPrivateState, PrivateStateUpdate, format_evaluation_for_action
from src.prompts import load_prompt


def evaluate_case(state: PartyMoveState) -> dict:
    party = state["party"]
    negotiation = state["negotiation"]
    round_number = state["round_number"]
    opponent_last_offer = state.get("opponent_last_offer")
    private_state = state.get("private_state")
    evaluation_mode = state.get("evaluation_mode")
    agent_instructions = state.get("agent_instructions")
    case_facts = state.get("case_facts")

    if evaluation_mode == "initial":
        if not agent_instructions:
            raise ValueError("Initial evaluation requires agent instructions.")
        if not case_facts:
            raise ValueError("Initial evaluation requires case facts.")
        if private_state is not None:
            raise ValueError("Initial evaluation must not run when private state already exists.")
        prompt_name = "evaluate_initial"
    elif evaluation_mode == "incremental":
        if private_state is None:
            raise ValueError("Incremental evaluation requires existing private state.")
        prompt_name = "evaluate_incremental"
    else:
        raise ValueError(f"Unknown evaluation_mode: {evaluation_mode}")

    system_prompt = load_prompt(party, prompt_name, negotiation)
    user_content = _build_evaluate_user_context(
        party=party,
        negotiation=negotiation,
        round_number=round_number,
        opponent_last_offer=opponent_last_offer,
        agent_instructions=agent_instructions,
        case_facts=case_facts,
        private_state=private_state,
        evaluation_mode=evaluation_mode,
    )

    llm = structured_llm(PrivateStateUpdate)
    result: PrivateStateUpdate = llm.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
    )

    updated_private_state = result.to_private_state(round_number)
    evaluation = format_evaluation_for_action(updated_private_state, result.round_assessment)

    return {
        "private_state": updated_private_state,
        "evaluation": evaluation,
    }


def _build_evaluate_user_context(
    *,
    party: str,
    negotiation,
    round_number: int,
    opponent_last_offer: int | None,
    agent_instructions: str | None,
    case_facts: str | None,
    private_state: PartyPrivateState | None,
    evaluation_mode: str,
) -> str:
    sections: list[str] = []

    if agent_instructions:
        sections.extend([*format_agent_instructions(agent_instructions), "", ""]
        )

    if case_facts:
        sections.extend([*format_case_facts(case_facts), "", ""]
        )

    if private_state is not None and evaluation_mode == "incremental":
        sections.extend(
            [
                "Prior private assessment:",
                format_evaluation_for_action(private_state, "See prior evaluation summary above."),
                "",
                "",
            ]
        )

    sections.extend(
        [
            format_negotiation_history(negotiation),
            "",
            f"You are representing {party_display_name(negotiation, party)}.",
            f"Current round number: {round_number}",
            f"Opponent's most recent offer: {_format_offer(opponent_last_offer)}",
        ]
    )

    return "\n".join(sections)


def _format_offer(offer: int | None) -> str:
    if offer is None:
        return "none"
    return f"${offer:,}"
