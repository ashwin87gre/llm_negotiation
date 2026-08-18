from __future__ import annotations

from pathlib import Path

from render_negotiation import build_html, load_negotiation

from src.models import Action, Negotiation, PartyMove, Round


def _breakdown_negotiation() -> Negotiation:
    return Negotiation(
        case_id="TEST-482",
        party_a="Summit VI LLC",
        party_b="Samsung Electronics Co., Ltd.",
        status="breakdown",
        settlement_value=-1,
        turns=[
            Round(
                round=1,
                party_a=PartyMove(
                    action=Action.demand,
                    offer=29_000_000,
                    message="We propose a lump-sum payment of $29,000,000.",
                ),
                party_b=PartyMove(
                    action=Action.counter,
                    offer=1_500_000,
                    reason="Comparable licences sit far below the demand.",
                    message="We counter at $1,500,000.",
                ),
            ),
            Round(
                round=2,
                party_a=PartyMove(
                    action=Action.counter,
                    offer=22_000_000,
                    reason="Injunction leverage supports holding near the demand.",
                    message="We can move to $22,000,000.",
                ),
                party_b=PartyMove(
                    action=Action.break_,
                    reason="The gap is too wide to close.",
                    message="We will proceed to litigation.",
                ),
            ),
        ],
    )


def test_build_html_includes_parties_and_moves():
    html_doc = build_html(_breakdown_negotiation())

    assert "Summit VI LLC" in html_doc
    assert "Samsung Electronics Co., Ltd." in html_doc
    assert "Round 1" in html_doc
    assert "Round 2" in html_doc
    assert "We counter at $1,500,000." in html_doc
    assert "Comparable licences sit far below the demand." in html_doc
    assert '<span class="status breakdown">breakdown</span>' in html_doc
    assert "Not settled" in html_doc


def test_build_html_includes_source_path_when_given():
    html_doc = build_html(
        _breakdown_negotiation(),
        Path("sample_run/20260101_000000/negotiation_new.json"),
    )

    assert "Source: sample_run/20260101_000000/negotiation_new.json" in html_doc


def test_build_html_empty_turns():
    negotiation = load_negotiation(Path("examples/negotiation_new.json"))
    html_doc = build_html(negotiation)

    assert "No negotiation turns recorded yet" in html_doc
    assert negotiation.party_a in html_doc
