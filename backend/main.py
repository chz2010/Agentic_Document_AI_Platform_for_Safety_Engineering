"""FastAPI application for project workspaces, document RAG, and requirements engineering."""

from __future__ import annotations

import time
import re
import shutil
from datetime import datetime
from pathlib import Path

import httpx
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from langchain_core.documents import Document as LangchainDocument
from openai import OpenAI
from sqlmodel import Session, select

from backend.agent_operations import build_operations_dashboard, create_agent_run_log, create_integration_event, run_mock_tool, update_approval
from backend.analysis_intelligence import build_precision_review
from backend.database import get_session, init_db
from backend.document_processing import chunk_documents, extract_documents
from backend.knowledge_graph import build_project_knowledge_graph
from backend.models import AgentRunLogRecord, DocumentChunk, EvaluationRunRecord, IntegrationEventRecord, Project, ProjectDocument, RequirementRecord, TestCaseRecord, WorkflowItemRecord
from backend.reporting import markdown_report, requirements_csv, traceability_csv
from backend.requirements_engineering import build_traceability, extract_requirements_from_text, generate_requirements_from_standards, generate_test_cases, quality_summary
from backend.retrieval_tools import SUPPORTED_RETRIEVAL_TOOLS, run_retrieval_tool
from backend.schemas import (
    AgentApprovalUpdate,
    AgentOperationsDashboard,
    AgentRunLogCreate,
    AgentRunLogRead,
    DocumentRead,
    EvaluationRun,
    IntegrationEventCreate,
    IntegrationEventRead,
    KnowledgeGraphResponse,
    ProjectCreate,
    ProjectRead,
    PrecisionReviewRequest,
    PrecisionReviewResponse,
    QueryRequest,
    QueryResponse,
    RetrievalSearchRequest,
    RetrievalSearchResponse,
    Requirement,
    RequirementEvaluateRequest,
    RequirementExtractionResponse,
    RequirementGenerateFromStandardsRequest,
    SafetyAnalysis,
    TestCase,
    TraceabilityLink,
    ToolOrchestrationRequest,
    ToolOrchestrationResponse,
    WorkflowDashboard,
    WorkflowItemCreate,
    WorkflowItemRead,
    WorkflowItemUpdate,
)
from backend.settings import settings
from backend.vector_store import get_project_vector_store


app = FastAPI(
    title="Agentic Document AI Platform for Safety Engineering API",
    version="0.1.0",
    description="Agentic Document AI and requirements engineering backend for safety engineering workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    Path(settings.project_chroma_path).mkdir(parents=True, exist_ok=True)
    init_db()


@app.get("/health")
def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "answer_mode": _configured_answer_mode(),
        "answer_model": _configured_answer_model(),
        "openai_configured": bool(settings.openai_api_key),
        "embedding_mode": "openai" if settings.openai_api_key else "local_hash",
    }


@app.post("/projects", response_model=ProjectRead)
def create_project(payload: ProjectCreate, session: Session = Depends(get_session)) -> Project:
    project = Project(**payload.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@app.get("/projects", response_model=list[ProjectRead])
def list_projects(session: Session = Depends(get_session)) -> list[Project]:
    return session.exec(select(Project).order_by(Project.created_at.desc())).all()


@app.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, session: Session = Depends(get_session)) -> Project:
    return _project_or_404(project_id, session)


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, session: Session = Depends(get_session)) -> dict[str, int | str]:
    project = _project_or_404(project_id, session)
    _delete_project_vector_entries(project_id)
    _delete_project_uploads(project_id)
    for model in [
        IntegrationEventRecord,
        WorkflowItemRecord,
        AgentRunLogRecord,
        EvaluationRunRecord,
        TestCaseRecord,
        RequirementRecord,
        DocumentChunk,
        ProjectDocument,
    ]:
        for record in session.exec(select(model).where(model.project_id == project_id)).all():
            session.delete(record)
    session.delete(project)
    session.commit()
    return {"status": "deleted", "id": project_id}


@app.post("/projects/{project_id}/documents", response_model=DocumentRead)
async def upload_document(project_id: int, file: UploadFile = File(...), session: Session = Depends(get_session)) -> ProjectDocument:
    _project_or_404(project_id, session)
    suffix = Path(file.filename or "").suffix.lower()
    project_dir = settings.uploads_dir / str(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)
    storage_path = project_dir / (file.filename or f"upload{suffix}")
    storage_path.write_bytes(await file.read())

    try:
        docs = extract_documents(storage_path)
    except ValueError as exc:
        storage_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db_doc = ProjectDocument(
        project_id=project_id,
        filename=storage_path.name,
        source_type=suffix.lstrip(".") or "unknown",
        storage_path=str(storage_path),
    )
    session.add(db_doc)
    session.commit()
    session.refresh(db_doc)

    chunks = chunk_documents(docs)
    vector_docs: list[LangchainDocument] = []
    ids: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_id = f"project-{project_id}-doc-{db_doc.id}-chunk-{index:04d}"
        ids.append(chunk_id)
        metadata = {
            "project_id": str(project_id),
            "document_id": str(db_doc.id),
            "document": db_doc.filename,
            "source_type": db_doc.source_type,
            "chunk_id": chunk_id,
        }
        if chunk.metadata.get("page") is not None:
            metadata["page"] = chunk.metadata.get("page")
        if chunk.metadata.get("section"):
            metadata["section"] = chunk.metadata.get("section")
        vector_docs.append(LangchainDocument(page_content=chunk.page_content, metadata=metadata))
        session.add(
            DocumentChunk(
                project_id=project_id,
                document_id=db_doc.id,
                chunk_id=chunk_id,
                page=chunk.metadata.get("page"),
                section=chunk.metadata.get("section"),
                text_preview=chunk.page_content[:400],
            )
        )

    if vector_docs:
        get_project_vector_store().add_documents(vector_docs, ids=ids)
    db_doc.chunk_count = len(vector_docs)
    session.add(db_doc)
    session.commit()
    session.refresh(db_doc)
    return db_doc


@app.get("/projects/{project_id}/documents", response_model=list[DocumentRead])
def list_documents(project_id: int, session: Session = Depends(get_session)) -> list[ProjectDocument]:
    _project_or_404(project_id, session)
    return session.exec(select(ProjectDocument).where(ProjectDocument.project_id == project_id)).all()


@app.post("/projects/{project_id}/query", response_model=QueryResponse)
def query_project(project_id: int, payload: QueryRequest, session: Session = Depends(get_session)) -> QueryResponse:
    _project_or_404(project_id, session)
    started = time.perf_counter()
    retrieved = _retrieve_project_chunks(project_id, payload.question)
    answer_mode = _configured_answer_mode(payload.answer_mode)
    answer_model = _configured_answer_model(payload.answer_mode, payload.answer_model)
    answer = _answer_from_context(payload.question, retrieved, payload.standards, payload.answer_mode, payload.answer_model)
    missing_requirements: list[str] = []
    recommended_requirements: list[Requirement] = []
    if payload.include_requirements_review:
        missing_requirements = _missing_requirements(payload.question, retrieved)
        recommended_requirements = extract_requirements_from_text("\n".join(missing_requirements), "generated_from_query")

    latency_ms = int((time.perf_counter() - started) * 1000)
    token_usage = {
        "prompt_tokens": _estimate_text_tokens(payload.question + " " + " ".join(chunk.text for chunk in retrieved)),
        "completion_tokens": _estimate_text_tokens(answer),
        "estimated": True,
    }
    run = EvaluationRunRecord(
        project_id=project_id,
        run_type="query",
        model_used=answer_model,
        query=payload.question,
        answer=answer,
        retrieved_chunk_count=len(retrieved),
        latency_ms=latency_ms,
        token_usage=token_usage,
        missing_sections=missing_requirements,
        requirement_quality_summary=quality_summary(recommended_requirements),
    )
    session.add(run)
    session.commit()
    session.refresh(run)
    run_quality_score = _query_quality_score(retrieved, missing_requirements)
    create_agent_run_log(
        project_id,
        AgentRunLogCreate(
            evaluation_run_id=run.id,
            operation_name="project_query",
            agent_name="project_rag_agent",
            status="resolved",
            model_used=run.model_used,
            model_version=run.model_used,
            prompt_version="query-answer-v1",
            prompt_template_id="project-rag-with-requirements-review",
            tool_config_version="rag-tools-v1",
            user_request=payload.question,
            input_summary=payload.question,
            output_summary=answer[:500],
            tools_used=["search_project_docs", "requirements_review"] if payload.include_requirements_review else ["search_project_docs"],
            retrieved_docs=[chunk.model_dump(mode="json") for chunk in retrieved],
            latency_ms=latency_ms,
            token_usage=token_usage,
            estimated_cost_usd=0.0,
            confidence_score=run_quality_score,
            hallucination_risk="low" if retrieved else "high",
            hallucination_flags=[] if retrieved else ["no_retrieved_evidence"],
            evaluation_score=run_quality_score,
            metadata={
                "source_system": "autonomous_driving_safety_analyst",
                "retrieved_chunk_count": len(retrieved),
                "include_requirements_review": payload.include_requirements_review,
                "standards": payload.standards,
                "answer_mode": answer_mode,
            },
        ),
        session,
    )
    return QueryResponse(
        answer=answer,
        retrieved_sources=retrieved,
        missing_requirements=missing_requirements,
        recommended_requirements=recommended_requirements,
        evaluation_run_id=run.id,
        answer_mode=answer_mode,
        answer_model=answer_model,
    )


@app.post("/projects/{project_id}/retrieval/search", response_model=RetrievalSearchResponse)
def retrieval_search(project_id: int, payload: RetrievalSearchRequest, session: Session = Depends(get_session)) -> RetrievalSearchResponse:
    _project_or_404(project_id, session)
    tools = [tool for tool in payload.tools if tool in SUPPORTED_RETRIEVAL_TOOLS]
    results_by_tool = {
        tool: run_retrieval_tool(tool, project_id, payload.query, payload.top_k, session)
        for tool in tools
    }
    return RetrievalSearchResponse(
        query=payload.query,
        tools_used=tools,
        results_by_tool=results_by_tool,
        total_results=sum(len(results) for results in results_by_tool.values()),
    )


@app.post("/projects/{project_id}/analysis/precision-review", response_model=PrecisionReviewResponse)
def precision_review(project_id: int, payload: PrecisionReviewRequest, session: Session = Depends(get_session)) -> PrecisionReviewResponse:
    project = _project_or_404(project_id, session)
    standards = payload.standards or project.standards_scope
    return build_precision_review(
        project_id=project_id,
        query=payload.query,
        requested_tools=payload.tools,
        top_k=payload.top_k,
        standards=standards,
        session=session,
    )


@app.post("/projects/{project_id}/safety-analysis", response_model=SafetyAnalysis)
def safety_analysis(project_id: int, payload: QueryRequest, session: Session = Depends(get_session)) -> SafetyAnalysis:
    response = query_project(project_id, payload, session)
    return SafetyAnalysis(
        answer=response.answer,
        retrieved_sources=response.retrieved_sources,
        missing_requirements=response.missing_requirements,
        recommended_requirements=response.recommended_requirements,
    )


@app.post("/projects/{project_id}/requirements/extract", response_model=RequirementExtractionResponse)
def extract_requirements(project_id: int, session: Session = Depends(get_session)) -> RequirementExtractionResponse:
    _project_or_404(project_id, session)
    requirements = _extract_project_requirements(project_id)
    _replace_requirements(project_id, requirements, session)
    summary = quality_summary(requirements)
    session.add(
        EvaluationRunRecord(
            project_id=project_id,
            run_type="requirements_extract",
            model_used="heuristic-pydantic-extractor",
            retrieved_chunk_count=len(requirements),
            requirement_quality_summary=summary,
            quality_score=summary.get("average_quality_score", 0.0),
        )
    )
    session.commit()
    return RequirementExtractionResponse(requirements=requirements, quality_summary=summary)


@app.post("/projects/{project_id}/requirements/generate", response_model=RequirementExtractionResponse)
def generate_requirements(project_id: int, payload: QueryRequest, session: Session = Depends(get_session)) -> RequirementExtractionResponse:
    response = query_project(project_id, payload, session)
    text = "\n".join(response.missing_requirements) or f"The system shall address: {payload.question}."
    requirements = extract_requirements_from_text(text, "generated_from_safety_analysis")
    _replace_requirements(project_id, _stored_requirements(project_id, session) + requirements, session)
    return RequirementExtractionResponse(requirements=requirements, quality_summary=quality_summary(requirements))


@app.post("/projects/{project_id}/requirements/generate-from-standards", response_model=RequirementExtractionResponse)
def generate_requirements_from_iso_standards(
    project_id: int,
    payload: RequirementGenerateFromStandardsRequest,
    session: Session = Depends(get_session),
) -> RequirementExtractionResponse:
    project = _project_or_404(project_id, session)
    standards = payload.standards or project.standards_scope
    generated = generate_requirements_from_standards(
        standards,
        domain=project.domain,
        system_type=project.system_type,
    )
    requirements = generated if payload.replace_existing else _stored_requirements(project_id, session) + generated
    _replace_requirements(project_id, requirements, session)
    summary = quality_summary(generated)
    session.add(
        EvaluationRunRecord(
            project_id=project_id,
            run_type="requirements_generate_from_standards",
            model_used="iso-candidate-template-generator",
            retrieved_chunk_count=len(generated),
            quality_score=summary.get("average_quality_score", 0.0),
            requirement_quality_summary={
                **summary,
                "standards": standards,
                "note": "Candidate requirements generated from ISO clause areas; verify against licensed standards before production use.",
            },
        )
    )
    session.commit()
    return RequirementExtractionResponse(requirements=generated, quality_summary=summary)


@app.post("/projects/{project_id}/requirements/evaluate", response_model=RequirementExtractionResponse)
def evaluate_requirements(project_id: int, payload: RequirementEvaluateRequest, session: Session = Depends(get_session)) -> RequirementExtractionResponse:
    _project_or_404(project_id, session)
    requirements = payload.requirements or _stored_requirements(project_id, session)
    summary = quality_summary(requirements)
    session.add(
        EvaluationRunRecord(
            project_id=project_id,
            run_type="requirements_evaluate",
            model_used="heuristic-quality-scorer",
            retrieved_chunk_count=len(requirements),
            quality_score=summary.get("average_quality_score", 0.0),
            requirement_quality_summary=summary,
        )
    )
    session.commit()
    return RequirementExtractionResponse(requirements=requirements, quality_summary=summary)


@app.get("/projects/{project_id}/traceability", response_model=list[TraceabilityLink])
def get_traceability(project_id: int, format: str = Query(default="json", pattern="^(json|csv)$"), session: Session = Depends(get_session)):
    _project_or_404(project_id, session)
    rows = build_traceability(_stored_requirements(project_id, session))
    if format == "csv":
        return PlainTextResponse(traceability_csv(rows), media_type="text/csv")
    return rows


@app.get("/projects/{project_id}/knowledge-graph", response_model=KnowledgeGraphResponse)
def get_knowledge_graph(project_id: int, session: Session = Depends(get_session)) -> KnowledgeGraphResponse:
    project = _project_or_404(project_id, session)
    requirements = _stored_requirements(project_id, session)
    traceability = build_traceability(requirements)
    documents = session.exec(select(ProjectDocument).where(ProjectDocument.project_id == project_id)).all()
    test_cases = session.exec(select(TestCaseRecord).where(TestCaseRecord.project_id == project_id)).all()
    workflow_items = session.exec(select(WorkflowItemRecord).where(WorkflowItemRecord.project_id == project_id)).all()
    evaluation_runs = session.exec(select(EvaluationRunRecord).where(EvaluationRunRecord.project_id == project_id)).all()
    agent_runs = session.exec(select(AgentRunLogRecord).where(AgentRunLogRecord.project_id == project_id)).all()
    return build_project_knowledge_graph(
        project=project,
        documents=documents,
        requirements=requirements,
        traceability=traceability,
        test_cases=test_cases,
        workflow_items=workflow_items,
        evaluation_runs=evaluation_runs,
        agent_runs=agent_runs,
    )


@app.post("/projects/{project_id}/test-cases/generate", response_model=list[TestCase])
def create_test_cases(project_id: int, session: Session = Depends(get_session)) -> list[TestCase]:
    _project_or_404(project_id, session)
    test_cases = generate_test_cases(_stored_requirements(project_id, session))
    for test_case in test_cases:
        session.add(TestCaseRecord(project_id=project_id, test_case_id=test_case.id, payload=test_case.model_dump(mode="json")))
    session.commit()
    return test_cases


@app.get("/projects/{project_id}/evaluation-runs", response_model=list[EvaluationRun])
def list_evaluation_runs(project_id: int, session: Session = Depends(get_session)) -> list[EvaluationRunRecord]:
    _project_or_404(project_id, session)
    return session.exec(select(EvaluationRunRecord).where(EvaluationRunRecord.project_id == project_id).order_by(EvaluationRunRecord.created_at.desc())).all()


@app.post("/projects/{project_id}/agent-runs", response_model=AgentRunLogRead)
def create_agent_run(project_id: int, payload: AgentRunLogCreate, session: Session = Depends(get_session)) -> AgentRunLogRead:
    _project_or_404(project_id, session)
    return _agent_run_read(create_agent_run_log(project_id, payload, session))


@app.get("/projects/{project_id}/agent-runs", response_model=list[AgentRunLogRead])
def list_agent_runs(
    project_id: int,
    approval_status: str | None = None,
    human_escalation_required: bool | None = None,
    source_system: str | None = None,
    session: Session = Depends(get_session),
) -> list[AgentRunLogRead]:
    _project_or_404(project_id, session)
    statement = select(AgentRunLogRecord).where(AgentRunLogRecord.project_id == project_id)
    if approval_status:
        statement = statement.where(AgentRunLogRecord.approval_status == approval_status)
    if human_escalation_required is not None:
        statement = statement.where(AgentRunLogRecord.human_escalation_required == human_escalation_required)
    records = session.exec(statement.order_by(AgentRunLogRecord.created_at.desc())).all()
    if source_system:
        records = [record for record in records if (record.run_metadata or {}).get("source_system") == source_system]
    return [_agent_run_read(record) for record in records]


@app.get("/projects/{project_id}/agent-runs/{agent_run_id}", response_model=AgentRunLogRead)
def get_agent_run(project_id: int, agent_run_id: int, session: Session = Depends(get_session)) -> AgentRunLogRead:
    _project_or_404(project_id, session)
    return _agent_run_read(_agent_run_or_404(project_id, agent_run_id, session))


@app.patch("/projects/{project_id}/agent-runs/{agent_run_id}/approval", response_model=AgentRunLogRead)
def update_agent_run_approval(project_id: int, agent_run_id: int, payload: AgentApprovalUpdate, session: Session = Depends(get_session)) -> AgentRunLogRead:
    _project_or_404(project_id, session)
    record = _agent_run_or_404(project_id, agent_run_id, session)
    return _agent_run_read(update_approval(record, payload, session))


@app.post("/projects/{project_id}/agent-tools/run", response_model=ToolOrchestrationResponse)
def run_agent_tools(project_id: int, payload: ToolOrchestrationRequest, session: Session = Depends(get_session)) -> ToolOrchestrationResponse:
    _project_or_404(project_id, session)
    started = time.perf_counter()
    tool_results = {
        tool_name: run_mock_tool(tool_name, project_id, payload.user_request, session)
        for tool_name in payload.tools
    }
    needs_review = payload.hallucination_risk in {"high", "critical"} or (
        payload.confidence_score is not None and payload.confidence_score < 0.75
    )
    record = create_agent_run_log(
        project_id,
        AgentRunLogCreate(
            operation_name="tool_orchestration",
            agent_name="orchestration_agent",
            status="requires_human_review" if needs_review else "resolved",
            model_used=payload.model_version,
            model_version=payload.model_version,
            prompt_version=payload.prompt_version,
            tool_config_version=payload.tool_config_version,
            user_request=payload.user_request,
            input_summary=payload.user_request,
            output_summary=f"Executed {len(payload.tools)} tools.",
            tools_used=payload.tools,
            latency_ms=int((time.perf_counter() - started) * 1000),
            confidence_score=payload.confidence_score,
            hallucination_risk=payload.hallucination_risk,
            hallucination_flags=["high_hallucination_risk"] if payload.hallucination_risk in {"high", "critical"} else [],
            evaluation_score=payload.confidence_score,
            metadata={"source_system": "agentic_document_ai_platform", "tool_results": tool_results},
        ),
        session,
    )
    return ToolOrchestrationResponse(
        agent_run_id=record.id,
        status=record.status,
        tools_used=record.tools_used,
        tool_results=tool_results,
        approval_required=record.approval_required,
        human_escalation_required=record.human_escalation_required,
    )


@app.post("/projects/{project_id}/integrations/mock", response_model=IntegrationEventRead)
def create_mock_integration(project_id: int, payload: IntegrationEventCreate, session: Session = Depends(get_session)) -> IntegrationEventRecord:
    _project_or_404(project_id, session)
    return create_integration_event(project_id, payload, session)


@app.post("/projects/{project_id}/integrations/github-issue", response_model=IntegrationEventRead)
def create_mock_github_issue(project_id: int, payload: IntegrationEventCreate, session: Session = Depends(get_session)) -> IntegrationEventRecord:
    _project_or_404(project_id, session)
    payload.integration_type = "github_issue"
    return create_integration_event(project_id, payload, session)


@app.post("/projects/{project_id}/integrations/jira-ticket", response_model=IntegrationEventRead)
def create_mock_jira_ticket(project_id: int, payload: IntegrationEventCreate, session: Session = Depends(get_session)) -> IntegrationEventRecord:
    _project_or_404(project_id, session)
    payload.integration_type = "jira_ticket"
    return create_integration_event(project_id, payload, session)


@app.post("/projects/{project_id}/integrations/slack-notification", response_model=IntegrationEventRead)
def create_mock_slack_notification(project_id: int, payload: IntegrationEventCreate, session: Session = Depends(get_session)) -> IntegrationEventRecord:
    _project_or_404(project_id, session)
    payload.integration_type = "slack_notification"
    return create_integration_event(project_id, payload, session)


@app.get("/projects/{project_id}/integrations", response_model=list[IntegrationEventRead])
def list_integrations(project_id: int, session: Session = Depends(get_session)) -> list[IntegrationEventRecord]:
    _project_or_404(project_id, session)
    return session.exec(select(IntegrationEventRecord).where(IntegrationEventRecord.project_id == project_id).order_by(IntegrationEventRecord.created_at.desc())).all()


@app.post("/projects/{project_id}/workflow/items", response_model=WorkflowItemRead)
def create_workflow_item(project_id: int, payload: WorkflowItemCreate, session: Session = Depends(get_session)) -> WorkflowItemRead:
    _project_or_404(project_id, session)
    record = WorkflowItemRecord(project_id=project_id, **payload.model_dump())
    session.add(record)
    session.commit()
    session.refresh(record)
    return _workflow_item_read(record)


@app.get("/projects/{project_id}/workflow/items", response_model=list[WorkflowItemRead])
def list_workflow_items(
    project_id: int,
    status: str | None = None,
    workflow_stage: str | None = None,
    source_system: str | None = None,
    session: Session = Depends(get_session),
) -> list[WorkflowItemRead]:
    _project_or_404(project_id, session)
    statement = select(WorkflowItemRecord).where(WorkflowItemRecord.project_id == project_id)
    if status:
        statement = statement.where(WorkflowItemRecord.status == status)
    if workflow_stage:
        statement = statement.where(WorkflowItemRecord.workflow_stage == workflow_stage)
    if source_system:
        statement = statement.where(WorkflowItemRecord.source_system == source_system)
    records = session.exec(statement.order_by(WorkflowItemRecord.created_at.desc())).all()
    return [_workflow_item_read(record) for record in records]


@app.patch("/projects/{project_id}/workflow/items/{item_id}", response_model=WorkflowItemRead)
def update_workflow_item(project_id: int, item_id: int, payload: WorkflowItemUpdate, session: Session = Depends(get_session)) -> WorkflowItemRead:
    _project_or_404(project_id, session)
    record = session.get(WorkflowItemRecord, item_id)
    if not record or record.project_id != project_id:
        raise HTTPException(status_code=404, detail="Workflow item not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    record.updated_at = datetime.utcnow()
    session.add(record)
    session.commit()
    session.refresh(record)
    return _workflow_item_read(record)


@app.delete("/projects/{project_id}/workflow/items/{item_id}")
def delete_workflow_item(project_id: int, item_id: int, session: Session = Depends(get_session)) -> dict[str, int | str]:
    _project_or_404(project_id, session)
    record = session.get(WorkflowItemRecord, item_id)
    if not record or record.project_id != project_id:
        raise HTTPException(status_code=404, detail="Workflow item not found")
    session.delete(record)
    session.commit()
    return {"status": "deleted", "id": item_id}


@app.get("/projects/{project_id}/workflow/dashboard", response_model=WorkflowDashboard)
def get_workflow_dashboard(
    project_id: int,
    source_system: str | None = None,
    session: Session = Depends(get_session),
) -> WorkflowDashboard:
    _project_or_404(project_id, session)
    statement = select(WorkflowItemRecord).where(WorkflowItemRecord.project_id == project_id)
    if source_system:
        statement = statement.where(WorkflowItemRecord.source_system == source_system)
    records = session.exec(statement).all()
    return _build_workflow_dashboard(project_id, records)


@app.post("/projects/{project_id}/workflow/bootstrap-autonomous-safety-analyst", response_model=list[WorkflowItemRead])
def bootstrap_autonomous_safety_analyst_workflow(project_id: int, session: Session = Depends(get_session)) -> list[WorkflowItemRead]:
    _project_or_404(project_id, session)
    existing = session.exec(
        select(WorkflowItemRecord).where(
            WorkflowItemRecord.project_id == project_id,
            WorkflowItemRecord.source_system == "autonomous_driving_safety_analyst",
        )
    ).all()
    if existing:
        return [_workflow_item_read(record) for record in existing]

    templates = [
        WorkflowItemCreate(
            title="Define safety analysis question",
            description="Capture the first project's user question, standards scope, target system, and expected decision.",
            workflow_stage="intake",
            status="open",
            priority="high",
            acceptance_criteria=["Question is specific", "Standards scope is selected", "Expected output is clear"],
        ),
        WorkflowItemCreate(
            title="Retrieve safety evidence",
            description="Run project-specific retrieval against ISO, SOTIF, ISO 8800, NCAP/IIHS, video, and dataset context where available.",
            workflow_stage="evidence_retrieval",
            status="open",
            priority="high",
            acceptance_criteria=["Retrieved sources are visible", "Evidence is linked to the question", "Weak or missing evidence is flagged"],
        ),
        WorkflowItemCreate(
            title="Review answer quality and hallucination risk",
            description="Check citations, missing sections, confidence, hallucination flags, and need for human review.",
            workflow_stage="quality_review",
            status="open",
            priority="high",
            acceptance_criteria=["Confidence score is recorded", "Hallucination flags are reviewed", "Human review gate is decided"],
        ),
        WorkflowItemCreate(
            title="Convert findings into requirements",
            description="Translate safety analysis gaps into candidate requirements with hazards, safety goals, and ISO references.",
            workflow_stage="requirements_engineering",
            status="open",
            priority="medium",
            acceptance_criteria=["Requirements have measurable thresholds", "ODD assumptions are captured", "Hazard and safety-goal links exist"],
        ),
        WorkflowItemCreate(
            title="Generate traceability and tests",
            description="Build Hazard -> Safety Goal -> Requirement -> Test Case -> Evidence links for the first project result.",
            workflow_stage="traceability",
            status="open",
            priority="medium",
            acceptance_criteria=["Traceability matrix is complete", "Test cases include pass/fail criteria", "Evidence source is recorded"],
        ),
        WorkflowItemCreate(
            title="Prepare report for portfolio or engineering review",
            description="Export a concise report with answer, evidence, quality review, requirements, traceability, and follow-up actions.",
            workflow_stage="reporting",
            status="open",
            priority="medium",
            acceptance_criteria=["Report is exported", "Open risks are listed", "Next actions are assigned"],
        ),
    ]
    records: list[WorkflowItemRecord] = []
    for template in templates:
        record = WorkflowItemRecord(project_id=project_id, **template.model_dump())
        session.add(record)
        records.append(record)
    session.commit()
    for record in records:
        session.refresh(record)
    return [_workflow_item_read(record) for record in records]


@app.get("/projects/{project_id}/agent-operations/dashboard", response_model=AgentOperationsDashboard)
def get_agent_operations_dashboard(
    project_id: int,
    source_system: str | None = None,
    session: Session = Depends(get_session),
) -> AgentOperationsDashboard:
    _project_or_404(project_id, session)
    return build_operations_dashboard(project_id, session, source_system=source_system)


@app.get("/projects/{project_id}/report")
def export_report(project_id: int, format: str = Query(default="markdown", pattern="^(markdown|requirements_csv|traceability_csv|json)$"), session: Session = Depends(get_session)):
    project = _project_or_404(project_id, session)
    requirements = _stored_requirements(project_id, session)
    traceability = build_traceability(requirements)
    if format == "requirements_csv":
        return PlainTextResponse(requirements_csv(requirements), media_type="text/csv")
    if format == "traceability_csv":
        return PlainTextResponse(traceability_csv(traceability), media_type="text/csv")
    if format == "json":
        return {"requirements": requirements, "traceability": traceability}
    return PlainTextResponse(markdown_report(project.name, requirements, traceability), media_type="text/markdown")


def _project_or_404(project_id: int, session: Session) -> Project:
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _delete_project_vector_entries(project_id: int) -> None:
    try:
        get_project_vector_store().delete(where={"project_id": str(project_id)})
    except Exception:
        # Keep project deletion robust even if the local vector store is unavailable or empty.
        pass


def _delete_project_uploads(project_id: int) -> None:
    project_upload_dir = settings.uploads_dir / str(project_id)
    if project_upload_dir.exists():
        shutil.rmtree(project_upload_dir)


def _agent_run_or_404(project_id: int, agent_run_id: int, session: Session) -> AgentRunLogRecord:
    record = session.get(AgentRunLogRecord, agent_run_id)
    if not record or record.project_id != project_id:
        raise HTTPException(status_code=404, detail="Agent run log not found")
    return record


def _agent_run_read(record: AgentRunLogRecord) -> AgentRunLogRead:
    return AgentRunLogRead(
        id=record.id,
        agent_run_id=record.id,
        project_id=record.project_id,
        source_system=(record.run_metadata or {}).get("source_system"),
        evaluation_run_id=record.evaluation_run_id,
        operation_name=record.operation_name,
        agent_name=record.agent_name,
        status=record.status,
        model_used=record.model_used,
        model_version=record.model_version,
        prompt_version=record.prompt_version,
        prompt_template_id=record.prompt_template_id,
        tool_config_version=record.tool_config_version,
        user_request=record.user_request,
        input_summary=record.input_summary,
        output_summary=record.output_summary,
        tools_used=record.tools_used,
        retrieved_docs=record.retrieved_docs,
        latency_ms=record.latency_ms,
        token_usage=record.token_usage,
        estimated_cost_usd=record.estimated_cost_usd,
        failure_reason=record.failure_reason,
        failure_stage=record.failure_stage,
        human_escalation_required=record.human_escalation_required,
        escalation_reason=record.escalation_reason,
        approval_required=record.approval_required,
        approval_status=record.approval_status,
        approved_by=record.approved_by,
        approval_notes=record.approval_notes,
        confidence_score=record.confidence_score,
        hallucination_risk=record.hallucination_risk,
        hallucination_flags=record.hallucination_flags,
        evaluation_score=record.evaluation_score,
        metadata=record.run_metadata,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _workflow_item_read(record: WorkflowItemRecord) -> WorkflowItemRead:
    return WorkflowItemRead(
        id=record.id,
        project_id=record.project_id,
        title=record.title,
        description=record.description,
        source_system=record.source_system,
        workflow_stage=record.workflow_stage,
        status=record.status,
        priority=record.priority,
        owner=record.owner,
        due_date=record.due_date,
        linked_requirement_id=record.linked_requirement_id,
        linked_hazard_id=record.linked_hazard_id,
        linked_safety_goal_id=record.linked_safety_goal_id,
        linked_agent_run_id=record.linked_agent_run_id,
        linked_evaluation_run_id=record.linked_evaluation_run_id,
        evidence_refs=record.evidence_refs,
        acceptance_criteria=record.acceptance_criteria,
        notes=record.notes,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _build_workflow_dashboard(project_id: int, records: list[WorkflowItemRecord]) -> WorkflowDashboard:
    by_stage: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_priority: dict[str, int] = {}
    now = datetime.utcnow()
    for record in records:
        by_stage[record.workflow_stage] = by_stage.get(record.workflow_stage, 0) + 1
        by_status[record.status] = by_status.get(record.status, 0) + 1
        by_priority[record.priority] = by_priority.get(record.priority, 0) + 1

    total = len(records)
    done = by_status.get("done", 0) + by_status.get("completed", 0)
    return WorkflowDashboard(
        project_id=project_id,
        total_items=total,
        open_items=by_status.get("open", 0),
        in_progress_items=by_status.get("in_progress", 0),
        blocked_items=by_status.get("blocked", 0),
        done_items=done,
        completion_rate=round(done / total, 3) if total else 0.0,
        by_stage=by_stage,
        by_status=by_status,
        by_priority=by_priority,
        overdue_items=sum(
            1
            for record in records
            if record.due_date is not None and record.due_date < now and record.status not in {"done", "completed"}
        ),
    )


def _retrieve_project_chunks(project_id: int, question: str):
    docs = get_project_vector_store().similarity_search(
        question,
        k=settings.retrieval_k,
        filter={"project_id": str(project_id)},
    )
    from backend.schemas import RetrievedChunk

    return [
        RetrievedChunk(
            chunk_id=doc.metadata.get("chunk_id", ""),
            document=doc.metadata.get("document", "unknown"),
            page=doc.metadata.get("page"),
            section=doc.metadata.get("section"),
            text=doc.page_content,
            score=None,
            source_type=doc.metadata.get("source_type", "project_document"),
        )
        for doc in docs
    ]


def _answer_from_context(
    question: str,
    chunks,
    standards: list[str],
    requested_mode: str | None = None,
    requested_model: str | None = None,
) -> str:
    context = "\n\n".join(f"[{chunk.document} p.{chunk.page}] {chunk.text}" for chunk in chunks)
    mode = _configured_answer_mode(requested_mode)
    model = _configured_answer_model(requested_mode, requested_model)
    if mode == "openai":
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _answer_system_prompt()},
                {"role": "user", "content": _answer_user_prompt(question, standards, context)},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content or ""
    if mode == "local":
        local_answer = _local_llm_answer(question, standards, context, model)
        if local_answer:
            return local_answer
        return _deterministic_answer_from_context(
            question,
            chunks,
            standards,
            prefix="Local model unavailable. Deterministic evidence synthesis was used instead.",
        )
    return _deterministic_answer_from_context(question, chunks, standards)


def _configured_answer_mode(requested_mode: str | None = None) -> str:
    requested = (requested_mode or "").strip().lower()
    configured = requested or settings.answer_mode
    mode = configured if configured in {"none", "openai", "local", "auto"} else "none"
    if mode == "auto":
        return "openai" if settings.openai_api_key and settings.use_openai_generation else "none"
    if mode == "openai" and (not settings.openai_api_key or not settings.use_openai_generation):
        return "none"
    return mode


def _configured_answer_model(requested_mode: str | None = None, requested_model: str | None = None) -> str:
    mode = _configured_answer_mode(requested_mode)
    model = (requested_model or "").strip()
    if mode == "openai":
        return model or settings.llm_model
    if mode == "local":
        return model or settings.local_llm_model
    return "deterministic-evidence-synthesis"


def _answer_system_prompt() -> str:
    return (
        "You are an autonomous-driving safety and requirements engineering analyst. "
        "Answer only from the supplied evidence, cite the document/page markers when useful, "
        "separate confirmed coverage from gaps, and do not invent exact ISO clause numbers unless they are present in the evidence."
    )


def _answer_user_prompt(question: str, standards: list[str], context: str) -> str:
    return (
        f"Question: {question}\n"
        f"Standards scope: {', '.join(standards) or 'project documents only'}\n\n"
        "Return a concise professional answer with these sections: Answer, Evidence reviewed, "
        "Safety/requirements interpretation, Missing or weak evidence, Recommended next actions.\n\n"
        f"Evidence:\n{context}"
    )


def _local_llm_answer(question: str, standards: list[str], context: str, model: str) -> str | None:
    if not context.strip():
        return None
    base_url = settings.local_llm_base_url.rstrip("/")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _answer_system_prompt()},
            {"role": "user", "content": _answer_user_prompt(question, standards, context)},
        ],
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": settings.local_llm_num_predict},
    }
    try:
        response = httpx.post(f"{base_url}/api/chat", json=payload, timeout=settings.local_llm_timeout)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    data = response.json()
    content = data.get("message", {}).get("content")
    return content.strip() if isinstance(content, str) and content.strip() else None


def _deterministic_answer_from_context(question: str, chunks, standards: list[str], prefix: str | None = None) -> str:
    if not chunks:
        sections = []
        if prefix:
            sections.append(prefix)
        sections.append(
            "## Answer\n"
            "No project-specific evidence was retrieved for this question. Upload relevant safety documents, "
            "requirements, test reports, or broaden the query before treating the result as complete."
        )
        sections.append("## Evidence reviewed\n- No retrieved project chunks.")
        sections.append(
            "## Recommended next actions\n"
            "- Upload or ingest the relevant project documents.\n"
            "- Re-run retrieval and requirement extraction.\n"
            "- Check that hazards, safety goals, requirements, test cases, and evidence are linked."
        )
        return "\n\n".join(sections)

    evidence_lines = _evidence_lines(question, chunks)
    coverage_terms = _coverage_terms(question, chunks)
    gap_lines = _deterministic_gap_lines(question, chunks)
    standards_text = ", ".join(standards) if standards else "project document evidence only"

    sections = []
    if prefix:
        sections.append(prefix)
    sections.append(
        "## Answer\n"
        f"The retrieved evidence gives a partial project-specific answer to: \"{question}\". "
        f"It contains {len(chunks)} relevant evidence chunk(s), but completeness still depends on whether the linked "
        "hazards, safety goals, measurable requirements, verification method, and test evidence are all present."
    )
    sections.append("## Evidence reviewed\n" + "\n".join(evidence_lines))
    sections.append(
        "## Safety/requirements interpretation\n"
        f"- Standards lens: {standards_text}.\n"
        f"- Coverage signals found: {', '.join(coverage_terms) if coverage_terms else 'no strong coverage signals found'}.\n"
        "- Treat retrieved project evidence as primary. Use ISO references as review lenses unless exact clauses are present in the documents.\n"
        "- A strong requirement should be atomic, unambiguous, measurable, testable, traceable to a hazard/safety goal, and linked to evidence."
    )
    sections.append("## Missing or weak evidence\n" + "\n".join(gap_lines))
    sections.append(
        "## Recommended next actions\n"
        "- Convert each gap into a requirement or verification task.\n"
        "- Link each requirement to a hazard, safety goal, test case, and evidence source.\n"
        "- Re-run requirement quality scoring and the traceability matrix after updating the documents."
    )
    return "\n\n".join(sections)


def _evidence_lines(question: str, chunks) -> list[str]:
    lines: list[str] = []
    for chunk in chunks[:5]:
        citation = f"{chunk.document}"
        if chunk.page is not None:
            citation += f", page {chunk.page}"
        sentence = _best_sentence(question, chunk.text)
        lines.append(f"- {citation} ({chunk.chunk_id}): {sentence}")
    return lines


def _best_sentence(question: str, text: str) -> str:
    sentences = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", _clean_text(text)) if sentence.strip()]
    if not sentences:
        return _clean_text(text)[:260]
    terms = _query_terms(question)
    ranked = sorted(
        sentences,
        key=lambda sentence: sum(1 for term in terms if term in sentence.lower()),
        reverse=True,
    )
    best = ranked[0]
    return best if len(best) <= 280 else best[:277].rstrip() + "..."


def _coverage_terms(question: str, chunks) -> list[str]:
    text = " ".join(chunk.text.lower() for chunk in chunks)
    candidates = [
        "hazard",
        "safety goal",
        "requirement",
        "test",
        "verification",
        "validation",
        "evidence",
        "ODD",
        "night",
        "occlusion",
        "pedestrian",
        "range",
        "threshold",
        "confidence",
    ]
    return [term for term in candidates if term.lower() in text or term.lower() in question.lower()]


def _deterministic_gap_lines(question: str, chunks) -> list[str]:
    text = " ".join(chunk.text.lower() for chunk in chunks)
    question_lower = question.lower()
    gaps: list[str] = []
    if "hazard" not in text:
        gaps.append("- Hazard linkage is not explicit in the retrieved evidence.")
    if "safety goal" not in text and "sg-" not in text:
        gaps.append("- Safety goal linkage is not explicit in the retrieved evidence.")
    if "test" not in text and "verification" not in text and "validation" not in text:
        gaps.append("- Verification or validation method is not clearly stated.")
    if "range" not in text and "detect" in text:
        gaps.append("- Measurable detection range or operating threshold is missing or weak.")
    if "night" in question_lower and "night" not in text:
        gaps.append("- Night-time ODD evidence was requested but not found in the retrieved chunks.")
    if ("occluded" in question_lower or "occlusion" in question_lower) and "occlusion" not in text and "occluded" not in text:
        gaps.append("- Occlusion coverage was requested but not found in the retrieved chunks.")
    if not gaps:
        gaps.append("- No major gap was detected heuristically, but a human review should confirm clause-level coverage and evidence quality.")
    return gaps


def _query_terms(question: str) -> set[str]:
    return {
        term
        for term in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", question.lower())
        if term not in {"the", "and", "for", "with", "that", "this", "are", "from", "into", "shall"}
    }


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _missing_requirements(question: str, chunks) -> list[str]:
    text = " ".join(chunk.text.lower() for chunk in chunks)
    gaps: list[str] = []
    if "night" in question.lower() and "night" not in text:
        gaps.append("REQ-GAP-NIGHT-001: The system shall define night-time ODD coverage and validation evidence.")
    if "occluded" in question.lower() and "occlusion" not in text and "occluded" not in text:
        gaps.append("REQ-GAP-OCCLUSION-001: The system shall specify detection performance for partially occluded vulnerable road users.")
    if "range" not in text and "detect" in text:
        gaps.append("REQ-GAP-MEAS-001: The system shall specify measurable detection range, speed range, and confidence threshold.")
    if not gaps:
        gaps.append("REQ-GAP-REVIEW-001: The project shall link each safety requirement to a hazard, safety goal, verification method, and objective evidence.")
    return gaps


def _query_quality_score(chunks, missing_requirements: list[str]) -> float:
    if not chunks:
        return 0.25
    score = 0.85
    if missing_requirements:
        score -= min(0.3, 0.08 * len(missing_requirements))
    return round(max(score, 0.0), 2)


def _estimate_text_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, int(len(text.split()) * 1.35))


def _extract_project_requirements(project_id: int) -> list[Requirement]:
    raw = get_project_vector_store().get(where={"project_id": str(project_id)}, include=["documents", "metadatas"])
    requirements: list[Requirement] = []
    for text, metadata in zip(raw.get("documents", []), raw.get("metadatas", []), strict=False):
        source = metadata.get("document") if metadata else None
        requirements.extend(extract_requirements_from_text(text, source))
    return requirements


def _replace_requirements(project_id: int, requirements: list[Requirement], session: Session) -> None:
    for record in session.exec(select(RequirementRecord).where(RequirementRecord.project_id == project_id)).all():
        session.delete(record)
    seen: set[str] = set()
    for req in requirements:
        if req.id in seen:
            continue
        seen.add(req.id)
        session.add(
            RequirementRecord(
                project_id=project_id,
                requirement_id=req.id,
                requirement_type=req.type.value,
                text=req.text,
                linked_hazard=req.linked_hazard,
                linked_safety_goal=req.linked_safety_goal,
                quality_score=req.quality_score,
                quality_issues=req.quality_issues,
                suggested_improvement=req.suggested_improvement,
                linked_test_cases=req.linked_test_cases,
                evidence_source=req.evidence_source,
            )
        )
    session.commit()


def _stored_requirements(project_id: int, session: Session) -> list[Requirement]:
    records = session.exec(select(RequirementRecord).where(RequirementRecord.project_id == project_id)).all()
    return [
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
        for record in records
    ]
