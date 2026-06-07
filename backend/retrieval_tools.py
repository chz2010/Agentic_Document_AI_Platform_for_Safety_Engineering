"""Multi-source retrieval tools for project documents and structured records."""

from __future__ import annotations

import re
from typing import Any

from sqlmodel import Session, select

from backend.models import AgentRunLogRecord, EvaluationRunRecord, RequirementRecord, TestCaseRecord
from backend.requirements_engineering import build_traceability
from backend.schemas import Requirement, RetrievalResult
from backend.settings import settings
from backend.vector_store import get_project_vector_store


SUPPORTED_RETRIEVAL_TOOLS = {
    "project_docs",
    "requirements",
    "traceability",
    "test_cases",
    "evaluation_runs",
    "agent_runs",
}


def run_retrieval_tool(tool_name: str, project_id: int, query: str, top_k: int, session: Session) -> list[RetrievalResult]:
    if tool_name == "project_docs":
        return search_project_docs(project_id, query, top_k)
    if tool_name == "requirements":
        return search_requirements(project_id, query, top_k, session)
    if tool_name == "traceability":
        return search_traceability(project_id, query, top_k, session)
    if tool_name == "test_cases":
        return search_test_cases(project_id, query, top_k, session)
    if tool_name == "evaluation_runs":
        return search_evaluation_runs(project_id, query, top_k, session)
    if tool_name == "agent_runs":
        return search_agent_runs(project_id, query, top_k, session)
    return []


def search_project_docs(project_id: int, query: str, top_k: int) -> list[RetrievalResult]:
    docs = get_project_vector_store().similarity_search(
        query,
        k=min(top_k, settings.retrieval_k),
        filter={"project_id": str(project_id)},
    )
    results: list[RetrievalResult] = []
    for doc in docs:
        results.append(
            RetrievalResult(
                source="project_docs",
                title=doc.metadata.get("document", "Project document"),
                snippet=_snippet(doc.page_content),
                score=_lexical_score(query, doc.page_content),
                metadata={
                    "chunk_id": doc.metadata.get("chunk_id"),
                    "document_id": doc.metadata.get("document_id"),
                    "page": doc.metadata.get("page"),
                    "section": doc.metadata.get("section"),
                    "source_type": doc.metadata.get("source_type"),
                },
            )
        )
    return results


def search_requirements(project_id: int, query: str, top_k: int, session: Session) -> list[RetrievalResult]:
    records = session.exec(select(RequirementRecord).where(RequirementRecord.project_id == project_id)).all()
    results = [
        RetrievalResult(
            source="requirements",
            title=record.requirement_id,
            snippet=_snippet(record.text),
            score=_lexical_score(query, " ".join([
                record.requirement_id,
                record.requirement_type,
                record.text,
                record.linked_hazard or "",
                record.linked_safety_goal or "",
                " ".join(record.quality_issues),
            ])),
            metadata={
                "requirement_type": record.requirement_type,
                "linked_hazard": record.linked_hazard,
                "linked_safety_goal": record.linked_safety_goal,
                "quality_score": record.quality_score,
                "quality_issues": record.quality_issues,
                "evidence_source": record.evidence_source,
            },
        )
        for record in records
    ]
    return _ranked(results, top_k)


def search_traceability(project_id: int, query: str, top_k: int, session: Session) -> list[RetrievalResult]:
    requirements = [
        Requirement(
            id=record.requirement_id,
            type=record.requirement_type,
            text=record.text,
            linked_hazard=record.linked_hazard,
            linked_safety_goal=record.linked_safety_goal,
            quality_score=record.quality_score,
            quality_issues=record.quality_issues,
            suggested_improvement=record.suggested_improvement,
            linked_test_cases=record.linked_test_cases,
            evidence_source=record.evidence_source,
        )
        for record in session.exec(select(RequirementRecord).where(RequirementRecord.project_id == project_id)).all()
    ]
    results: list[RetrievalResult] = []
    for row in build_traceability(requirements):
        haystack = " ".join([
            row.hazard_id or "",
            row.safety_goal_id or "",
            row.requirement_id,
            row.requirement_type.value,
            row.test_case_id or "",
            row.requirement_text,
            row.status,
        ])
        results.append(
            RetrievalResult(
                source="traceability",
                title=f"{row.hazard_id or 'No hazard'} -> {row.requirement_id}",
                snippet=_snippet(row.requirement_text),
                score=_lexical_score(query, haystack),
                metadata=row.model_dump(mode="json"),
            )
        )
    return _ranked(results, top_k)


def search_test_cases(project_id: int, query: str, top_k: int, session: Session) -> list[RetrievalResult]:
    records = session.exec(select(TestCaseRecord).where(TestCaseRecord.project_id == project_id)).all()
    results: list[RetrievalResult] = []
    for record in records:
        payload = record.payload or {}
        haystack = _flatten(payload)
        results.append(
            RetrievalResult(
                source="test_cases",
                title=record.test_case_id,
                snippet=_snippet(haystack),
                score=_lexical_score(query, haystack),
                metadata=payload,
            )
        )
    return _ranked(results, top_k)


def search_evaluation_runs(project_id: int, query: str, top_k: int, session: Session) -> list[RetrievalResult]:
    records = session.exec(select(EvaluationRunRecord).where(EvaluationRunRecord.project_id == project_id)).all()
    results: list[RetrievalResult] = []
    for record in records:
        haystack = " ".join([
            record.run_type,
            record.model_used,
            record.query or "",
            record.answer or "",
            _flatten(record.missing_sections),
            _flatten(record.hallucination_flags),
            _flatten(record.requirement_quality_summary),
        ])
        results.append(
            RetrievalResult(
                source="evaluation_runs",
                title=f"Evaluation run {record.id}: {record.run_type}",
                snippet=_snippet(haystack),
                score=_lexical_score(query, haystack),
                metadata={
                    "id": record.id,
                    "run_type": record.run_type,
                    "model_used": record.model_used,
                    "quality_score": record.quality_score,
                    "retrieved_chunk_count": record.retrieved_chunk_count,
                    "latency_ms": record.latency_ms,
                    "created_at": record.created_at.isoformat(),
                },
            )
        )
    return _ranked(results, top_k)


def search_agent_runs(project_id: int, query: str, top_k: int, session: Session) -> list[RetrievalResult]:
    records = session.exec(select(AgentRunLogRecord).where(AgentRunLogRecord.project_id == project_id)).all()
    results: list[RetrievalResult] = []
    for record in records:
        haystack = " ".join([
            str(record.id),
            record.operation_name,
            record.agent_name,
            record.status,
            record.model_used,
            record.user_request or "",
            record.input_summary or "",
            record.output_summary or "",
            record.failure_reason or "",
            record.escalation_reason or "",
            _flatten(record.tools_used),
            _flatten(record.hallucination_flags),
        ])
        results.append(
            RetrievalResult(
                source="agent_runs",
                title=f"Agent run {record.id}: {record.operation_name}",
                snippet=_snippet(haystack),
                score=_lexical_score(query, haystack),
                metadata={
                    "id": record.id,
                    "status": record.status,
                    "approval_required": record.approval_required,
                    "approval_status": record.approval_status,
                    "human_escalation_required": record.human_escalation_required,
                    "evaluation_score": record.evaluation_score,
                    "estimated_cost_usd": record.estimated_cost_usd,
                    "created_at": record.created_at.isoformat(),
                },
            )
        )
    return _ranked(results, top_k)


def _ranked(results: list[RetrievalResult], top_k: int) -> list[RetrievalResult]:
    return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]


def _lexical_score(query: str, text: str) -> float:
    query_tokens = set(_tokens(query))
    if not query_tokens:
        return 0.0
    text_tokens = _tokens(text)
    if not text_tokens:
        return 0.0
    text_set = set(text_tokens)
    overlap = query_tokens & text_set
    coverage = len(overlap) / len(query_tokens)
    frequency = sum(text_tokens.count(token) for token in overlap) / max(len(text_tokens), 1)
    return round(min(1.0, coverage * 0.85 + frequency * 0.15), 4)


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _snippet(text: str, limit: int = 480) -> str:
    compact = " ".join(str(text).split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def _flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(f"{key}: {_flatten(item)}" for key, item in value.items())
    if isinstance(value, list):
        return " ".join(_flatten(item) for item in value)
    return str(value)
