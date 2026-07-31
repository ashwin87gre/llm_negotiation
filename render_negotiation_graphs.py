#!/usr/bin/env python3
"""
Standalone batch graph renderer for multiple negotiation runs.

Scans run directories (e.g. sample_run/<timestamp>/negotiation_new.json) and writes
an HTML report with summary charts.

Usage:
  python render_negotiation_graphs.py sample_run
  render-negotiation-graphs sample_run -o report.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path

from render_negotiation import load_negotiation

from src.models import Negotiation


DEFAULT_NEGOTIATION_NAME = "negotiation_new.json"

PARTY_A_COLOR = "#2563eb"
PARTY_B_COLOR = "#ea580c"
END_AGREED_COLOR = "#22c55e"
END_BREAKDOWN_COLOR = "#ef4444"
END_IN_PROGRESS_COLOR = "#94a3b8"


@dataclass
class RunRecord:
    run_id: str
    path: Path
    status: str
    settlement_value: int
    turn_count: int
    party_a_offers: list[tuple[int, int]] = field(default_factory=list)
    party_b_offers: list[tuple[int, int]] = field(default_factory=list)


def _end_outcome_color(status: str) -> str:
    if status == "agreed":
        return END_AGREED_COLOR
    if status == "breakdown":
        return END_BREAKDOWN_COLOR
    return END_IN_PROGRESS_COLOR


def _endpoint_marker_style(point_count: int, end_color: str) -> dict[str, list]:
    if point_count == 0:
        return {"size": [], "color": [], "symbol": []}
    if point_count == 1:
        return {
            "size": [12],
            "color": [end_color],
            "symbol": ["diamond"],
        }
    return {
        "size": [0] * (point_count - 1) + [12],
        "color": ["rgba(0,0,0,0)"] * (point_count - 1) + [end_color],
        "symbol": ["circle"] * (point_count - 1) + ["diamond"],
    }


def _progression_legend_traces() -> list[dict]:
    """Legend-only traces explaining line and endpoint colors."""
    return [
        {
            "name": "Party A (solid)",
            "x": [None],
            "y": [None],
            "mode": "lines",
            "line": {"color": PARTY_A_COLOR, "width": 2.5},
            "showlegend": True,
        },
        {
            "name": "Party B (dashed)",
            "x": [None],
            "y": [None],
            "mode": "lines",
            "line": {"color": PARTY_B_COLOR, "width": 2.5, "dash": "dash"},
            "showlegend": True,
        },
        {
            "name": "Endpoint · agreed",
            "x": [None],
            "y": [None],
            "mode": "markers",
            "marker": {"size": 12, "color": END_AGREED_COLOR, "symbol": "diamond"},
            "showlegend": True,
        },
        {
            "name": "Endpoint · breakdown / incomplete",
            "x": [None],
            "y": [None],
            "mode": "markers",
            "marker": {"size": 12, "color": END_BREAKDOWN_COLOR, "symbol": "diamond"},
            "showlegend": True,
        },
    ]


def discover_negotiation_files(
    roots: list[Path],
    *,
    negotiation_name: str = DEFAULT_NEGOTIATION_NAME,
) -> list[Path]:
    """Find negotiation JSON files under each root directory."""
    found: list[Path] = []
    seen: set[Path] = set()

    for root in roots:
        root = root.resolve()
        if root.is_file() and root.name == negotiation_name:
            if root not in seen:
                seen.add(root)
                found.append(root)
            continue
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            candidate = child / negotiation_name
            if candidate.is_file() and candidate not in seen:
                seen.add(candidate)
                found.append(candidate)

    return sorted(found, key=lambda p: p.parent.name)


def _offer_series(negotiation: Negotiation) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    party_a: list[tuple[int, int]] = []
    party_b: list[tuple[int, int]] = []
    for turn in negotiation.turns:
        if turn.party_a is not None and turn.party_a.offer is not None:
            party_a.append((turn.round, turn.party_a.offer))
        if turn.party_b is not None and turn.party_b.offer is not None:
            party_b.append((turn.round, turn.party_b.offer))
    return party_a, party_b


def load_run_record(path: Path) -> RunRecord:
    negotiation = load_negotiation(path)
    party_a_offers, party_b_offers = _offer_series(negotiation)
    return RunRecord(
        run_id=path.parent.name,
        path=path,
        status=negotiation.status,
        settlement_value=negotiation.settlement_value,
        turn_count=len(negotiation.turns),
        party_a_offers=party_a_offers,
        party_b_offers=party_b_offers,
    )


def _escape(text: str) -> str:
    return html.escape(text)


def build_graphs_html(records: list[RunRecord], title: str) -> str:
    agreed = [r for r in records if r.status == "agreed" and r.settlement_value > 0]
    breakdown = [r for r in records if r.status == "breakdown"]
    in_progress = [r for r in records if r.status == "in_progress"]

    settlement_dots = {
        "run_ids": [r.run_id for r in agreed],
        "amounts": [r.settlement_value for r in agreed],
    }

    outcome_bar = {
        "labels": ["Agreed", "Breakdown (litigation)"],
        "counts": [len(agreed), len(breakdown)],
    }

    turn_hist: dict[int, dict[str, int]] = {}
    for r in agreed:
        turn_hist.setdefault(r.turn_count, {"agreed": 0, "breakdown": 0})["agreed"] += 1
    for r in breakdown:
        turn_hist.setdefault(r.turn_count, {"agreed": 0, "breakdown": 0})["breakdown"] += 1

    turn_counts = sorted(turn_hist.keys())
    turn_chart = {
        "turns": turn_counts,
        "agreed": [turn_hist[t]["agreed"] for t in turn_counts],
        "breakdown": [turn_hist[t]["breakdown"] for t in turn_counts],
    }

    progression_traces: list[dict] = []
    for r in records:
        if not r.party_a_offers and not r.party_b_offers:
            continue
        end_color = _end_outcome_color(r.status)
        if r.party_a_offers:
            n = len(r.party_a_offers)
            endpoint = _endpoint_marker_style(n, end_color)
            progression_traces.append(
                {
                    "name": f"{r.run_id} · party A",
                    "x": [p[0] for p in r.party_a_offers],
                    "y": [p[1] for p in r.party_a_offers],
                    "mode": "lines+markers",
                    "line": {"color": PARTY_A_COLOR, "width": 1.5},
                    "marker": {
                        "size": endpoint["size"],
                        "color": endpoint["color"],
                        "symbol": endpoint["symbol"],
                        "line": {"width": 1.5, "color": end_color},
                    },
                    "legendgroup": r.run_id,
                    "showlegend": False,
                    "hovertemplate": (
                        f"Run {_escape(r.run_id)}<br>Party A<br>"
                        "Round %{x}<br>$%{y:,.0f}<extra></extra>"
                    ),
                }
            )
        if r.party_b_offers:
            n = len(r.party_b_offers)
            endpoint = _endpoint_marker_style(n, end_color)
            progression_traces.append(
                {
                    "name": f"{r.run_id} · party B",
                    "x": [p[0] for p in r.party_b_offers],
                    "y": [p[1] for p in r.party_b_offers],
                    "mode": "lines+markers",
                    "line": {"color": PARTY_B_COLOR, "width": 1.5, "dash": "dash"},
                    "marker": {
                        "size": endpoint["size"],
                        "color": endpoint["color"],
                        "symbol": endpoint["symbol"],
                        "line": {"width": 1.5, "color": end_color},
                    },
                    "legendgroup": r.run_id,
                    "showlegend": False,
                    "hovertemplate": (
                        f"Run {_escape(r.run_id)}<br>Party B<br>"
                        "Round %{x}<br>$%{y:,.0f}<extra></extra>"
                    ),
                }
            )

    progression_traces.extend(_progression_legend_traces())

    chart_data = {
        "settlement_dots": settlement_dots,
        "outcome_bar": outcome_bar,
        "turn_chart": turn_chart,
        "progression_traces": progression_traces,
    }
    chart_json = json.dumps(chart_data)

    summary_lines = [
        f"{len(records)} run(s) loaded",
        f"{len(agreed)} agreed",
        f"{len(breakdown)} breakdown",
    ]
    if in_progress:
        summary_lines.append(f"{len(in_progress)} still in progress (excluded from outcome charts)")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_escape(title)}</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #0f172a;
      --card: #1e293b;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --border: #334155;
    }}
    @media (prefers-color-scheme: light) {{
      :root {{
        --bg: #f8fafc;
        --card: #ffffff;
        --text: #0f172a;
        --muted: #64748b;
        --border: #e2e8f0;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    header {{
      padding: 1.5rem 2rem;
      border-bottom: 1px solid var(--border);
    }}
    h1 {{ margin: 0 0 0.35rem; font-size: 1.5rem; }}
    .summary {{ color: var(--muted); font-size: 0.95rem; }}
    main {{ padding: 1.5rem 2rem 2.5rem; max-width: 1200px; }}
    section {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1rem 1rem 0.5rem;
      margin-bottom: 1.25rem;
    }}
    section h2 {{
      margin: 0 0 0.25rem;
      font-size: 1.1rem;
    }}
    section p {{
      margin: 0 0 0.75rem;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    .chart {{ width: 100%; min-height: 360px; }}
    #chart-progression {{ min-height: 520px; }}
    .legend-note {{
      font-size: 0.85rem;
      color: var(--muted);
      margin: 0.5rem 0 0;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{_escape(title)}</h1>
    <p class="summary">{_escape(" · ".join(summary_lines))}</p>
  </header>
  <main>
    <section>
      <h2>1. Accepted settlement amounts</h2>
      <p>One marker per agreed negotiation. Breakdowns and in-progress runs are omitted.</p>
      <div id="chart-settlements" class="chart"></div>
    </section>
    <section>
      <h2>2. Outcomes</h2>
      <p>Count of negotiations that ended in agreement vs breakdown (litigation).</p>
      <div id="chart-outcomes" class="chart"></div>
    </section>
    <section>
      <h2>3. Turns vs outcome</h2>
      <p>For each number of recorded rounds, how many runs agreed vs broke down.</p>
      <div id="chart-turns" class="chart"></div>
    </section>
    <section>
      <h2>4. Offer progression</h2>
      <p>Blue solid = party A; orange dashed = party B. Diamond at the end of each line shows outcome
         (green = agreed, red = breakdown or incomplete). Agreed runs converge — both lines meet at the same offer.</p>
      <p class="legend-note">Hover a line for run id, party, round, and offer.</p>
      <div id="chart-progression" class="chart"></div>
    </section>
  </main>
  <script>
    const data = {chart_json};

    Plotly.newPlot("chart-settlements", [{{
      type: "scatter",
      mode: "markers",
      x: data.settlement_dots.amounts,
      y: data.settlement_dots.run_ids,
      marker: {{ size: 10, color: "#22c55e", opacity: 0.85 }},
      hovertemplate: "Run %{{y}}<br>$%{{x:,}}<extra></extra>",
    }}], {{
      margin: {{ t: 24, r: 24, b: 56, l: 120 }},
      xaxis: {{ title: "Settlement amount (USD)", tickformat: ",.0f" }},
      yaxis: {{ title: "Run", automargin: true }},
    }}, {{ responsive: true, displayModeBar: true }});

    Plotly.newPlot("chart-outcomes", [{{
      type: "bar",
      x: data.outcome_bar.labels,
      y: data.outcome_bar.counts,
      marker: {{ color: ["#22c55e", "#ef4444"] }},
      hovertemplate: "%{{x}}<br>count=%{{y}}<extra></extra>",
    }}], {{
      margin: {{ t: 24, r: 24, b: 56, l: 56 }},
      yaxis: {{ title: "Number of negotiations", rangemode: "tozero" }},
    }}, {{ responsive: true, displayModeBar: true }});

    Plotly.newPlot("chart-turns", [
      {{
        type: "bar",
        name: "Agreed",
        x: data.turn_chart.turns,
        y: data.turn_chart.agreed,
        marker: {{ color: "#22c55e" }},
      }},
      {{
        type: "bar",
        name: "Breakdown",
        x: data.turn_chart.turns,
        y: data.turn_chart.breakdown,
        marker: {{ color: "#ef4444" }},
      }},
    ], {{
      barmode: "group",
      margin: {{ t: 24, r: 24, b: 56, l: 56 }},
      xaxis: {{ title: "Number of recorded rounds", dtick: 1 }},
      yaxis: {{ title: "Number of negotiations", rangemode: "tozero" }},
      legend: {{ orientation: "h", y: 1.12, x: 0 }},
    }}, {{ responsive: true, displayModeBar: true }});

    const progressionLayout = {{
      margin: {{ t: 48, r: 24, b: 56, l: 72 }},
      xaxis: {{ title: "Round", dtick: 1 }},
      yaxis: {{ title: "Offer (USD)", tickformat: ",.0f", rangemode: "tozero" }},
      hovermode: "closest",
      legend: {{ orientation: "h", y: 1.18, x: 0 }},
    }};
    Plotly.newPlot("chart-progression", data.progression_traces, progressionLayout,
      {{ responsive: true, displayModeBar: true }});
  </script>
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render batch summary graphs for negotiation runs under one or more directories.",
    )
    parser.add_argument(
        "roots",
        nargs="+",
        type=Path,
        help="Run root directory(ies), e.g. sample_run (scans */negotiation_new.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write HTML to this path (default: <first_root>/negotiation_batch_graphs.html)",
    )
    parser.add_argument(
        "--negotiation-name",
        default=DEFAULT_NEGOTIATION_NAME,
        help=f"Negotiation JSON filename in each run folder (default: {DEFAULT_NEGOTIATION_NAME})",
    )
    parser.add_argument(
        "--title",
        default="Negotiation batch report",
        help="Report title shown in the HTML header",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the report in a browser",
    )
    args = parser.parse_args(argv)

    roots = [p.resolve() for p in args.roots]
    paths = discover_negotiation_files(roots, negotiation_name=args.negotiation_name)
    if not paths:
        print(
            f"Error: no {args.negotiation_name} files found under: "
            + ", ".join(str(r) for r in roots),
            file=sys.stderr,
        )
        return 1

    records = [load_run_record(p) for p in paths]
    output_path = args.output
    if output_path is None:
        first_root = roots[0]
        if first_root.is_file():
            output_path = first_root.parent / "negotiation_batch_graphs.html"
        else:
            output_path = first_root / "negotiation_batch_graphs.html"
    output_path = output_path.resolve()

    html_doc = build_graphs_html(records, args.title)
    output_path.write_text(html_doc, encoding="utf-8")
    print(f"Loaded {len(records)} negotiation file(s)")
    print(f"Wrote {output_path}")

    if not args.no_open:
        webbrowser.open(output_path.as_uri())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
