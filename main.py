#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from src.graphs.negotiation import build_negotiation_graph
from src.run_workspace import resolve_run_negotiation_path


def _load_dotenv() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def main() -> None:
    _load_dotenv()
    parser = argparse.ArgumentParser(description="Run patent negotiation simulation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run one or more negotiation rounds")
    run_parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help=(
            "Path to an existing negotiation JSON under sample_run/ (resume). "
            "Omit to start a new timestamped run copied from --template."
        ),
    )
    run_parser.add_argument(
        "--template",
        default="examples/negotiation_new.json",
        help="Read-only template negotiation JSON to copy for new runs (default: examples/negotiation_new.json)",
    )
    run_parser.add_argument(
        "--max-rounds",
        type=int,
        default=None,
        help="Maximum number of complete rounds to run (default: unlimited until agreement/breakdown)",
    )
    run_parser.add_argument(
        "--party-a-case-facts",
        default=None,
        metavar="PATH",
        help=(
            "Case facts file for Party A (default: {negotiation_stem}.party_a.case_facts.txt "
            "next to the negotiation JSON)"
        ),
    )
    run_parser.add_argument(
        "--party-b-case-facts",
        default=None,
        metavar="PATH",
        help=(
            "Case facts file for Party B (default: {negotiation_stem}.party_b.case_facts.txt "
            "next to the negotiation JSON)"
        ),
    )

    args = parser.parse_args()

    if args.command == "run":
        for label, path_arg in (
            ("Party A", args.party_a_case_facts),
            ("Party B", args.party_b_case_facts),
        ):
            if path_arg is not None and not Path(path_arg).expanduser().resolve().exists():
                print(f"Error: {label} case facts file not found: {path_arg}", file=sys.stderr)
                sys.exit(1)

        try:
            negotiation_path, created = resolve_run_negotiation_path(
                args.file,
                template=args.template,
            )
        except (ValueError, FileNotFoundError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)

        if created:
            print(f"Run directory: {negotiation_path.parent}")

        graph = build_negotiation_graph()
        invoke_state: dict = {
            "file_path": str(negotiation_path),
            "done": False,
            "max_rounds": args.max_rounds,
        }
        if args.party_a_case_facts is not None:
            invoke_state["party_a_case_facts_path"] = str(
                Path(args.party_a_case_facts).expanduser().resolve()
            )
        if args.party_b_case_facts is not None:
            invoke_state["party_b_case_facts_path"] = str(
                Path(args.party_b_case_facts).expanduser().resolve()
            )
        result = graph.invoke(invoke_state)
        negotiation = result["negotiation"]
        print(f"Negotiation file: {negotiation_path}")
        print(f"Status: {negotiation.status}")
        print(f"Settlement value: {negotiation.settlement_value}")
        print(f"Rounds recorded: {len(negotiation.turns)}")
        if negotiation.status == "in_progress":
            sys.exit(0)
        sys.exit(0)


if __name__ == "__main__":
    main()
