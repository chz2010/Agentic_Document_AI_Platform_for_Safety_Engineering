"""Requirements extraction, quality scoring, traceability, and test generation."""

from __future__ import annotations

import re
from statistics import mean

from backend.schemas import Requirement, RequirementQualityScore, RequirementType, TestCase, TraceabilityLink


REQ_PATTERN = re.compile(
    r"\s*(?P<id>(?:REQ|SR|FSR|TSR|SWR|HWR|VAL|MON|DATA)[-_A-Z0-9]*\d+)?\s*[:\-]?\s*"
    r"(?P<text>[^.\n]*(?:shall|must|should|required to|needs to)[^.\n]*(?:\.|$))",
    re.IGNORECASE,
)
HAZARD_PATTERN = re.compile(r"\b(HZ[-_A-Z0-9]*\d+)\b", re.IGNORECASE)
SAFETY_GOAL_PATTERN = re.compile(r"\b(SG[-_A-Z0-9]*\d+)\b", re.IGNORECASE)


def classify_requirement(text: str) -> RequirementType:
    lower = text.lower()
    if any(term in lower for term in ["dataset", "training data", "validation data"]):
        return RequirementType.dataset_requirement
    if any(term in lower for term in ["monitor", "logging", "runtime"]):
        return RequirementType.monitoring_requirement
    if any(term in lower for term in ["verify", "validate", "test", "evidence"]):
        return RequirementType.validation_requirement
    if "software" in lower:
        return RequirementType.software_requirement
    if "hardware" in lower or "sensor" in lower:
        return RequirementType.hardware_requirement
    if any(term in lower for term in ["asil", "safe state", "fault", "hazard"]):
        return RequirementType.functional_safety_requirement
    if "technical safety" in lower:
        return RequirementType.technical_safety_requirement
    if "safety" in lower:
        return RequirementType.safety_requirement
    return RequirementType.functional_requirement


def score_requirement(text: str, linked_hazard: str | None, linked_safety_goal: str | None) -> tuple[RequirementQualityScore, list[str], str]:
    lower = text.lower()
    issues: list[str] = []
    vague_terms = ["appropriate", "sufficient", "robust", "as soon as possible", "quickly", "adequate"]
    measurable = bool(re.search(r"\b\d+(\.\d+)?\s?(ms|s|m|km/h|%|deg|lux|fps|hz|seconds|meters)\b", lower))
    verification = any(term in lower for term in ["test", "verify", "validate", "measure", "evidence", "pass"])
    odd = any(term in lower for term in ["odd", "operational design domain", "night", "rain", "fog", "occlusion", "speed", "lighting"])
    ambiguous = any(term in lower for term in vague_terms)
    atomic = lower.count(" and ") + lower.count(" or ") <= 2

    if ambiguous:
        issues.append("too vague")
    if not verification:
        issues.append("missing verification method")
    if not measurable:
        issues.append("missing measurable threshold")
    if not odd:
        issues.append("missing ODD condition")
    if not linked_hazard:
        issues.append("missing linked hazard")
    if not linked_safety_goal:
        issues.append("missing linked safety goal")
    if not atomic:
        issues.append("not atomic")

    score = RequirementQualityScore(
        atomicity=1.0 if atomic else 0.45,
        clarity=0.55 if ambiguous else 0.9,
        testability=0.9 if verification else 0.45,
        measurability=0.95 if measurable else 0.35,
        traceability=mean([1.0 if linked_hazard else 0.35, 1.0 if linked_safety_goal else 0.35]),
        ambiguity=0.2 if ambiguous else 0.9,
        duplication=0.8,
        conflict_risk=0.8,
    )
    score.overall = round(mean([
        score.atomicity,
        score.clarity,
        score.testability,
        score.measurability,
        score.traceability,
        score.ambiguity,
        score.duplication,
        score.conflict_risk,
    ]), 2)
    improvement = "Add measurable thresholds, ODD boundaries, hazard/safety-goal links, and a verification method."
    return score, issues, improvement


def extract_requirements_from_text(text: str, evidence_source: str | None = None) -> list[Requirement]:
    requirements: list[Requirement] = []
    seen: set[str] = set()
    for idx, match in enumerate(REQ_PATTERN.finditer(text), start=1):
        req_text = " ".join(match.group("text").strip().split())
        if len(req_text) < 20 or req_text.lower() in seen:
            continue
        seen.add(req_text.lower())
        req_id = match.group("id") or f"REQ-AUTO-{idx:03d}"
        hazard = _first_match(HAZARD_PATTERN, req_text)
        safety_goal = _first_match(SAFETY_GOAL_PATTERN, req_text)
        score, issues, improvement = score_requirement(req_text, hazard, safety_goal)
        requirements.append(
            Requirement(
                id=req_id,
                type=classify_requirement(req_text),
                text=req_text,
                linked_hazard=hazard,
                linked_safety_goal=safety_goal,
                quality_score=score.overall,
                quality_issues=issues,
                suggested_improvement=improvement if issues else None,
                evidence_source=evidence_source,
            )
        )
    return requirements


def quality_summary(requirements: list[Requirement]) -> dict:
    if not requirements:
        return {"count": 0, "average_quality_score": 0.0, "common_issues": []}
    issue_counts: dict[str, int] = {}
    for req in requirements:
        for issue in req.quality_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
    return {
        "count": len(requirements),
        "average_quality_score": round(mean(req.quality_score for req in requirements), 2),
        "common_issues": sorted(issue_counts, key=issue_counts.get, reverse=True)[:8],
    }


def build_traceability(requirements: list[Requirement]) -> list[TraceabilityLink]:
    return [
        TraceabilityLink(
            hazard_id=req.linked_hazard,
            hazard_description=None,
            safety_goal_id=req.linked_safety_goal,
            requirement_id=req.id,
            requirement_type=req.type,
            requirement_text=req.text,
            test_case_id=req.linked_test_cases[0] if req.linked_test_cases else None,
            evidence_source=req.evidence_source,
            status="needs_review" if req.quality_issues else "draft_complete",
            quality_score=req.quality_score,
        )
        for req in requirements
    ]


def generate_test_cases(requirements: list[Requirement]) -> list[TestCase]:
    test_cases: list[TestCase] = []
    for idx, req in enumerate(requirements, start=1):
        test_cases.append(
            TestCase(
                id=f"TC-{req.id.replace('REQ-', '').replace('_', '-')}-{idx:03d}",
                scenario=f"Verification scenario for {req.id}",
                preconditions=["System configured within declared ODD", "Required sensors and logging are active"],
                test_steps=[
                    "Prepare scenario inputs and safety monitor configuration",
                    "Execute the scenario across nominal and edge-case variants",
                    "Collect logs, detections, warnings, and pass/fail evidence",
                ],
                expected_result=f"The system satisfies: {req.text}",
                pass_fail_criteria="Pass only if measured behavior satisfies the requirement threshold and evidence is recorded.",
                linked_requirement=req.id,
                required_evidence=["test log", "scenario configuration", "measured result summary"],
            )
        )
    return test_cases


def _first_match(pattern: re.Pattern, text: str) -> str | None:
    match = pattern.search(text)
    return match.group(1).upper() if match else None
