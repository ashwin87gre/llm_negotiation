from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class Action(str, Enum):
    demand = "demand"
    counter = "counter"
    accept = "accept"
    break_ = "break" 


AGENT_ACTIONS: frozenset[Action] = frozenset({Action.counter, Action.accept, Action.break_})

AgentActionLiteral = Literal["accept", "break", "counter"]


def parse_action(value: Action | str) -> Action:
    if isinstance(value, Action):
        return value
    return Action(value)


NegotiationStatus = Literal["in_progress", "agreed", "breakdown"]
Party = Literal["A", "B"]


class PartyMove(BaseModel):
    action: Action
    offer: int | None = None
    reason: str | None = None
    message: str


class OpeningDemand(BaseModel):
    offer: int = Field(gt=0)
    message: str = Field(min_length=1)
    reason: str | None = None


class PartyPrivateState(BaseModel):
    reservation_price: int = Field(gt=0)
    case_strength: float = Field(ge=0.0, le=1.0)
    opponent_argument_risk: float = Field(ge=0.0, le=1.0)
    litigation_cost_estimate: int = Field(gt=0)
    evaluation_summary: str = Field(min_length=1)
    last_updated_round: int = Field(ge=1)


class PrivateStateUpdate(BaseModel):
    reservation_price: int = Field(gt=0)
    case_strength: float = Field(ge=0.0, le=1.0)
    opponent_argument_risk: float = Field(ge=0.0, le=1.0)
    litigation_cost_estimate: int = Field(gt=0)
    evaluation_summary: str = Field(min_length=1)
    round_assessment: str = Field(min_length=1)

    def to_private_state(self, round_number: int) -> PartyPrivateState:
        return PartyPrivateState(
            reservation_price=self.reservation_price,
            case_strength=self.case_strength,
            opponent_argument_risk=self.opponent_argument_risk,
            litigation_cost_estimate=self.litigation_cost_estimate,
            evaluation_summary=self.evaluation_summary,
            last_updated_round=round_number,
        )


class Round(BaseModel):
    round: int
    party_a: PartyMove | None = None
    party_b: PartyMove | None = None


class Negotiation(BaseModel):
    case_id: str
    party_a: str
    party_b: str
    currency: Literal["USD"] = "USD"
    settlement_value: int = -1
    status: NegotiationStatus = "in_progress"
    turns: list[Round] = Field(default_factory=list)


class EvaluationOutput(BaseModel):
    evaluation: str


def format_evaluation_for_action(private_state: PartyPrivateState, round_assessment: str) -> str:
    return (
        f"Reservation price: ${private_state.reservation_price:,}\n"
        f"Case strength: {private_state.case_strength:.2f}\n"
        f"Opponent argument risk: {private_state.opponent_argument_risk:.2f}\n"
        f"Litigation cost estimate: ${private_state.litigation_cost_estimate:,}\n"
        f"Summary: {private_state.evaluation_summary}\n\n"
        f"This round: {round_assessment}"
    )


class ActionOutput(BaseModel):
    action: Action
    offer: int | None = None


def allowed_actions(party: Party, round_number: int) -> frozenset[Action]:
    """Return the actions permitted for an agent move."""
    del party, round_number
    return AGENT_ACTIONS


def build_action_output_model(party: Party, round_number: int) -> type[BaseModel]:
    """Build a structured-output model constrained to allowed actions for this turn."""
    allowed = allowed_actions(party, round_number)
    if allowed != AGENT_ACTIONS:
        raise ValueError("Unexpected allowed_actions set for agent moves")

    class ConstrainedActionOutput(BaseModel):
        action: AgentActionLiteral
        offer: int | None = None
        reason: str = Field(min_length=1)

    ConstrainedActionOutput.__name__ = f"ActionOutput_{party}_R{round_number}"
    return ConstrainedActionOutput


class MessageOutput(BaseModel):
    message: str


class PartyMoveState(TypedDict, total=False):
    party: Party
    negotiation: Negotiation
    negotiation_file_path: str
    agent_instructions: str
    case_facts: str
    round_number: int
    opponent_last_offer: int | None
    evaluation_mode: str
    private_state: PartyPrivateState | None
    private_state_path: str
    evaluation: str | None
    action: Action | str | None
    offer: int | None
    reason: str | None
    message: str | None
    validation_errors: list[str]
    retry_count: int


class NegotiationState(TypedDict, total=False):
    file_path: str
    negotiation: Negotiation
    current_round: Round | None
    last_party_move: PartyMove | None
    done: bool
    max_rounds: int | None


def opponent_offer_for_party(
    negotiation: Negotiation, party: Party, current_round: Round | None
) -> int | None:
    if party == "A":
        if not negotiation.turns:
            return None
        last_complete = negotiation.turns[-1]
        if last_complete.party_b is None:
            return None
        return last_complete.party_b.offer

    if current_round is None:
        return None
    if current_round.party_a is None:
        return None
    return current_round.party_a.offer


def next_round_number(negotiation: Negotiation) -> int:
    if not negotiation.turns:
        return 1
    last = negotiation.turns[-1]
    if last.party_b is not None:
        return last.round + 1
    return last.round


def is_terminal_action(action: Action | str) -> bool:
    parsed = parse_action(action)
    return parsed in {Action.accept, Action.break_}


def needs_start_round_one(negotiation: Negotiation) -> bool:
    return len(negotiation.turns) == 0


def needs_party_a_demand_publish(negotiation: Negotiation) -> bool:
    if not negotiation.turns:
        return False
    last = negotiation.turns[-1]
    return last.round == 1 and last.party_b is None and last.party_a is None
