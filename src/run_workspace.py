from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from src.nodes.persist import load_negotiation_file, save_negotiation_file

TEMPLATE_SUFFIXES = (
    ".party_a.opening_demand.json",
    ".party_a.instructions.txt",
    ".party_b.instructions.txt",
    ".party_a.case_facts.txt",
    ".party_b.case_facts.txt",
)

REQUIRED_COMPANION_SUFFIXES = TEMPLATE_SUFFIXES


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def examples_dir() -> Path:
    return project_root() / "examples"


def sample_run_root() -> Path:
    return project_root() / "sample_run"


def is_under_directory(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory.resolve())
        return True
    except ValueError:
        return False


def _companion_paths_for_stem(stem_path: Path) -> list[Path]:
    return [Path(f"{stem_path}{suffix}") for suffix in REQUIRED_COMPANION_SUFFIXES]


def _template_companion_files(template_negotiation_json: Path) -> list[Path]:
    """All files in the template bundle except the main negotiation JSON."""
    template_dir = template_negotiation_json.parent
    stem_name = template_negotiation_json.with_suffix("").name
    companions = sorted(template_dir.glob(f"{stem_name}.*"))
    return [path for path in companions if path != template_negotiation_json]


def create_run_from_template(
    template_negotiation_json: Path,
    *,
    runs_root: Path | None = None,
) -> Path:
    template_negotiation_json = template_negotiation_json.resolve()
    if not template_negotiation_json.exists():
        raise FileNotFoundError(f"Template negotiation file not found: {template_negotiation_json}")

    runs_root = (runs_root or sample_run_root()).resolve()
    run_dir = runs_root / datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)

    dest_negotiation = run_dir / template_negotiation_json.name
    negotiation = load_negotiation_file(str(template_negotiation_json))
    negotiation.turns = []
    negotiation.status = "in_progress"
    negotiation.settlement_value = -1
    save_negotiation_file(str(dest_negotiation), negotiation)

    stem = template_negotiation_json.with_suffix("")
    for companion in _companion_paths_for_stem(stem):
        if not companion.exists():
            raise FileNotFoundError(
                f"Template companion file not found for run: {companion}"
            )

    for companion in _template_companion_files(template_negotiation_json):
        shutil.copy2(companion, run_dir / companion.name)

    return dest_negotiation


def resolve_run_negotiation_path(
    file_arg: str | None,
    *,
    template: str | None = None,
) -> tuple[Path, bool]:
    """Return negotiation JSON path and whether a new run directory was created."""
    if file_arg:
        negotiation_path = Path(file_arg).resolve()
        if is_under_directory(negotiation_path, examples_dir()):
            raise ValueError(
                "Refusing to run against examples/ (read-only templates). "
                "Omit the file argument to start a new timestamped run under sample_run/, "
                "or pass a negotiation JSON path under sample_run/ to resume."
            )
        if not negotiation_path.exists():
            raise FileNotFoundError(f"Negotiation file not found: {negotiation_path}")
        return negotiation_path, False

    template_path = Path(template or "examples/negotiation_new.json")
    if not template_path.is_absolute():
        template_path = project_root() / template_path
    negotiation_path = create_run_from_template(template_path)
    return negotiation_path, True
