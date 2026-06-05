"""Seed dataset loading utilities for demo requirements engineering projects."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.requirements_engineering import score_requirement
from backend.schemas import Requirement, RequirementType


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEED_REQUIREMENTS_PATH = PROJECT_ROOT / "datasets" / "seed_requirements" / "automotive_safety_requirements.jsonl"
SEED_DOCUMENT_PATH = PROJECT_ROOT / "datasets" / "seed_requirements" / "automotive_safety_requirements.md"


def load_seed_requirement_rows(path: Path = SEED_REQUIREMENTS_PATH) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL on line {line_number} in {path}") from exc
    return rows


def load_seed_requirements(path: Path = SEED_REQUIREMENTS_PATH) -> list[Requirement]:
    requirements: list[Requirement] = []
    for row in load_seed_requirement_rows(path):
        score, issues, improvement = score_requirement(
            row["text"],
            row.get("linked_hazard"),
            row.get("linked_safety_goal"),
        )
        requirements.append(
            Requirement(
                id=row["id"],
                type=RequirementType(row["type"]),
                text=row["text"],
                linked_hazard=row.get("linked_hazard"),
                linked_safety_goal=row.get("linked_safety_goal"),
                quality_score=score.overall,
                quality_issues=issues,
                suggested_improvement=improvement if issues else None,
                linked_test_cases=row.get("linked_test_cases", []),
                evidence_source=row.get("evidence_source"),
            )
        )
    return requirements


def seed_document_text(path: Path = SEED_DOCUMENT_PATH) -> str:
    return path.read_text(encoding="utf-8")
