"""Report and export helpers."""

from __future__ import annotations

import csv
import io
import json

from backend.schemas import Requirement, TraceabilityLink


TRACEABILITY_COLUMNS = [
    "hazard_id",
    "hazard_description",
    "safety_goal_id",
    "requirement_id",
    "requirement_type",
    "requirement_text",
    "test_case_id",
    "evidence_source",
    "status",
    "quality_score",
]


def traceability_csv(rows: list[TraceabilityLink]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=TRACEABILITY_COLUMNS)
    writer.writeheader()
    for row in rows:
        data = row.model_dump()
        data["requirement_type"] = row.requirement_type.value
        writer.writerow({column: data.get(column) for column in TRACEABILITY_COLUMNS})
    return output.getvalue()


def requirements_csv(requirements: list[Requirement]) -> str:
    output = io.StringIO()
    fieldnames = ["id", "type", "text", "linked_hazard", "linked_safety_goal", "quality_score", "quality_issues", "suggested_improvement", "evidence_source"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for req in requirements:
        row = req.model_dump()
        row["type"] = req.type.value
        row["quality_issues"] = "; ".join(req.quality_issues)
        writer.writerow({field: row.get(field) for field in fieldnames})
    return output.getvalue()


def markdown_report(project_name: str, requirements: list[Requirement], traceability: list[TraceabilityLink]) -> str:
    payload = {
        "requirements": [req.model_dump(mode="json") for req in requirements],
        "traceability": [row.model_dump(mode="json") for row in traceability],
    }
    lines = [
        f"# {project_name} Safety Requirements Report",
        "",
        "## Summary",
        f"- Requirements: {len(requirements)}",
        f"- Traceability rows: {len(traceability)}",
        "",
        "## Requirements",
    ]
    for req in requirements:
        lines.append(f"- **{req.id}** ({req.type.value}, score {req.quality_score}): {req.text}")
    lines.extend(["", "## Structured JSON", "```json", json.dumps(payload, indent=2), "```"])
    return "\n".join(lines)

