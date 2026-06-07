"""Agent operations logging, approval gates, and run-level governance."""

from __future__ import annotations

from datetime import datetime
from statistics import mean
from typing import Any

from sqlmodel import Session, select

from backend.models import AgentRunLogRecord, IntegrationEventRecord, RequirementRecord, TestCaseRecord
from backend.retrieval_tools import search_project_docs
from backend.schemas import AgentApprovalUpdate, AgentOperationsDashboard, AgentRunLogCreate, IntegrationEventCreate


APPROVAL_REQUIRED_THRESHOLD = 0.7
ESCALATION_REQUIRED_THRESHOLD = 0.55
HIGH_HALLUCINATION_RISKS = {"high", "critical"}


def estimate_cost_usd(token_usage: dict[str, Any], input_per_million: float = 0.15, output_per_million: float = 0.60) -> float:
    """Estimate cost from token usage with conservative default rates."""
    input_tokens = int(token_usage.get("prompt_tokens") or token_usage.get("input_tokens") or 0)
    output_tokens = int(token_usage.get("completion_tokens") or token_usage.get("output_tokens") or 0)
    return round((input_tokens / 1_000_000 * input_per_million) + (output_tokens / 1_000_000 * output_per_million), 6)


def output_token_count(token_usage: dict[str, Any]) -> int:
    return int(token_usage.get("completion_tokens") or token_usage.get("output_tokens") or 0)


def infer_governance_flags(
    evaluation_score: float | None,
    failure_reason: str | None,
    confidence_score: float | None = None,
    hallucination_risk: str = "low",
) -> tuple[bool, bool, str | None]:
    if failure_reason:
        return True, True, failure_reason
    if confidence_score is not None and confidence_score < 0.75:
        return True, True, "Confidence score is below approval threshold."
    if hallucination_risk.lower() in HIGH_HALLUCINATION_RISKS:
        return True, True, "Hallucination risk requires human review."
    if evaluation_score is None:
        return False, False, None
    if evaluation_score < ESCALATION_REQUIRED_THRESHOLD:
        return True, True, "Evaluation score is below human escalation threshold."
    if evaluation_score < APPROVAL_REQUIRED_THRESHOLD:
        return True, False, None
    return False, False, None


def create_agent_run_log(project_id: int, payload: AgentRunLogCreate, session: Session) -> AgentRunLogRecord:
    approval_required, escalation_required, escalation_reason = infer_governance_flags(
        payload.evaluation_score,
        payload.failure_reason,
        payload.confidence_score,
        payload.hallucination_risk,
    )
    approval_required = payload.approval_required or approval_required
    escalation_required = payload.human_escalation_required or escalation_required
    approval_status = payload.approval_status or ("pending" if approval_required else "not_required")
    estimated_cost = payload.estimated_cost_usd or estimate_cost_usd(payload.token_usage)
    record = AgentRunLogRecord(
        project_id=project_id,
        evaluation_run_id=payload.evaluation_run_id,
        operation_name=payload.operation_name,
        agent_name=payload.agent_name,
        status=payload.status,
        model_used=payload.model_used,
        model_version=payload.model_version,
        prompt_version=payload.prompt_version,
        prompt_template_id=payload.prompt_template_id,
        tool_config_version=payload.tool_config_version,
        user_request=payload.user_request,
        input_summary=payload.input_summary,
        output_summary=payload.output_summary,
        tools_used=payload.tools_used,
        retrieved_docs=payload.retrieved_docs,
        latency_ms=payload.latency_ms,
        token_usage=payload.token_usage,
        estimated_cost_usd=estimated_cost,
        failure_reason=payload.failure_reason,
        failure_stage=payload.failure_stage,
        human_escalation_required=escalation_required,
        escalation_reason=payload.escalation_reason or escalation_reason,
        approval_required=approval_required,
        approval_status=approval_status,
        approved_by=payload.approved_by,
        approval_notes=payload.approval_notes,
        confidence_score=payload.confidence_score,
        hallucination_risk=payload.hallucination_risk,
        hallucination_flags=payload.hallucination_flags,
        evaluation_score=payload.evaluation_score,
        run_metadata=payload.metadata,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def create_integration_event(project_id: int, payload: IntegrationEventCreate, session: Session) -> IntegrationEventRecord:
    prefix = {
        "github_issue": "GH",
        "jira_ticket": "JIRA",
        "crm_update": "CRM",
        "slack_notification": "SLACK",
    }.get(payload.integration_type, "EXT")
    count = len(session.exec(select(IntegrationEventRecord).where(IntegrationEventRecord.project_id == project_id)).all()) + 1
    record = IntegrationEventRecord(
        project_id=project_id,
        agent_run_id=payload.agent_run_id,
        integration_type=payload.integration_type,
        external_id=f"{prefix}-{project_id}-{count:04d}",
        title=payload.title,
        description=payload.description,
        payload=payload.payload,
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def build_operations_dashboard(project_id: int, session: Session, source_system: str | None = None) -> AgentOperationsDashboard:
    runs = session.exec(select(AgentRunLogRecord).where(AgentRunLogRecord.project_id == project_id)).all()
    if source_system:
        runs = [run for run in runs if (run.run_metadata or {}).get("source_system") == source_system]
    total = len(runs)
    if not runs:
        return AgentOperationsDashboard(
            project_id=project_id,
            total_runs=0,
            success_rate=0.0,
            escalation_rate=0.0,
            average_latency_ms=0.0,
            average_cost_usd=0.0,
            total_cost_usd=0.0,
            average_output_tokens=0.0,
            total_output_tokens=0,
            approval_pending_count=0,
            hallucination_flags={},
            average_evaluation_score=None,
        )
    success_count = sum(1 for run in runs if run.status in {"resolved", "completed", "success"})
    escalation_count = sum(1 for run in runs if run.human_escalation_required)
    costs = [run.estimated_cost_usd for run in runs]
    latencies = [run.latency_ms for run in runs]
    output_tokens = [output_token_count(run.token_usage) for run in runs]
    scores = [run.evaluation_score for run in runs if run.evaluation_score is not None]
    flags: dict[str, int] = {}
    for run in runs:
        for flag in run.hallucination_flags:
            flags[flag] = flags.get(flag, 0) + 1
    return AgentOperationsDashboard(
        project_id=project_id,
        total_runs=total,
        success_rate=round(success_count / total, 3),
        escalation_rate=round(escalation_count / total, 3),
        average_latency_ms=round(mean(latencies), 2),
        average_cost_usd=round(mean(costs), 6),
        total_cost_usd=round(sum(costs), 6),
        average_output_tokens=round(mean(output_tokens), 2),
        total_output_tokens=sum(output_tokens),
        approval_pending_count=sum(1 for run in runs if run.approval_status == "pending"),
        hallucination_flags=flags,
        average_evaluation_score=round(mean(scores), 3) if scores else None,
    )


def run_mock_tool(tool_name: str, project_id: int, user_request: str, session: Session) -> Any:
    if tool_name == "search_project_docs":
        return {
            "query": user_request,
            "retrieved_docs": [
                result.model_dump(mode="json")
                for result in search_project_docs(project_id, user_request, top_k=5)
            ],
        }
    if tool_name == "extract_requirements":
        count = len(session.exec(select(RequirementRecord).where(RequirementRecord.project_id == project_id)).all())
        return {"requirements_found": count}
    if tool_name == "evaluate_requirements":
        records = session.exec(select(RequirementRecord).where(RequirementRecord.project_id == project_id)).all()
        average = round(mean([record.quality_score for record in records]), 3) if records else 0.0
        return {"requirement_count": len(records), "average_quality_score": average}
    if tool_name == "generate_traceability":
        records = session.exec(select(RequirementRecord).where(RequirementRecord.project_id == project_id)).all()
        return {"traceability_rows": len(records)}
    if tool_name == "generate_test_cases":
        records = session.exec(select(TestCaseRecord).where(TestCaseRecord.project_id == project_id)).all()
        return {"test_cases": len(records)}
    if tool_name == "create_issue_ticket":
        event = create_integration_event(
            project_id,
            IntegrationEventCreate(
                integration_type="jira_ticket",
                title="Agent follow-up ticket",
                description=user_request,
                payload={"source": "tool_orchestration"},
            ),
            session,
        )
        return {"ticket_id": event.external_id, "status": event.status}
    return {"error": f"Unknown tool: {tool_name}"}


def update_approval(record: AgentRunLogRecord, payload: AgentApprovalUpdate, session: Session) -> AgentRunLogRecord:
    record.approval_status = payload.approval_status
    record.approved_by = payload.approved_by
    record.approval_notes = payload.approval_notes
    if payload.human_escalation_required is not None:
        record.human_escalation_required = payload.human_escalation_required
    if payload.escalation_reason is not None:
        record.escalation_reason = payload.escalation_reason
    record.updated_at = datetime.utcnow()
    session.add(record)
    session.commit()
    session.refresh(record)
    return record
