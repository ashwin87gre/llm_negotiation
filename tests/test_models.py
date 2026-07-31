from __future__ import annotations

from src.models import (
    Action,
    Negotiation,
    PartyMove,
    Round,
    needs_party_a_demand_publish,
    opponent_offer_for_party,
)


def test_opponent_offer_for_party_b_round_1_reads_party_a_demand():
    negotiation = Negotiation(
        case_id="TEST",
        party_a="A",
        party_b="B",
        turns=[
            Round(
                round=1,
                party_a=PartyMove(
                    action=Action.demand,
                    offer=5000000,
                    message="Opening demand.",
                ),
            )
        ],
    )
    current_round = negotiation.turns[0]

    assert opponent_offer_for_party(negotiation, "B", current_round) == 5000000


def test_needs_party_a_demand_publish():
    empty = Negotiation(case_id="TEST", party_a="A", party_b="B", turns=[])
    assert needs_party_a_demand_publish(empty) is False

    awaiting_demand = Negotiation(
        case_id="TEST",
        party_a="A",
        party_b="B",
        turns=[Round(round=1)],
    )
    assert needs_party_a_demand_publish(awaiting_demand) is True

    demand_published = Negotiation(
        case_id="TEST",
        party_a="A",
        party_b="B",
        turns=[
            Round(
                round=1,
                party_a=PartyMove(action=Action.demand, offer=5000000, message="Open."),
            )
        ],
    )
    assert needs_party_a_demand_publish(demand_published) is False
