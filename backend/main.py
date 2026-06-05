"""FastAPI application for project workspaces, document RAG, and requirements engineering."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse
from langchain_core.documents import Document as LangchainDocument
from openai import OpenAI
from sqlmodel import Session, select

from backend.agent_operations import build_operations_dashboard, create_agent_run_log, create_integration_event, run_mock_tool, update_approval
from backend.database import get_session, init_db
from backend.document_processing import chunk_documents, extract_documents
from backend.models import AgentRunLogRecord, DocumentChunk, EvaluationRunRecord, IntegrationEventRecord, Project, ProjectDocument, RequirementRecord, TestCaseRecord
from backend.reporting import markdown_report, requirements_csv, traceability_csv
from backend.requirements_engineering import build_traceability, extract_requirements_from_text, generate_test_cases, quality_summary
from backend.schemas import (
    AgentApprovalUpdate,
    AgentOperationsDashboard,
    AgentRunLogCreate,
    AgentRunLogRead,
    DocumentRead,
    EvaluationRun,
    IntegrationEventCreate,
    IntegrationEventRead,
    ProjectCreate,
    ProjectRead,
    QueryRequest,
    QueryResponse,
    Requirement,
    RequirementEvaluateRequest,
    RequirementExtractionResponse,
    SafetyAnalysis,
    TestCase,
    TraceabilityLink,
    ToolOrchestrationRequest,
    ToolOrchestrationResponse,
)
from backend.settings import settings
from backend.vector_store import get_project_vector_store


app = FastAPI(
    title="Agentic Document AI Platform for Safety Engineering API",
    version="0.1.0",
    description="Agentic Document AI and requirements engineering backend for safety engineering workflows.",
)


@app.on_event("startup")
def on_startup() -> None:
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    Path(settings.project_chroma_path).mkdir(parents=True, exist_ok=True)
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


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
    answer = _answer_from_context(payload.question, retrieved, payload.standards)
    missing_requirements: list[str] = []
    recommended_requirements: list[Requirement] = []
    if payload.include_requirements_review:
        missing_requirements = _missing_requirements(payload.question, retrieved)
        recommended_requirements = extract_requirements_from_text("\n".join(missing_requirements), "generated_from_query")

    latency_ms = int((time.perf_counter() - started) * 1000)
    run = EvaluationRunRecord(
        project_id=project_id,
        run_type="query",
        model_used=settings.llm_model if settings.openai_api_key else "local-evidence-synthesis",
        query=payload.question,
        answer=answer,
        retrieved_chunk_count=len(retrieved),
        latency_ms=latency_ms,
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
            token_usage=run.token_usage,
            estimated_cost_usd=0.0,
            confidence_score=run_quality_score,
            hallucination_risk="low" if retrieved else "high",
            hallucination_flags=[] if retrieved else ["no_retrieved_evidence"],
            evaluation_score=run_quality_score,
            metadata={
                "retrieved_chunk_count": len(retrieved),
                "include_requirements_review": payload.include_requirements_review,
                "standards": payload.standards,
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
    session: Session = Depends(get_session),
) -> list[AgentRunLogRead]:
    _project_or_404(project_id, session)
    statement = select(AgentRunLogRecord).where(AgentRunLogRecord.project_id == project_id)
    if approval_status:
        statement = statement.where(AgentRunLogRecord.approval_status == approval_status)
    if human_escalation_required is not None:
        statement = statement.where(AgentRunLogRecord.human_escalation_required == human_escalation_required)
    return [_agent_run_read(record) for record in session.exec(statement.order_by(AgentRunLogRecord.created_at.desc())).all()]


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
            metadata={"tool_results": tool_results},
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


@app.get("/projects/{project_id}/agent-operations/dashboard", response_model=AgentOperationsDashboard)
def get_agent_operations_dashboard(project_id: int, session: Session = Depends(get_session)) -> AgentOperationsDashboard:
    _project_or_404(project_id, session)
    return build_operations_dashboard(project_id, session)


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


def _answer_from_context(question: str, chunks, standards: list[str]) -> str:
    context = "\n\n".join(f"[{chunk.document} p.{chunk.page}] {chunk.text}" for chunk in chunks)
    if settings.openai_api_key and settings.use_openai_generation:
        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "You are an autonomous-driving safety analyst. Answer only from supplied evidence and name gaps clearly."},
                {"role": "user", "content": f"Question: {question}\nStandards scope: {', '.join(standards) or 'project documents only'}\nEvidence:\n{context}"},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content or ""
    if not chunks:
        return "No project-specific evidence was retrieved. Upload documents or broaden the question."
    return (
        f"Based on {len(chunks)} retrieved project chunks, the evidence partially addresses the question: {question}\n\n"
        f"Most relevant evidence: {chunks[0].text[:900]}"
    )


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
