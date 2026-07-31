from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.run_workspace import create_run_from_template, resolve_run_negotiation_path

FRESH_NEGOTIATION = {
    "case_id": "CASE-1",
    "party_a": "Party A",
    "party_b": "Party B",
    "status": "in_progress",
    "settlement_value": -1,
    "turns": [],
}


def test_create_run_from_template_copies_companions_and_resets_negotiation(
    tmp_path: Path,
) -> None:
    template_dir = tmp_path / "examples"
    template_dir.mkdir()
    template_json = template_dir / "negotiation_new.json"
    template_json.write_text(
        json.dumps(
            {
                **FRESH_NEGOTIATION,
                "status": "breakdown",
                "settlement_value": 100,
                "turns": [
                    {
                        "round": 1,
                        "party_a": {
                            "action": "demand",
                            "offer": 1,
                            "message": "demand",
                        },
                        "party_b": {
                            "action": "break",
                            "message": "no deal",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (template_dir / "negotiation_new.party_a.opening_demand.json").write_text(
        '{"offer": 5, "message": "open"}',
        encoding="utf-8",
    )
    (template_dir / "negotiation_new.party_a.instructions.txt").write_text(
        "party a instructions",
        encoding="utf-8",
    )
    (template_dir / "negotiation_new.party_b.instructions.txt").write_text(
        "party b instructions",
        encoding="utf-8",
    )
    (template_dir / "negotiation_new.party_a.case_facts.txt").write_text(
        "party a case facts",
        encoding="utf-8",
    )
    (template_dir / "negotiation_new.party_b.case_facts.txt").write_text(
        "party b case facts",
        encoding="utf-8",
    )
    (template_dir / "negotiation_new.party_a.notes.txt").write_text(
        "extra companion file",
        encoding="utf-8",
    )

    runs_root = tmp_path / "sample_run"
    dest = create_run_from_template(template_json, runs_root=runs_root)

    assert dest.parent.parent == runs_root
    assert dest.name == "negotiation_new.json"
    saved = json.loads(dest.read_text(encoding="utf-8"))
    assert saved["status"] == "in_progress"
    assert saved["settlement_value"] == -1
    assert saved["turns"] == []

    run_dir = dest.parent
    assert (run_dir / "negotiation_new.party_a.opening_demand.json").exists()
    assert (run_dir / "negotiation_new.party_a.instructions.txt").read_text() == "party a instructions"
    assert (run_dir / "negotiation_new.party_b.instructions.txt").read_text() == "party b instructions"
    assert (run_dir / "negotiation_new.party_a.case_facts.txt").read_text() == "party a case facts"
    assert (run_dir / "negotiation_new.party_b.case_facts.txt").read_text() == "party b case facts"
    assert (run_dir / "negotiation_new.party_a.notes.txt").read_text() == "extra companion file"
    assert not (run_dir / "negotiation_new.party_a.private.json").exists()


def test_resolve_run_negotiation_path_refuses_examples(tmp_path: Path, monkeypatch) -> None:
    examples = tmp_path / "examples"
    examples.mkdir()
    negotiation = examples / "negotiation_new.json"
    negotiation.write_text("{}", encoding="utf-8")

    monkeypatch.setattr("src.run_workspace.examples_dir", lambda: examples)

    with pytest.raises(ValueError, match="read-only templates"):
        resolve_run_negotiation_path(str(negotiation))


def test_resolve_run_negotiation_path_creates_timestamped_run(
    tmp_path: Path,
    monkeypatch,
) -> None:
    examples = tmp_path / "examples"
    examples.mkdir()
    template_json = examples / "negotiation_new.json"
    template_json.write_text(json.dumps(FRESH_NEGOTIATION), encoding="utf-8")
    (examples / "negotiation_new.party_a.opening_demand.json").write_text(
        '{"offer": 5, "message": "open"}',
        encoding="utf-8",
    )
    (examples / "negotiation_new.party_a.instructions.txt").write_text("a", encoding="utf-8")
    (examples / "negotiation_new.party_b.instructions.txt").write_text("b", encoding="utf-8")
    (examples / "negotiation_new.party_a.case_facts.txt").write_text("a facts", encoding="utf-8")
    (examples / "negotiation_new.party_b.case_facts.txt").write_text("b facts", encoding="utf-8")

    runs_root = tmp_path / "sample_run"
    monkeypatch.setattr("src.run_workspace.examples_dir", lambda: examples)
    monkeypatch.setattr("src.run_workspace.sample_run_root", lambda: runs_root)

    path, created = resolve_run_negotiation_path(
        None,
        template=str(template_json),
    )

    assert created is True
    assert path.parent.parent == runs_root
    assert path.name == "negotiation_new.json"
