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
REQ_BLOCK_PATTERN = re.compile(
    r"(?ms)^\s*(?P<id>(?:REQ|SR|FSR|TSR|SWR|HWR|VAL|MON|DATA)[-_A-Z0-9]*\d+)\s*:\s*"
    r"(?P<body>.*?)(?=^\s*(?:REQ|SR|FSR|TSR|SWR|HWR|VAL|MON|DATA)[-_A-Z0-9]*\d+\s*:|^\s*#{1,6}\s+|\Z)",
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
    used_spans: list[tuple[int, int]] = []
    for block in REQ_BLOCK_PATTERN.finditer(text):
        used_spans.append(block.span())
        req_id = block.group("id").upper()
        block_text = _normalize_requirement_block(block.group("body"))
        req_text = _requirement_statement(block_text)
        _append_requirement(requirements, seen, req_id, req_text, block_text, evidence_source)

    fallback_index = len(requirements) + 1
    for match in REQ_PATTERN.finditer(text):
        if any(start <= match.start() < end for start, end in used_spans):
            continue
        req_text = " ".join(match.group("text").strip().split())
        req_id = (match.group("id") or f"REQ-AUTO-{fallback_index:03d}").upper()
        added = _append_requirement(requirements, seen, req_id, req_text, req_text, evidence_source)
        if added:
            fallback_index += 1
    return requirements


def _append_requirement(
    requirements: list[Requirement],
    seen: set[str],
    req_id: str,
    req_text: str,
    traceability_text: str,
    evidence_source: str | None,
) -> bool:
    req_text = " ".join(req_text.strip().split())
    traceability_text = " ".join(traceability_text.strip().split())
    if len(req_text) < 20 or req_text.lower() in seen:
        return False
    seen.add(req_text.lower())
    hazard = _first_match(HAZARD_PATTERN, traceability_text)
    safety_goal = _first_match(SAFETY_GOAL_PATTERN, traceability_text)
    score, issues, improvement = score_requirement(traceability_text or req_text, hazard, safety_goal)
    requirements.append(
        Requirement(
            id=req_id,
            type=classify_requirement(traceability_text or req_text),
            text=req_text,
            linked_hazard=hazard,
            linked_safety_goal=safety_goal,
            quality_score=score.overall,
            quality_issues=issues,
            suggested_improvement=improvement if issues else None,
            evidence_source=evidence_source,
        )
    )
    return True


def _normalize_requirement_block(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lines.append(stripped)
    return " ".join(lines)


def _requirement_statement(block_text: str) -> str:
    if not block_text:
        return ""
    split_markers = [
        " Linked hazard:",
        " Linked Hazard:",
        " linked hazard:",
        " Linked safety goal:",
        " Linked Safety Goal:",
        " linked safety goal:",
    ]
    cut = len(block_text)
    for marker in split_markers:
        marker_index = block_text.find(marker)
        if marker_index != -1:
            cut = min(cut, marker_index)
    return block_text[:cut].strip()


def generate_requirements_from_standards(
    standards: list[str],
    domain: str = "Autonomous driving",
    system_type: str = "ADAS",
) -> list[Requirement]:
    """Create reviewable starter requirements mapped to candidate ISO clause areas."""
    selected = {standard.lower() for standard in standards}
    templates: list[dict[str, str]] = []
    if any("26262" in standard for standard in selected):
        templates.extend(
            [
                {
                    "id": "REQ-ISO26262-HARA-001",
                    "type": RequirementType.functional_safety_requirement.value,
                    "text": f"The {system_type} safety case shall define HARA-derived hazardous events for the declared ODD, including severity, exposure, controllability, and ASIL classification, and verify completeness during safety review.",
                    "hazard": "HZ-ISO26262-001",
                    "safety_goal": "SG-ISO26262-001",
                    "source": "ISO 26262-3:2018 Clause 6 candidate reference: hazard analysis and risk assessment",
                },
                {
                    "id": "REQ-ISO26262-FSC-001",
                    "type": RequirementType.functional_safety_requirement.value,
                    "text": f"The {system_type} system shall define functional safety goals and safe-state behavior for each ASIL-relevant hazardous event within the ODD and verify traceability from hazard to safety goal.",
                    "hazard": "HZ-ISO26262-001",
                    "safety_goal": "SG-ISO26262-001",
                    "source": "ISO 26262-3:2018 Clause 7 candidate reference: functional safety concept",
                },
                {
                    "id": "REQ-ISO26262-TSC-001",
                    "type": RequirementType.technical_safety_requirement.value,
                    "text": f"The {system_type} architecture shall allocate technical safety requirements to system elements with diagnostic coverage targets and verification evidence for fault detection within 100 ms where applicable.",
                    "hazard": "HZ-ISO26262-002",
                    "safety_goal": "SG-ISO26262-002",
                    "source": "ISO 26262-4:2018 Clause 6 and Clause 7 candidate reference: technical safety concept and system architectural design",
                },
                {
                    "id": "REQ-ISO26262-VALID-001",
                    "type": RequirementType.validation_requirement.value,
                    "text": f"The {system_type} validation plan shall verify safety goals through scenario tests, fault-injection tests, and recorded evidence across nominal and boundary ODD conditions with pass/fail criteria.",
                    "hazard": "HZ-ISO26262-003",
                    "safety_goal": "SG-ISO26262-003",
                    "source": "ISO 26262-4:2018 Clause 9 candidate reference: safety validation",
                },
            ]
        )
    if any("21448" in standard or "sotif" in standard for standard in selected):
        templates.extend(
            [
                {
                    "id": "REQ-ISO21448-SOTIF-001",
                    "type": RequirementType.safety_requirement.value,
                    "text": f"The {system_type} system shall identify reasonably foreseeable misuse, performance limitations, and triggering conditions for the declared ODD and document mitigation evidence before release.",
                    "hazard": "HZ-SOTIF-001",
                    "safety_goal": "SG-SOTIF-001",
                    "source": "ISO 21448:2022 Clause 6 candidate reference: SOTIF specification and design considerations",
                },
                {
                    "id": "REQ-ISO21448-TRIG-001",
                    "type": RequirementType.validation_requirement.value,
                    "text": f"The {system_type} evaluation shall include scenario tests for known triggering conditions such as low light, occlusion, adverse weather, and unusual pedestrian behavior, with measurable detection and response criteria.",
                    "hazard": "HZ-SOTIF-002",
                    "safety_goal": "SG-SOTIF-002",
                    "source": "ISO 21448:2022 Clause 7 candidate reference: evaluation of triggering conditions",
                },
            ]
        )
    if any("8800" in standard for standard in selected):
        templates.extend(
            [
                {
                    "id": "REQ-ISO8800-DATA-001",
                    "type": RequirementType.dataset_requirement.value,
                    "text": f"The {system_type} AI dataset shall define ODD coverage, data provenance, labeling quality checks, class balance targets above 95% review completion, and validation evidence for safety-relevant scenarios.",
                    "hazard": "HZ-AI-001",
                    "safety_goal": "SG-AI-001",
                    "source": "ISO 8800 candidate reference: AI safety lifecycle, data assurance, and validation clause area",
                },
                {
                    "id": "REQ-ISO8800-MON-001",
                    "type": RequirementType.monitoring_requirement.value,
                    "text": f"The {system_type} AI runtime shall monitor model confidence, ODD exits, sensor degradation, and safety-relevant prediction uncertainty every 100 ms and trigger a documented fallback strategy when thresholds are violated.",
                    "hazard": "HZ-AI-002",
                    "safety_goal": "SG-AI-002",
                    "source": "ISO 8800 candidate reference: AI monitoring, operational controls, and safety assurance clause area",
                },
            ]
        )
    if any(term in standard for standard in selected for term in ["62278", "50126", "50128", "50129", "ertms", "62425", "rail"]):
        templates.extend(
            [
                {
                    "id": "REQ-RAIL-RAMS-001",
                    "type": RequirementType.safety_requirement.value,
                    "text": f"The {system_type} project shall define RAMS objectives, lifecycle phase responsibilities, acceptance criteria, and verification evidence for each safety-relevant function before authorization.",
                    "hazard": "HZ-RAIL-RAMS-001",
                    "safety_goal": "SG-RAIL-RAMS-001",
                    "source": "IEC 62278 / EN 50126 candidate reference: RAMS lifecycle and safety management clause area",
                },
                {
                    "id": "REQ-RAIL-HAZLOG-001",
                    "type": RequirementType.functional_safety_requirement.value,
                    "text": f"The {system_type} hazard log shall link each identified railway hazard to causes, mitigations, responsible owner, verification evidence, residual risk status, and safety case argument.",
                    "hazard": "HZ-RAIL-HAZLOG-001",
                    "safety_goal": "SG-RAIL-HAZLOG-001",
                    "source": "IEC 62278 / EN 50126 candidate reference: hazard analysis, risk evaluation, and hazard log management",
                },
                {
                    "id": "REQ-RAIL-SW-001",
                    "type": RequirementType.software_requirement.value,
                    "text": f"The {system_type} software shall define safety integrity assumptions, design constraints, verification activities, test coverage evidence above 95 percent for safety-relevant logic, and change impact analysis before release.",
                    "hazard": "HZ-RAIL-SW-001",
                    "safety_goal": "SG-RAIL-SW-001",
                    "source": "EN 50128 candidate reference: railway software lifecycle, verification, validation, and safety integrity clause area",
                },
                {
                    "id": "REQ-RAIL-SAFETYCASE-001",
                    "type": RequirementType.validation_requirement.value,
                    "text": f"The {system_type} safety case shall provide traceable evidence from hazards to safety requirements, verification results, validation reports, open issues, approvals, and operational restrictions.",
                    "hazard": "HZ-RAIL-CASE-001",
                    "safety_goal": "SG-RAIL-CASE-001",
                    "source": "EN 50129 / IEC 62425 candidate reference: safety case structure, evidence, and approval argument clause area",
                },
                {
                    "id": "REQ-RAIL-ERTMS-001",
                    "type": RequirementType.validation_requirement.value,
                    "text": f"The {system_type} validation plan shall verify ERTMS operational scenarios, degraded modes, interface assumptions, timing constraints within 1 second where safety relevant, and recorded pass/fail evidence.",
                    "hazard": "HZ-RAIL-ERTMS-001",
                    "safety_goal": "SG-RAIL-ERTMS-001",
                    "source": "ERTMS candidate reference: operational scenario validation, interfaces, degraded mode handling, and evidence review",
                },
            ]
        )
    if not templates:
        templates.extend(
            [
                {
                    "id": "REQ-SAFE-TRACE-001",
                    "type": RequirementType.safety_requirement.value,
                    "text": f"The {system_type} safety case shall trace each hazard to mitigations, measurable requirements, verification evidence, responsible owner, approval status, and residual risk decision.",
                    "hazard": "HZ-SAFE-001",
                    "safety_goal": "SG-SAFE-001",
                    "source": "Generic safety engineering candidate reference: hazard traceability and safety case evidence",
                },
                {
                    "id": "REQ-SAFE-VERIFY-001",
                    "type": RequirementType.validation_requirement.value,
                    "text": f"The {system_type} verification plan shall define objective pass/fail criteria, required evidence, test environment assumptions, and review gates for each safety-relevant requirement.",
                    "hazard": "HZ-SAFE-002",
                    "safety_goal": "SG-SAFE-002",
                    "source": "Generic safety engineering candidate reference: verification planning and acceptance criteria",
                },
            ]
        )

    requirements: list[Requirement] = []
    for template in templates:
        score, issues, improvement = score_requirement(template["text"], template["hazard"], template["safety_goal"])
        requirements.append(
            Requirement(
                id=template["id"],
                type=RequirementType(template["type"]),
                text=template["text"],
                linked_hazard=template["hazard"],
                linked_safety_goal=template["safety_goal"],
                quality_score=score.overall,
                quality_issues=issues,
                suggested_improvement=improvement if issues else f"Review project-specific thresholds and ODD assumptions for {domain}.",
                evidence_source=template["source"],
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
