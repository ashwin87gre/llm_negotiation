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

    args = parser.parse_args()

    if args.command == "run":
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
        result = graph.invoke(
            {
                "file_path": str(negotiation_path),
                "done": False,
                "max_rounds": args.max_rounds,
            }
        )
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
