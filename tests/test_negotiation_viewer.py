from __future__ import annotations

from pathlib import Path

from render_negotiation import build_html, load_negotiation


def test_build_html_includes_parties_and_moves():
    negotiation = load_negotiation(
        Path("sample_run/20260614_012654/negotiation_new.json")
    )
    html_doc = build_html(negotiation, Path("sample_run/20260614_012654/negotiation_new.json"))

    assert "Summit VI LLC" in html_doc
    assert "Samsung Electronics Co., Ltd." in html_doc
    assert "Round 1" in html_doc
    assert "Round 2" in html_doc
    assert "Reason" in html_doc or "Message" in html_doc
    assert "breakdown" in html_doc


def test_build_html_empty_turns():
    negotiation = load_negotiation(Path("examples/negotiation_new.json"))
    html_doc = build_html(negotiation)

    assert "No negotiation turns recorded yet" in html_doc
    assert negotiation.party_a in html_doc
