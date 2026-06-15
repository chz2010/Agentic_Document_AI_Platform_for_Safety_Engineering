"""Optional MLflow tracking for Project 2 evaluation and AgentOps runs."""

from __future__ import annotations

from typing import Any

from backend.models import AgentRunLogRecord, EvaluationRunRecord, Project
from backend.settings import settings

try:
    import mlflow
except Exception:  # pragma: no cover - exercised when optional dependency is absent
    mlflow = None


def mlflow_status() -> dict[str, Any]:
    available = mlflow is not None
    return {
        "enabled": settings.mlflow_tracking_enabled,
        "available": available,
        "tracking_uri": settings.mlflow_tracking_uri,
        "experiment_name": settings.mlflow_experiment_name,
        "status": "enabled" if settings.mlflow_tracking_enabled and available else "disabled",
        "message": _disabled_reason(available),
    }


def log_evaluation_run(record: EvaluationRunRecord, project: Project | None = None) -> None:
    if not _tracking_ready():
        return
    try:
        _configure_mlflow()
        with mlflow.start_run(run_name=f"eval:{record.run_type}:{record.id}", nested=False):
            _set_project_tags(project, record.project_id)
            mlflow.set_tags(
                {
                    "project2.run_kind": "evaluation",
                    "project2.run_type": record.run_type,
                    "project2.evaluation_run_id": str(record.id),
                    "model.used": record.model_used,
                }
            )
            mlflow.log_params(
                _compact_params(
                    {
                        "run_type": record.run_type,
                        "model_used": record.model_used,
                        "retrieved_chunk_count": record.retrieved_chunk_count,
                    }
                )
            )
            mlflow.log_metrics(
                _compact_metrics(
                    {
                        "quality_score": record.quality_score,
                        "latency_ms": record.latency_ms,
                        "retrieved_chunk_count": record.retrieved_chunk_count,
                        "prompt_tokens": _token_value(record.token_usage, "prompt_tokens", "input_tokens"),
                        "completion_tokens": _token_value(record.token_usage, "completion_tokens", "output_tokens"),
                        "missing_sections": len(record.missing_sections or []),
                        "hallucination_flags": len(record.hallucination_flags or []),
                        "requirement_count": (record.requirement_quality_summary or {}).get("count"),
                        "average_requirement_quality": (record.requirement_quality_summary or {}).get("average_quality_score"),
                    }
                )
            )
            _log_dict_artifact(
                {
                    "query": record.query,
                    "answer": record.answer,
                    "token_usage": record.token_usage,
                    "missing_sections": record.missing_sections,
                    "hallucination_flags": record.hallucination_flags,
                    "requirement_quality_summary": record.requirement_quality_summary,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                },
                "evaluation_payload.json",
            )
    except Exception:
        return


def log_agent_run(record: AgentRunLogRecord, project: Project | None = None) -> None:
    if not _tracking_ready():
        return
    try:
        _configure_mlflow()
        with mlflow.start_run(run_name=f"agent:{record.operation_name}:{record.id}", nested=False):
            _set_project_tags(project, record.project_id)
            mlflow.set_tags(
                {
                    "project2.run_kind": "agent_ops",
                    "project2.agent_run_id": str(record.id),
                    "project2.operation_name": record.operation_name,
                    "project2.agent_name": record.agent_name,
                    "project2.status": record.status,
                    "project2.approval_status": record.approval_status,
                    "model.used": record.model_used,
                }
            )
            mlflow.log_params(
                _compact_params(
                    {
                        "operation_name": record.operation_name,
                        "agent_name": record.agent_name,
                        "status": record.status,
                        "model_used": record.model_used,
                        "model_version": record.model_version,
                        "prompt_version": record.prompt_version,
                        "prompt_template_id": record.prompt_template_id,
                        "tool_config_version": record.tool_config_version,
                        "tools_used": ",".join(record.tools_used or []),
                        "hallucination_risk": record.hallucination_risk,
                    }
                )
            )
            mlflow.log_metrics(
                _compact_metrics(
                    {
                        "latency_ms": record.latency_ms,
                        "estimated_cost_usd": record.estimated_cost_usd,
                        "confidence_score": record.confidence_score,
                        "evaluation_score": record.evaluation_score,
                        "approval_required": int(record.approval_required),
                        "human_escalation_required": int(record.human_escalation_required),
                        "retrieved_docs": len(record.retrieved_docs or []),
                        "tools_used": len(record.tools_used or []),
                        "prompt_tokens": _token_value(record.token_usage, "prompt_tokens", "input_tokens"),
                        "completion_tokens": _token_value(record.token_usage, "completion_tokens", "output_tokens"),
                    }
                )
            )
            _log_dict_artifact(
                {
                    "user_request": record.user_request,
                    "input_summary": record.input_summary,
                    "output_summary": record.output_summary,
                    "retrieved_docs": record.retrieved_docs,
                    "token_usage": record.token_usage,
                    "failure_reason": record.failure_reason,
                    "failure_stage": record.failure_stage,
                    "escalation_reason": record.escalation_reason,
                    "hallucination_flags": record.hallucination_flags,
                    "metadata": record.run_metadata,
                    "created_at": record.created_at.isoformat() if record.created_at else None,
                },
                "agent_run_payload.json",
            )
    except Exception:
        return


def _tracking_ready() -> bool:
    return settings.mlflow_tracking_enabled and mlflow is not None


def _disabled_reason(available: bool) -> str:
    if not settings.mlflow_tracking_enabled:
        return "Set MLFLOW_TRACKING_ENABLED=true to mirror runs into MLflow."
    if not available:
        return "Install the mlflow package to enable tracking."
    return "MLflow tracking is ready."


def _configure_mlflow() -> None:
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)


def _set_project_tags(project: Project | None, project_id: int) -> None:
    tags = {"project2.project_id": str(project_id)}
    if project:
        tags.update(
            {
                "project2.project_name": project.name,
                "project2.domain": project.domain,
                "project2.system_type": project.system_type,
            }
        )
    mlflow.set_tags(tags)


def _compact_params(values: dict[str, Any]) -> dict[str, str]:
    return {key: str(value)[:250] for key, value in values.items() if value is not None and value != ""}


def _compact_metrics(values: dict[str, Any]) -> dict[str, float]:
    metrics: dict[str, float] = {}
    for key, value in values.items():
        if value is None:
            continue
        try:
            metrics[key] = float(value)
        except (TypeError, ValueError):
            continue
    return metrics


def _token_value(token_usage: dict[str, Any], primary: str, fallback: str) -> int:
    return int(token_usage.get(primary) or token_usage.get(fallback) or 0)


def _log_dict_artifact(payload: dict[str, Any], artifact_file: str) -> None:
    if hasattr(mlflow, "log_dict"):
        mlflow.log_dict(payload, artifact_file)
