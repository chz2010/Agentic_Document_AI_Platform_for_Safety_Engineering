"""Precision tools for routing, reranking, citations, and review queues."""

from __future__ import annotations

import re
from statistics import mean

from sqlmodel import Session, select

from backend.models import AgentRunLogRecord, RequirementRecord
from backend.retrieval_tools import SUPPORTED_RETRIEVAL_TOOLS, run_retrieval_tool
from backend.schemas import (
    EvidenceCitation,
    HumanReviewItem,
    PrecisionReviewResponse,
    RequirementCompletenessItem,
    RetrievalResult,
    StandardReference,
)


ISO_REFERENCE_RULES = [
    {
        "keywords": {"hazard", "hara", "asil", "severity", "exposure", "controllability"},
        "references": [
            ("ISO 26262-3:2018", "Clause 6", "Hazard analysis and risk assessment"),
        ],
    },
    {
        "keywords": {"safety goal", "functional safety concept", "safe state"},
        "references": [
            ("ISO 26262-3:2018", "Clause 7", "Functional safety concept"),
        ],
    },
    {
        "keywords": {"technical safety", "system", "architecture", "safety requirement"},
        "references": [
            ("ISO 26262-4:2018", "Clause 6", "Technical safety concept"),
            ("ISO 26262-4:2018", "Clause 7", "System architectural design"),
        ],
    },
    {
        "keywords": {"software", "software safety", "implementation", "unit", "integration"},
        "references": [
            ("ISO 26262-6:2018", "Clause 6", "Software safety requirements specification"),
            ("ISO 26262-6:2018", "Clause 9", "Software unit verification"),
        ],
    },
    {
        "keywords": {"validation", "verify", "test", "evidence", "pass", "scenario"},
        "references": [
            ("ISO 26262-4:2018", "Clause 9", "Safety validation"),
            ("ISO 26262-6:2018", "Clause 11", "Testing of embedded software"),
        ],
    },
    {
        "keywords": {"sotif", "misuse", "unknown unsafe", "triggering condition", "performance limitation"},
        "references": [
            ("ISO 21448:2022", "Clause 6", "SOTIF specification and design considerations"),
            ("ISO 21448:2022", "Clause 7", "Evaluation of triggering conditions"),
        ],
    },
    {
        "keywords": {"dataset", "ai", "model", "training", "monitoring", "confidence", "perception"},
        "references": [
            ("ISO 8800", "AI safety lifecycle clause area", "AI safety assurance, data, validation, and monitoring"),
        ],
    },
    {
        "keywords": {"rams", "railway", "hazard log", "lifecycle", "residual risk", "acceptance criteria"},
        "references": [
            ("IEC 62278 / EN 50126", "RAMS lifecycle clause area", "Railway RAMS process, hazard analysis, and risk acceptance"),
        ],
    },
    {
        "keywords": {"software", "sil", "railway software", "verification", "validation", "change impact"},
        "references": [
            ("EN 50128", "Software lifecycle clause area", "Railway software safety integrity, verification, validation, and change control"),
        ],
    },
    {
        "keywords": {"safety case", "approval", "authorization", "evidence", "argument"},
        "references": [
            ("EN 50129 / IEC 62425", "Safety case clause area", "Railway safety case evidence, approval, and structured safety argument"),
        ],
    },
    {
        "keywords": {"ertms", "etcs", "degraded mode", "interface", "operational scenario", "train control"},
        "references": [
            ("ERTMS", "Operational scenario clause area", "ERTMS operational scenarios, interfaces, degraded modes, and validation evidence"),
        ],
    },
]


def build_precision_review(
    project_id: int,
    query: str,
    requested_tools: list[str] | None,
    top_k: int,
    standards: list[str],
    session: Session,
) -> PrecisionReviewResponse:
    tools = requested_tools or route_query(query)
    tools = [tool for tool in tools if tool in SUPPORTED_RETRIEVAL_TOOLS]
    if not tools:
        tools = route_query(query)

    results_by_tool = {
        tool: run_retrieval_tool(tool, project_id, query, top_k, session)
        for tool in tools
    }
    reranked = rerank_evidence(query, results_by_tool)
    requirements = session.exec(select(RequirementRecord).where(RequirementRecord.project_id == project_id)).all()
    completeness = check_requirement_completeness(requirements, standards)
    citations = build_citations(reranked[:top_k], standards)
    human_review_queue = build_human_review_queue(project_id, completeness, reranked, session)
    iso_references = map_iso_references(query + " " + " ".join(result.snippet for result in reranked[:top_k]), standards)
    confidence, rationale = score_answer_confidence(reranked, completeness, human_review_queue)

    return PrecisionReviewResponse(
        query=query,
        routed_tools=tools,
        reranked_evidence=reranked[:top_k],
        citations=citations,
        compressed_context=compress_context(reranked[:top_k]),
        requirement_completeness=completeness,
        human_review_queue=human_review_queue,
        iso_references=iso_references,
        confidence_score=confidence,
        confidence_rationale=rationale,
    )


def route_query(query: str) -> list[str]:
    lower = query.lower()
    tools: list[str] = []
    if any(term in lower for term in ["document", "evidence", "source", "uploaded", "pdf", "section"]):
        tools.append("project_docs")
    if any(term in lower for term in ["iso", "clause", "standard", "supported", "support", "compliance"]):
        tools.extend(["project_docs", "requirements", "traceability", "test_cases"])
    if any(term in lower for term in ["requirement", "shall", "quality", "gap", "missing", "complete"]):
        tools.extend(["requirements", "traceability"])
    if any(term in lower for term in ["hazard", "safety goal", "trace", "traceability", "link"]):
        tools.append("traceability")
    if any(term in lower for term in ["test", "scenario", "verification", "validation"]):
        tools.append("test_cases")
    if any(term in lower for term in ["evaluation", "run", "history", "quality score"]):
        tools.append("evaluation_runs")
    if any(term in lower for term in ["agent", "approval", "cost", "latency", "failure", "escalation"]):
        tools.append("agent_runs")
    if not tools:
        tools = ["project_docs", "requirements", "traceability"]
    return list(dict.fromkeys(tools))


def rerank_evidence(query: str, results_by_tool: dict[str, list[RetrievalResult]]) -> list[RetrievalResult]:
    reranked: list[RetrievalResult] = []
    query_ids = set(re.findall(r"\b(?:REQ|HZ|SG|TC)[-_A-Z0-9]*\d+\b", query.upper()))
    for tool, results in results_by_tool.items():
        for result in results:
            boost = 0.0
            haystack = f"{result.title} {result.snippet} {result.metadata}".upper()
            if query_ids and any(identifier in haystack for identifier in query_ids):
                boost += 0.25
            if tool in {"requirements", "traceability"}:
                boost += 0.08
            if tool == "project_docs" and result.metadata.get("chunk_id"):
                boost += 0.06
            if tool in {"evaluation_runs", "agent_runs"} and any(term in query.lower() for term in ["run", "failure", "cost", "latency"]):
                boost += 0.12
            result.score = round(min(1.0, result.score + boost), 4)
            reranked.append(result)
    return sorted(reranked, key=lambda item: item.score, reverse=True)


def check_requirement_completeness(records: list[RequirementRecord], standards: list[str]) -> list[RequirementCompletenessItem]:
    items: list[RequirementCompletenessItem] = []
    for record in records:
        missing: list[str] = []
        lower = record.text.lower()
        if not re.search(r"\b\d+(\.\d+)?\s?(ms|s|m|km/h|%|deg|lux|hz|seconds|meters)\b", lower):
            missing.append("measurable threshold")
        if not any(term in lower for term in ["odd", "night", "rain", "fog", "occlusion", "speed", "lighting", "road"]):
            missing.append("ODD condition")
        if not any(term in lower for term in ["test", "verify", "validate", "measure", "evidence", "pass"]):
            missing.append("verification method")
        if not record.linked_hazard:
            missing.append("linked hazard")
        if not record.linked_safety_goal:
            missing.append("linked safety goal")
        if not record.evidence_source:
            missing.append("evidence source")
        if not record.linked_test_cases:
            missing.append("linked test case")
        items.append(
            RequirementCompletenessItem(
                requirement_id=record.requirement_id,
                quality_score=record.quality_score,
                missing_fields=missing,
                issues=record.quality_issues,
                iso_references=map_iso_references(record.text, standards),
            )
        )
    return items


def build_citations(results: list[RetrievalResult], standards: list[str]) -> list[EvidenceCitation]:
    citations: list[EvidenceCitation] = []
    for result in results:
        metadata = result.metadata
        if result.source == "project_docs":
            citation = f"{result.title}"
            if metadata.get("page"):
                citation += f", page {metadata['page']}"
            if metadata.get("section"):
                citation += f", section {metadata['section']}"
            if metadata.get("chunk_id"):
                citation += f", chunk {metadata['chunk_id']}"
        elif result.source == "requirements":
            citation = f"Requirement {result.title}"
        elif result.source == "traceability":
            citation = f"Traceability row {metadata.get('requirement_id', result.title)}"
        elif result.source == "test_cases":
            citation = f"Test case {result.title}"
        elif result.source == "evaluation_runs":
            citation = f"Evaluation run {metadata.get('id', result.title)}"
        else:
            citation = f"Agent run {metadata.get('id', result.title)}"
        citations.append(
            EvidenceCitation(
                source=result.source,
                title=result.title,
                citation=citation,
                snippet=result.snippet,
                score=result.score,
                iso_references=map_iso_references(result.snippet + " " + result.title, standards),
            )
        )
    return citations


def build_human_review_queue(
    project_id: int,
    completeness: list[RequirementCompletenessItem],
    reranked: list[RetrievalResult],
    session: Session,
) -> list[HumanReviewItem]:
    items: list[HumanReviewItem] = []
    for item in completeness:
        if item.missing_fields or item.quality_score < 0.75:
            severity = "high" if len(item.missing_fields) >= 3 or item.quality_score < 0.65 else "medium"
            items.append(
                HumanReviewItem(
                    item_type="requirement",
                    item_id=item.requirement_id,
                    reason=", ".join(item.missing_fields or item.issues),
                    severity=severity,
                    suggested_action="Add missing traceability, measurable thresholds, ODD conditions, and verification evidence.",
                )
            )
    if not reranked:
        items.append(
            HumanReviewItem(
                item_type="retrieval",
                item_id=f"project-{project_id}",
                reason="No evidence was retrieved for the query.",
                severity="high",
                suggested_action="Upload relevant documents or broaden the query.",
            )
        )
    failed_runs = session.exec(
        select(AgentRunLogRecord).where(
            AgentRunLogRecord.project_id == project_id,
            AgentRunLogRecord.human_escalation_required == True,  # noqa: E712
        )
    ).all()
    for run in failed_runs[:5]:
        items.append(
            HumanReviewItem(
                item_type="agent_run",
                item_id=str(run.id),
                reason=run.escalation_reason or run.failure_reason or "Agent run requires human review.",
                severity="medium",
                suggested_action="Review the run log, approval status, evidence, and retry plan.",
            )
        )
    return items


def score_answer_confidence(
    reranked: list[RetrievalResult],
    completeness: list[RequirementCompletenessItem],
    human_review_queue: list[HumanReviewItem],
) -> tuple[float, str]:
    if not reranked:
        return 0.2, "No retrieved evidence was available."
    evidence_score = mean(result.score for result in reranked[:5])
    completeness_penalty = 0.0
    if completeness:
        incomplete_ratio = sum(1 for item in completeness if item.missing_fields) / len(completeness)
        completeness_penalty = incomplete_ratio * 0.25
    review_penalty = min(0.2, 0.04 * len(human_review_queue))
    confidence = round(max(0.0, min(1.0, evidence_score - completeness_penalty - review_penalty + 0.15)), 2)
    rationale = (
        f"Evidence relevance average={evidence_score:.2f}; "
        f"completeness penalty={completeness_penalty:.2f}; "
        f"human review penalty={review_penalty:.2f}."
    )
    return confidence, rationale


def compress_context(results: list[RetrievalResult]) -> list[str]:
    return [
        f"{idx}. [{result.source}] {result.title}: {result.snippet}"
        for idx, result in enumerate(results, start=1)
    ]


def map_iso_references(text: str, standards: list[str]) -> list[StandardReference]:
    lower = text.lower()
    requested = " ".join(standards).lower()
    references: list[StandardReference] = []
    for rule in ISO_REFERENCE_RULES:
        matches = [keyword for keyword in rule["keywords"] if keyword in lower]
        if not matches:
            continue
        for standard, clause, topic in rule["references"]:
            if "iso 26262" in standard.lower() and "26262" not in requested:
                continue
            if "iso 21448" in standard.lower() and "21448" not in requested and "sotif" not in requested:
                continue
            if "iso 8800" in standard.lower() and "8800" not in requested:
                continue
            if "50126" in standard.lower() and "50126" not in requested and "62278" not in requested and "rail" not in requested:
                continue
            if "50128" in standard.lower() and "50128" not in requested and "rail" not in requested:
                continue
            if ("50129" in standard.lower() or "62425" in standard.lower()) and not any(term in requested for term in ["50129", "62425", "rail"]):
                continue
            if "ertms" in standard.lower() and "ertms" not in requested and "rail" not in requested:
                continue
            references.append(
                StandardReference(
                    standard=standard,
                    clause=clause,
                    topic=topic,
                    rationale=f"Matched terms: {', '.join(sorted(matches))}",
                    confidence=round(min(0.95, 0.55 + 0.1 * len(matches)), 2),
                )
            )
    unique: dict[tuple[str, str, str], StandardReference] = {}
    for reference in references:
        unique[(reference.standard, reference.clause, reference.topic)] = reference
    return list(unique.values())[:8]
