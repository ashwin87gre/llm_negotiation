# llm_negotiation

A LangGraph simulation of a patent licensing negotiation. Two LLM agents — Summit VI LLC
(patent holder) and Samsung (licensee) — exchange offers and letters over the '482 MMS
patent until one side accepts, walks away, or a round limit is reached.

Each agent sees its own private briefing and the shared public transcript, and nothing else.

## Setup

Requires Python 3.11 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Installing with `-e .` also puts three commands on your PATH: `llm-negotiation`,
`render-negotiation`, and `render-negotiation-graphs`. Every example below also shows the
plain `python` form, which works without installing.

Create a `.env` in the repo root (`main.py` loads it at startup):

```
OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4o-mini
```

`OPENAI_MODEL` is optional and defaults to `gpt-4o-mini`. All LLM calls run at
`temperature=0.7`.

## Running a single negotiation

```bash
python main.py run
```

This creates a fresh timestamped run directory, plays the negotiation to completion, and
prints the settlement value and round count.

Cap the number of rounds — useful for smoke tests and for keeping batch runs bounded:

```bash
python main.py run --max-rounds 5
```

This is still **one** negotiation that stops after at most 5 complete rounds, not 5 runs.

Resume an existing run by passing its JSON path:

```bash
python main.py run sample_run/20260804_080153/negotiation_new.json --max-rounds 10
```

Running directly against `examples/` is refused, since those are read-only templates.

### Swapping in different case facts

By default each party reads the case facts file sitting next to the run's negotiation JSON.
Override either or both to simulate parties that read the same dispute differently:

```bash
python main.py run \
  --party-a-case-facts examples/negotiation_new.party_a.case_facts.txt \
  --party-b-case-facts examples/negotiation_new.party_b.case_facts.txt
```

Override files are read from the path you give and are **not** copied into the run
directory, so the run folder won't record which variant was used. Note that down if you're
comparing conditions.

## Running many negotiations

`run_batch.sh` runs a sequence of independent negotiations, each into its own directory:

```bash
./run_batch.sh
```

Counts are set at the top of the script — edit `RUNS` and `MAX_ROUNDS` to change them:

```bash
RUNS=30
MAX_ROUNDS=20
```

The script activates `.venv` if present, keeps going after a failed run, and exits with the
number of failures.

For a one-off batch without editing the script:

```bash
for i in $(seq 1 10); do python main.py run --max-rounds 20; done
```

Because runs are named by UTC timestamp to the second, avoid running two batches in
parallel in the same directory.

## Where output is stored

Every run creates its own directory:

```
sample_run/<YYYYMMDD_HHMMSS>/     # UTC timestamp
├── negotiation_new.json                      # the transcript, rewritten after every move
├── negotiation_new.party_a.opening_demand.json
├── negotiation_new.party_a.instructions.txt
├── negotiation_new.party_b.instructions.txt
├── negotiation_new.party_a.case_facts.txt
└── negotiation_new.party_b.case_facts.txt
```

The companion files are copied from the template bundle in `examples/` at run start, so each
run is a self-contained record of the inputs it used — edit `examples/` to change the
scenario for future runs, and past runs stay reproducible.

`sample_run/` is gitignored.

`negotiation_new.json` is the durable state. It is saved after each half-round rather than
at the end, so an interrupted run is still resumable. Its shape:

```json
{
  "case_id": "...",
  "party_a": "Summit VI LLC",
  "party_b": "Samsung Electronics Co., Ltd.",
  "status": "agreed",
  "settlement_value": 4200000,
  "turns": [
    {
      "round": 1,
      "party_a": {"action": "demand", "offer": 29000000, "reason": null, "message": "..."},
      "party_b": {"action": "counter", "offer": 1500000, "reason": "...", "message": "..."}
    }
  ]
}
```

`status` is one of `agreed`, `breakdown`, or `in_progress`. `settlement_value` is `-1` when
there is no settlement. Note that a run stopped by `--max-rounds` exits as `in_progress`
with `-1`, which is distinct from a `breakdown` — check `status`, not the value, when
classifying outcomes.

The `reason` field records each agent's internal rationale. It is written to disk and shown
in the timeline viewer, but is never included in the transcript sent to either agent.

## Generating the graphs

### One run, as a timeline

```bash
render-negotiation sample_run/20260804_080153/negotiation_new.json
# or: python render_negotiation.py sample_run/20260804_080153/negotiation_new.json
```

Writes `negotiation_new_timeline.html` beside the JSON and opens it in a browser.

### Many runs, as summary charts

```bash
render-negotiation-graphs sample_run
# or: python render_negotiation_graphs.py sample_run
```

Scans one level deep for `*/negotiation_new.json`, then writes
`sample_run/negotiation_batch_graphs.html` and opens it. The report has four charts:
settlement amounts per agreed run, agreed versus breakdown counts, rounds taken versus
outcome, and offer progression for every run overlaid on one axis.

Both commands accept `-o PATH` to choose the output file and `--no-open` to skip launching a
browser. The batch report loads Plotly from a CDN, so viewing it needs an internet
connection.

You can also point the batch renderer at several directories at once to compare conditions:

```bash
render-negotiation-graphs runs_high_injunction runs_low_injunction \
  -o comparison.html --title "Injunction sensitivity"
```

## Tests

```bash
python -m pytest -q
```

The suite is hermetic — no test depends on run output under `sample_run/`, and no test makes
network or LLM calls. Anything touching the model is mocked.

## Changing the scenario

| What to change | File |
|---|---|
| Party briefing, confidential goals, litigation outlook | `examples/negotiation_new.party_{a,b}.case_facts.txt` |
| Negotiating style, when to accept or walk away | `examples/negotiation_new.party_{a,b}.instructions.txt` |
| Opening letter text (`{{offer}}` is substituted) | `examples/negotiation_new.party_a.opening_demand.json` |
| Per-step task rules for the agents | `prompts/{a,b}/*.md` |
| Company names, case id | `examples/negotiation_new.json` |

The opening demand amount is generated by the model from Party A's case facts and
substituted into the `{{offer}}` placeholder, so it varies between runs.

## How it works

A LangGraph outer graph in `src/graphs/negotiation.py` drives the negotiation: it loads the
JSON, publishes Party A's opening demand, then alternates between the two parties until
someone accepts or breaks. Each party's turn runs a small inner graph
(`src/graphs/party_move.py`) of three nodes — `choose_action` picks the action and offer,
`write_message` drafts the public letter, and `validate_move` checks the result and retries
up to three times.

Neither graph uses a checkpointer. Durability comes entirely from rewriting the negotiation
JSON after each move.

For each LLM call, the system message carries the party's instructions, its case facts, its
identity, and the task rules for that step. The user message carries only what changes:
the public transcript as JSON, the round number, and the opponent's last offer.
