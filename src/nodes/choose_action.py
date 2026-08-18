from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.actions import normalize_action_offer
from src.context import build_user_context
from src.llm import structured_llm
from src.models import PartyMoveState, build_action_output_model
from src.prompts import build_system_prompt


def choose_action(state: PartyMoveState) -> dict:
    party = state["party"]
    negotiation = state["negotiation"]
    round_number = state["round_number"]
    opponent_last_offer = state.get("opponent_last_offer")
    validation_errors = state.get("validation_errors") or []

    system_prompt = build_system_prompt(
        party,
        "choose_action",
        negotiation,
        state.get("agent_instructions"),
        state.get("case_facts"),
    )
    user_content = build_user_context(
        party=party,
        negotiation=negotiation,
        round_number=round_number,
        opponent_last_offer=opponent_last_offer,
        validation_errors=validation_errors or None,
    )

    llm = structured_llm(build_action_output_model(party, round_number))
    result = llm.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
    )

    action = result.action
    offer = normalize_action_offer(action, result.offer, opponent_last_offer)

    return {
        "action": action,
        "offer": offer,
        "reason": result.reason,
        "message": None,
        "validation_errors": [],
    }
