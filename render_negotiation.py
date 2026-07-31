#!/usr/bin/env python3
"""
Standalone visual renderer for negotiation JSON files.

Reads a negotiation JSON (e.g. examples/negotiation_new.json or sample_run/.../negotiation_new.json),
writes an HTML timeline, and opens it in your browser.

Usage:
  python render_negotiation.py path/to/negotiation_new.json
  render-negotiation path/to/negotiation_new.json
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import webbrowser
from pathlib import Path

from src.models import Negotiation, PartyMove


def format_offer(offer: int | None) -> str:
    if offer is None:
        return "—"
    return f"${offer:,}"


def format_action(action: str) -> str:
    return action.replace("_", " ").upper()


def load_negotiation(path: Path) -> Negotiation:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Negotiation.model_validate(data)


def _escape(text: str | None) -> str:
    if not text:
        return ""
    return html.escape(text)


def _move_card(
    party_label: str,
    party_name: str,
    accent: str,
    move: PartyMove | None,
    pending: bool = False,
) -> str:
    if move is None and pending:
        return f"""
        <div class="move-card pending" style="--accent: {accent}">
          <div class="move-header">
            <span class="party-name">{_escape(party_name)}</span>
            <span class="party-tag">{_escape(party_label)}</span>
          </div>
          <p class="pending-text">Awaiting move…</p>
        </div>
        """

    if move is None:
        return ""

    reason_block = ""
    if move.reason:
        reason_block = f"""
        <div class="reason-block">
          <div class="label">Reason</div>
          <p>{_escape(move.reason)}</p>
        </div>
        """

    return f"""
    <div class="move-card" style="--accent: {accent}">
      <div class="move-header">
        <span class="party-name">{_escape(party_name)}</span>
        <span class="party-tag">{_escape(party_label)}</span>
      </div>
      <div class="meta-row">
        <span class="action-badge">{_escape(format_action(move.action.value))}</span>
        <span class="offer">{_escape(format_offer(move.offer))}</span>
      </div>
      {reason_block}
      <div class="message-block">
        <div class="label">Message</div>
        <p>{_escape(move.message)}</p>
      </div>
    </div>
    """


def build_html(negotiation: Negotiation, source_path: Path | None = None) -> str:
    status_class = negotiation.status.replace("_", "-")
    settlement = (
        format_offer(negotiation.settlement_value)
        if negotiation.settlement_value != -1
        else "Not settled"
    )

    rounds_html: list[str] = []
    for turn in negotiation.turns:
        party_b_pending = turn.party_a is not None and turn.party_b is None
        rounds_html.append(
            f"""
        <section class="round">
          <h2 class="round-title">Round {turn.round}</h2>
          <div class="round-moves">
            {_move_card("Party A", negotiation.party_a, "#1d4ed8", turn.party_a)}
            {_move_card("Party B", negotiation.party_b, "#0f766e", turn.party_b, pending=party_b_pending)}
          </div>
        </section>
        """
        )

    if not negotiation.turns:
        rounds_html.append(
            '<p class="empty">No negotiation turns recorded yet.</p>'
        )

    source_line = (
        f'<p class="source">Source: {_escape(str(source_path))}</p>'
        if source_path
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Negotiation — {_escape(negotiation.case_id)}</title>
  <style>
    :root {{
      color-scheme: light dark;
      --bg: #f4f4f5;
      --card: #ffffff;
      --text: #18181b;
      --muted: #52525b;
      --border: #e4e4e7;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #09090b;
        --card: #18181b;
        --text: #fafafa;
        --muted: #a1a1aa;
        --border: #3f3f46;
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .page {{
      max-width: 960px;
      margin: 0 auto;
      padding: 2rem 1.25rem 3rem;
    }}
    header {{
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 1.5rem 1.75rem;
      margin-bottom: 1.5rem;
    }}
    h1 {{
      margin: 0 0 0.35rem;
      font-size: 1.5rem;
    }}
    .case-id {{
      color: var(--muted);
      font-size: 0.95rem;
      margin-bottom: 1rem;
    }}
    .summary-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 0.75rem;
    }}
    .summary-item {{
      background: var(--bg);
      border-radius: 10px;
      padding: 0.75rem 1rem;
    }}
    .summary-item .label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--muted);
    }}
    .summary-item .value {{
      font-weight: 600;
      margin-top: 0.15rem;
    }}
    .status {{
      display: inline-block;
      padding: 0.2rem 0.65rem;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 600;
    }}
    .status.in-progress {{ background: #dbeafe; color: #1e40af; }}
    .status.agreed {{ background: #dcfce7; color: #166534; }}
    .status.breakdown {{ background: #fee2e2; color: #991b1b; }}
    @media (prefers-color-scheme: dark) {{
      .status.in-progress {{ background: #1e3a8a; color: #bfdbfe; }}
      .status.agreed {{ background: #14532d; color: #bbf7d0; }}
      .status.breakdown {{ background: #7f1d1d; color: #fecaca; }}
    }}
    .round {{
      margin-bottom: 1.25rem;
    }}
    .round-title {{
      font-size: 1rem;
      margin: 0 0 0.75rem;
      color: var(--muted);
      font-weight: 600;
      letter-spacing: 0.02em;
    }}
    .round-moves {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}
    .move-card {{
      background: var(--card);
      border: 1px solid var(--border);
      border-left: 4px solid var(--accent);
      border-radius: 14px;
      padding: 1.1rem 1.25rem;
    }}
    .move-card.pending {{
      opacity: 0.75;
    }}
    .move-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      margin-bottom: 0.65rem;
    }}
    .party-name {{
      font-weight: 700;
      font-size: 1.05rem;
    }}
    .party-tag {{
      font-size: 0.75rem;
      color: var(--muted);
      background: var(--bg);
      padding: 0.15rem 0.5rem;
      border-radius: 6px;
    }}
    .meta-row {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 0.85rem;
    }}
    .action-badge {{
      background: var(--accent);
      color: #fff;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      padding: 0.25rem 0.55rem;
      border-radius: 6px;
    }}
    .offer {{
      font-size: 1.35rem;
      font-weight: 700;
    }}
    .label {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
      margin-bottom: 0.35rem;
    }}
    .reason-block {{
      background: var(--bg);
      border-radius: 10px;
      padding: 0.75rem 0.9rem;
      margin-bottom: 0.85rem;
    }}
    .reason-block p {{
      margin: 0;
      white-space: pre-wrap;
    }}
    .message-block p {{
      margin: 0;
      white-space: pre-wrap;
    }}
    .pending-text {{
      color: var(--muted);
      margin: 0;
    }}
    .empty, .source {{
      color: var(--muted);
    }}
    .source {{
      margin-top: 1.5rem;
      font-size: 0.85rem;
    }}
  </style>
</head>
<body>
  <div class="page">
    <header>
      <h1>Negotiation timeline</h1>
      <div class="case-id">{_escape(negotiation.case_id)}</div>
      <div class="summary-grid">
        <div class="summary-item">
          <div class="label">Party A</div>
          <div class="value">{_escape(negotiation.party_a)}</div>
        </div>
        <div class="summary-item">
          <div class="label">Party B</div>
          <div class="value">{_escape(negotiation.party_b)}</div>
        </div>
        <div class="summary-item">
          <div class="label">Status</div>
          <div class="value"><span class="status {status_class}">{_escape(negotiation.status)}</span></div>
        </div>
        <div class="summary-item">
          <div class="label">Settlement</div>
          <div class="value">{_escape(settlement)}</div>
        </div>
      </div>
    </header>
    {"".join(rounds_html)}
    {source_line}
  </div>
</body>
</html>
"""


def render_negotiation_html(negotiation_path: Path) -> str:
    negotiation = load_negotiation(negotiation_path)
    return build_html(negotiation, negotiation_path.resolve())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a negotiation JSON file as a visual HTML timeline.",
    )
    parser.add_argument(
        "negotiation_json",
        type=Path,
        help="Path to negotiation JSON (e.g. examples/negotiation_new.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write HTML to this path (default: <json_stem>_timeline.html beside the JSON)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the report in a browser",
    )
    args = parser.parse_args(argv)

    negotiation_path = args.negotiation_json.resolve()
    if not negotiation_path.exists():
        print(f"Error: file not found: {negotiation_path}", file=sys.stderr)
        return 1

    output_path = args.output
    if output_path is None:
        output_path = negotiation_path.with_name(f"{negotiation_path.stem}_timeline.html")
    else:
        output_path = output_path.resolve()

    html_doc = render_negotiation_html(negotiation_path)
    output_path.write_text(html_doc, encoding="utf-8")
    print(f"Wrote {output_path}")

    if not args.no_open:
        webbrowser.open(output_path.as_uri())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
