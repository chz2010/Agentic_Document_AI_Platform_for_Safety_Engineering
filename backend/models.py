"""Relational persistence models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    domain: str
    system_type: str
    standards_scope: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    description: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectDocument(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    filename: str
    source_type: str
    storage_path: str
    chunk_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentChunk(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    document_id: int = Field(index=True, foreign_key="projectdocument.id")
    chunk_id: str = Field(index=True, unique=True)
    page: int | None = None
    section: str | None = None
    text_preview: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RequirementRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    requirement_id: str = Field(index=True)
    requirement_type: str
    text: str
    linked_hazard: str | None = None
    linked_safety_goal: str | None = None
    quality_score: float = 0.0
    quality_issues: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    suggested_improvement: str | None = None
    linked_test_cases: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    evidence_source: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TestCaseRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    test_case_id: str = Field(index=True)
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EvaluationRunRecord(SQLModel, table=True):
    model_config = ConfigDict(protected_namespaces=())

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    run_type: str
    model_used: str
    query: str | None = None
    answer: str | None = None
    retrieved_chunk_count: int = 0
    latency_ms: int = 0
    token_usage: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    quality_score: float | None = None
    missing_sections: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    hallucination_flags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    requirement_quality_summary: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentRunLogRecord(SQLModel, table=True):
    model_config = ConfigDict(protected_namespaces=())

    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    evaluation_run_id: int | None = Field(default=None, index=True, foreign_key="evaluationrunrecord.id")
    operation_name: str = Field(index=True)
    agent_name: str = "safety_analysis_agent"
    status: str = Field(default="completed", index=True)
    model_used: str
    model_version: str | None = None
    prompt_version: str = Field(default="v1", index=True)
    prompt_template_id: str | None = None
    tool_config_version: str = Field(default="tools-v1", index=True)
    user_request: str | None = None
    input_summary: str | None = None
    output_summary: str | None = None
    tools_used: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    retrieved_docs: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    latency_ms: int = 0
    token_usage: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    estimated_cost_usd: float = 0.0
    failure_reason: str | None = None
    failure_stage: str | None = None
    human_escalation_required: bool = Field(default=False, index=True)
    escalation_reason: str | None = None
    approval_required: bool = Field(default=False, index=True)
    approval_status: str = Field(default="not_required", index=True)
    approved_by: str | None = None
    approval_notes: str | None = None
    confidence_score: float | None = None
    hallucination_risk: str = Field(default="low", index=True)
    hallucination_flags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    evaluation_score: float | None = None
    run_metadata: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IntegrationEventRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    agent_run_id: int | None = Field(default=None, index=True, foreign_key="agentrunlogrecord.id")
    integration_type: str = Field(index=True)
    external_id: str = Field(index=True)
    title: str
    description: str | None = None
    status: str = Field(default="created", index=True)
    payload: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowItemRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(index=True, foreign_key="project.id")
    title: str
    description: str | None = None
    source_system: str = Field(default="autonomous_driving_safety_analyst", index=True)
    workflow_stage: str = Field(default="intake", index=True)
    status: str = Field(default="open", index=True)
    priority: str = Field(default="medium", index=True)
    owner: str | None = None
    due_date: datetime | None = None
    linked_requirement_id: str | None = Field(default=None, index=True)
    linked_hazard_id: str | None = Field(default=None, index=True)
    linked_safety_goal_id: str | None = Field(default=None, index=True)
    linked_agent_run_id: int | None = Field(default=None, index=True, foreign_key="agentrunlogrecord.id")
    linked_evaluation_run_id: int | None = Field(default=None, index=True, foreign_key="evaluationrunrecord.id")
    evidence_refs: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    acceptance_criteria: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    notes: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
