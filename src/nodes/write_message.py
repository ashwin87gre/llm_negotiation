from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from src.context import build_user_context
from src.llm import structured_llm
from src.models import MessageOutput, PartyMoveState
from src.prompts import build_system_prompt


def write_message(state: PartyMoveState) -> dict:
    party = state["party"]
    negotiation = state["negotiation"]
    round_number = state["round_number"]
    opponent_last_offer = state.get("opponent_last_offer")
    action = state.get("action")
    offer = state.get("offer")

    if action is None:
        raise ValueError("write_message requires action in state")

    system_prompt = build_system_prompt(
        party,
        "write_message",
        negotiation,
        state.get("agent_instructions"),
    )
    user_content = build_user_context(
        party=party,
        negotiation=negotiation,
        round_number=round_number,
        opponent_last_offer=opponent_last_offer,
        case_facts=state.get("case_facts"),
        action=action,
        offer=offer,
        reason=state.get("reason"),
    )

    llm = structured_llm(MessageOutput)
    result: MessageOutput = llm.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
    )

    return {"message": result.message}
