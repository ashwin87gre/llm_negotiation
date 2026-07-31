#!/usr/bin/env bash
# Run the negotiation simulation 30 times sequentially (new sample_run each time).
# Usage: ./run_batch.sh
# Requires: OPENAI_API_KEY (or .env in repo root). Uses .venv if present.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ -f .venv/bin/activate ]]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi

RUNS=30
MAX_ROUNDS=20

echo "Starting $RUNS runs with --max-rounds $MAX_ROUNDS"
echo "Working directory: $ROOT"
echo

failed=0
for i in $(seq 1 "$RUNS"); do
  echo "=== Run $i/$RUNS (max-rounds=$MAX_ROUNDS) ==="
  if python3 main.py run --max-rounds "$MAX_ROUNDS"; then
    echo "Run $i finished OK."
  else
    echo "Run $i failed." >&2
    failed=$((failed + 1))
  fi
  echo
done

echo "Batch complete: $RUNS runs, $failed failed."
exit "$failed"
