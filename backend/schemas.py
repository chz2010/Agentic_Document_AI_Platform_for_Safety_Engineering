"""Pydantic API contracts and structured AI outputs."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RequirementType(str, Enum):
    functional_requirement = "functional_requirement"
    safety_requirement = "safety_requirement"
    functional_safety_requirement = "functional_safety_requirement"
    technical_safety_requirement = "technical_safety_requirement"
    software_requirement = "software_requirement"
    hardware_requirement = "hardware_requirement"
    validation_requirement = "validation_requirement"
    monitoring_requirement = "monitoring_requirement"
    dataset_requirement = "dataset_requirement"


class ProjectCreate(BaseModel):
    name: str
    domain: str = "Autonomous driving"
    system_type: str = "ADAS"
    standards_scope: list[str] = Field(default_factory=lambda: ["ISO 26262", "ISO 21448", "ISO 8800"])
    description: str | None = None


class ProjectRead(ProjectCreate):
    id: int
    created_at: datetime


class DocumentRead(BaseModel):
    id: int
    project_id: int
    filename: str
    source_type: str
    chunk_count: int
    created_at: datetime


class RetrievedChunk(BaseModel):
    chunk_id: str
    document: str
    text: str
    page: int | None = None
    section: str | None = None
    score: float | None = None
    source_type: str = "project_document"


class Hazard(BaseModel):
    id: str
    description: str
    severity: str | None = None
    exposure: str | None = None
    controllability: str | None = None


class SafetyGoal(BaseModel):
    id: str
    text: str
    linked_hazard: str | None = None


class RequirementQualityScore(BaseModel):
    atomicity: float = 0.0
    clarity: float = 0.0
    testability: float = 0.0
    measurability: float = 0.0
    traceability: float = 0.0
    ambiguity: float = 0.0
    duplication: float = 0.0
    conflict_risk: float = 0.0
    overall: float = 0.0


class Requirement(BaseModel):
    id: str
    type: RequirementType
    text: str
    linked_hazard: str | None = None
    linked_safety_goal: str | None = None
    quality_score: float = 0.0
    quality_issues: list[str] = Field(default_factory=list)
    suggested_improvement: str | None = None
    linked_test_cases: list[str] = Field(default_factory=list)
    evidence_source: str | None = None


class RequirementExtractionResponse(BaseModel):
    requirements: list[Requirement]
    quality_summary: dict[str, Any] = Field(default_factory=dict)


class RequirementGenerateFromStandardsRequest(BaseModel):
    standards: list[str] = Field(default_factory=lambda: ["ISO 26262", "ISO 21448", "ISO 8800"])
    replace_existing: bool = False


class TraceabilityLink(BaseModel):
    hazard_id: str | None = None
    hazard_description: str | None = None
    safety_goal_id: str | None = None
    requirement_id: str
    requirement_type: RequirementType
    requirement_text: str
    test_case_id: str | None = None
    evidence_source: str | None = None
    status: str = "draft"
    quality_score: float


class KnowledgeGraphNode(BaseModel):
    id: str
    label: str
    type: str
    group: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphEdge(BaseModel):
    source: str
    target: str
    relationship: str
    label: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraphResponse(BaseModel):
    project_id: int
    nodes: list[KnowledgeGraphNode]
    edges: list[KnowledgeGraphEdge]
    node_count: int
    edge_count: int
    coverage_summary: dict[str, Any] = Field(default_factory=dict)


class TestCase(BaseModel):
    id: str
    scenario: str
    preconditions: list[str]
    test_steps: list[str]
    expected_result: str
    pass_fail_criteria: str
    linked_requirement: str
    required_evidence: list[str]


class SafetyAnalysis(BaseModel):
    answer: str
    hazards: list[Hazard] = Field(default_factory=list)
    safety_goals: list[SafetyGoal] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    recommended_requirements: list[Requirement] = Field(default_factory=list)
    retrieved_sources: list[RetrievedChunk] = Field(default_factory=list)


class QueryRequest(BaseModel):
    question: str
    standards: list[str] = Field(default_factory=list)
    include_requirements_review: bool = False
    answer_mode: str | None = Field(default=None, description="Optional per-run answer mode: openai, local, or none.")
    answer_model: str | None = Field(default=None, description="Optional per-run model name for OpenAI or local model engines.")


class QueryResponse(BaseModel):
    answer: str
    retrieved_sources: list[RetrievedChunk]
    missing_requirements: list[str] = Field(default_factory=list)
    recommended_requirements: list[Requirement] = Field(default_factory=list)
    evaluation_run_id: int | None = None
    answer_mode: str | None = None
    answer_model: str | None = None


class RetrievalSearchRequest(BaseModel):
    query: str
    tools: list[str] = Field(default_factory=lambda: [
        "project_docs",
        "requirements",
        "traceability",
        "test_cases",
        "evaluation_runs",
        "agent_runs",
    ])
    top_k: int = Field(default=5, ge=1, le=20)


class RetrievalResult(BaseModel):
    source: str
    title: str
    snippet: str
    score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalSearchResponse(BaseModel):
    query: str
    tools_used: list[str]
    results_by_tool: dict[str, list[RetrievalResult]]
    total_results: int


class StandardReference(BaseModel):
    standard: str
    clause: str
    topic: str
    rationale: str
    confidence: float = 0.0
    source: str = "heuristic_clause_mapping"


class EvidenceCitation(BaseModel):
    source: str
    title: str
    citation: str
    snippet: str
    score: float = 0.0
    iso_references: list[StandardReference] = Field(default_factory=list)


class RequirementCompletenessItem(BaseModel):
    requirement_id: str
    quality_score: float
    missing_fields: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    iso_references: list[StandardReference] = Field(default_factory=list)


class HumanReviewItem(BaseModel):
    item_type: str
    item_id: str
    reason: str
    severity: str = "medium"
    suggested_action: str


class PrecisionReviewRequest(BaseModel):
    query: str
    tools: list[str] | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    standards: list[str] = Field(default_factory=lambda: ["ISO 26262", "ISO 21448", "ISO 8800"])


class PrecisionReviewResponse(BaseModel):
    query: str
    routed_tools: list[str]
    reranked_evidence: list[RetrievalResult]
    citations: list[EvidenceCitation]
    compressed_context: list[str]
    requirement_completeness: list[RequirementCompletenessItem]
    human_review_queue: list[HumanReviewItem]
    iso_references: list[StandardReference]
    confidence_score: float
    confidence_rationale: str


class RequirementEvaluateRequest(BaseModel):
    requirements: list[Requirement] | None = None


class EvaluationRun(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: int
    project_id: int
    run_type: str
    model_used: str
    query: str | None = None
    answer: str | None = None
    retrieved_chunk_count: int = 0
    latency_ms: int = 0
    token_usage: dict[str, Any] = Field(default_factory=dict)
    quality_score: float | None = None
    missing_sections: list[str] = Field(default_factory=list)
    hallucination_flags: list[str] = Field(default_factory=list)
    requirement_quality_summary: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class AgentRunLogCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    operation_name: str
    agent_name: str = "safety_analysis_agent"
    status: str = "completed"
    model_used: str = "unknown"
    model_version: str | None = None
    prompt_version: str = "v1"
    prompt_template_id: str | None = None
    tool_config_version: str = "tools-v1"
    user_request: str | None = None
    input_summary: str | None = None
    output_summary: str | None = None
    tools_used: list[str] = Field(default_factory=list)
    retrieved_docs: list[dict[str, Any]] = Field(default_factory=list)
    latency_ms: int = 0
    token_usage: dict[str, Any] = Field(default_factory=dict)
    estimated_cost_usd: float = 0.0
    failure_reason: str | None = None
    failure_stage: str | None = None
    human_escalation_required: bool = False
    escalation_reason: str | None = None
    approval_required: bool = False
    approval_status: str | None = None
    approved_by: str | None = None
    approval_notes: str | None = None
    confidence_score: float | None = None
    hallucination_risk: str = "low"
    hallucination_flags: list[str] = Field(default_factory=list)
    evaluation_score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    evaluation_run_id: int | None = None


class AgentRunLogRead(AgentRunLogCreate):
    model_config = ConfigDict(protected_namespaces=())

    id: int
    agent_run_id: int
    project_id: int
    source_system: str | None = None
    approval_status: str
    created_at: datetime
    updated_at: datetime


class AgentApprovalUpdate(BaseModel):
    approval_status: str
    approved_by: str | None = None
    approval_notes: str | None = None
    human_escalation_required: bool | None = None
    escalation_reason: str | None = None


class ToolOrchestrationRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    user_request: str
    tools: list[str] = Field(default_factory=lambda: [
        "search_project_docs",
        "extract_requirements",
        "evaluate_requirements",
        "generate_traceability",
        "generate_test_cases",
    ])
    prompt_version: str = "orchestration-v1"
    model_version: str = "local-orchestrator-v1"
    tool_config_version: str = "tools-v1"
    confidence_score: float | None = None
    hallucination_risk: str = "low"


class ToolOrchestrationResponse(BaseModel):
    agent_run_id: int
    status: str
    tools_used: list[str]
    tool_results: dict[str, Any]
    approval_required: bool
    human_escalation_required: bool


class IntegrationEventCreate(BaseModel):
    integration_type: str
    title: str
    description: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    agent_run_id: int | None = None


class IntegrationEventRead(IntegrationEventCreate):
    id: int
    project_id: int
    external_id: str
    status: str
    created_at: datetime


class AgentOperationsDashboard(BaseModel):
    project_id: int
    total_runs: int
    success_rate: float
    escalation_rate: float
    average_latency_ms: float
    average_cost_usd: float
    total_cost_usd: float
    average_output_tokens: float = 0.0
    total_output_tokens: int = 0
    approval_pending_count: int
    hallucination_flags: dict[str, int]
    average_evaluation_score: float | None = None


class WorkflowItemCreate(BaseModel):
    title: str
    description: str | None = None
    source_system: str = "autonomous_driving_safety_analyst"
    workflow_stage: str = "intake"
    status: str = "open"
    priority: str = "medium"
    owner: str | None = None
    due_date: datetime | None = None
    linked_requirement_id: str | None = None
    linked_hazard_id: str | None = None
    linked_safety_goal_id: str | None = None
    linked_agent_run_id: int | None = None
    linked_evaluation_run_id: int | None = None
    evidence_refs: list[dict[str, Any]] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    notes: str | None = None


class WorkflowItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    workflow_stage: str | None = None
    status: str | None = None
    priority: str | None = None
    owner: str | None = None
    due_date: datetime | None = None
    linked_requirement_id: str | None = None
    linked_hazard_id: str | None = None
    linked_safety_goal_id: str | None = None
    linked_agent_run_id: int | None = None
    linked_evaluation_run_id: int | None = None
    evidence_refs: list[dict[str, Any]] | None = None
    acceptance_criteria: list[str] | None = None
    notes: str | None = None


class WorkflowItemRead(WorkflowItemCreate):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime


class WorkflowDashboard(BaseModel):
    project_id: int
    total_items: int
    open_items: int
    in_progress_items: int
    blocked_items: int
    done_items: int
    completion_rate: float
    by_stage: dict[str, int]
    by_status: dict[str, int]
    by_priority: dict[str, int]
    overdue_items: int
