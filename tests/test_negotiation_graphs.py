from __future__ import annotations

from pathlib import Path

from render_negotiation_graphs import (
    build_graphs_html,
    discover_negotiation_files,
    load_run_record,
)


def test_discover_negotiation_files_under_sample_run():
    paths = discover_negotiation_files([Path("sample_run")])
    assert paths
    assert all(p.name == "negotiation_new.json" for p in paths)
    assert all(p.parent.parent.name == "sample_run" for p in paths)


def test_build_graphs_html_includes_charts_and_summary():
    paths = discover_negotiation_files([Path("sample_run")])
    records = [load_run_record(p) for p in paths[:3]]
    html_doc = build_graphs_html(records, "Test report")

    assert "chart-settlements" in html_doc
    assert "chart-outcomes" in html_doc
    assert "chart-turns" in html_doc
    assert "chart-progression" in html_doc
    assert "Test report" in html_doc
    assert "plotly" in html_doc.lower()


def test_load_run_record_extracts_offer_series():
    paths = discover_negotiation_files([Path("sample_run")])
    record = next(r for p in paths if (r := load_run_record(p)).party_a_offers)
    assert record.party_a_offers[0][0] == 1
