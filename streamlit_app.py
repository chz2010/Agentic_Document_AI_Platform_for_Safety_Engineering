"""Streamlit frontend for the Agentic Document AI Platform."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import streamlit as st


DEFAULT_API_URL = os.getenv("SAFETY_BACKEND_API_URL", "http://127.0.0.1:8000")
SEED_DOCUMENT = Path(__file__).parent / "datasets" / "seed_requirements" / "automotive_safety_requirements.md"


st.set_page_config(
    page_title="Agentic Document AI Platform",
    page_icon="SA",
    layout="wide",
)


st.markdown(
    """
    <style>
    .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
    div[data-testid="stMetric"] {
        border: 1px solid #d7dde8;
        border-radius: 8px;
        padding: 0.7rem 0.8rem;
        background: #f8fafc;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #d7dde8;
        border-radius: 8px;
    }
    .small-muted {color: #5f6b7a; font-size: 0.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def api_request(method: str, path: str, **kwargs: Any) -> Any:
    base_url = st.session_state.get("api_url", DEFAULT_API_URL).rstrip("/")
    try:
        response = requests.request(method, f"{base_url}{path}", timeout=60, **kwargs)
    except requests.RequestException as exc:
        st.error(f"Backend connection failed: {exc}")
        st.stop()
    if response.status_code >= 400:
        detail = _safe_json(response).get("detail", response.text)
        st.error(f"API error {response.status_code}: {detail}")
        st.stop()
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        return response.json()
    return response.text


def _safe_json(response: requests.Response) -> dict[str, Any]:
    try:
        return response.json()
    except ValueError:
        return {}


def dataframe(rows: list[dict[str, Any]], columns: list[str] | None = None) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=columns or [])
    frame = pd.DataFrame(rows)
    if columns:
        existing = [column for column in columns if column in frame.columns]
        frame = frame[existing]
    return frame


def health_ok() -> bool:
    try:
        response = requests.get(f"{st.session_state.api_url.rstrip('/')}/health", timeout=5)
    except requests.RequestException:
        return False
    return response.status_code == 200


def load_projects() -> list[dict[str, Any]]:
    return api_request("GET", "/projects")


def selected_project(projects: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not projects:
        return None
    project_options = {
        f"{project['id']} - {project['name']}": project
        for project in projects
    }
    selected_label = st.sidebar.selectbox("Active project", list(project_options.keys()))
    return project_options[selected_label]


def create_seed_demo_project() -> dict[str, Any]:
    project = api_request(
        "POST",
        "/projects",
        json={
            "name": "Seed Demo - AEB and Perception Safety Requirements",
            "domain": "Autonomous driving",
            "system_type": "ADAS safety engineering",
            "standards_scope": ["ISO 26262", "ISO 21448", "ISO 8800"],
            "description": "Demo project populated from the tracked seed requirements document.",
        },
    )
    if SEED_DOCUMENT.exists():
        with SEED_DOCUMENT.open("rb") as handle:
            api_request(
                "POST",
                f"/projects/{project['id']}/documents",
                files={"file": (SEED_DOCUMENT.name, handle, "text/markdown")},
            )
        api_request("POST", f"/projects/{project['id']}/requirements/extract")
    return project


def render_project_sidebar() -> dict[str, Any] | None:
    st.sidebar.header("Workspace")
    st.sidebar.text_input("Backend API", key="api_url", value=DEFAULT_API_URL)
    st.sidebar.caption("FastAPI must be running before the UI can load data.")
    if not health_ok():
        st.sidebar.error("Backend offline")
        st.info("Start the backend with: `.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000`")
        st.stop()
    st.sidebar.success("Backend online")

    with st.sidebar.expander("Create project", expanded=False):
        with st.form("create_project"):
            name = st.text_input("Project name", value="AEB Pedestrian Safety Case")
            domain = st.text_input("Domain", value="Autonomous driving")
            system_type = st.text_input("System type", value="AEB")
            standards = st.multiselect(
                "Standards scope",
                ["ISO 26262", "ISO 21448", "ISO 8800", "NCAP", "IIHS"],
                default=["ISO 26262", "ISO 21448", "ISO 8800"],
            )
            description = st.text_area("Description", value="Safety engineering workspace for AEB pedestrian detection.")
            submitted = st.form_submit_button("Create")
        if submitted:
            api_request(
                "POST",
                "/projects",
                json={
                    "name": name,
                    "domain": domain,
                    "system_type": system_type,
                    "standards_scope": standards,
                    "description": description,
                },
            )
            st.rerun()

    if st.sidebar.button("Load seed demo", use_container_width=True):
        create_seed_demo_project()
        st.rerun()

    projects = load_projects()
    if not projects:
        st.warning("No projects yet. Create a project or load the seed demo from the sidebar.")
        return None
    return selected_project(projects)


def render_overview(project: dict[str, Any]) -> None:
    docs = api_request("GET", f"/projects/{project['id']}/documents")
    runs = api_request("GET", f"/projects/{project['id']}/evaluation-runs")
    dashboard = api_request("GET", f"/projects/{project['id']}/agent-operations/dashboard")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Documents", len(docs))
    col2.metric("Evaluation runs", len(runs))
    col3.metric("Agent runs", dashboard["total_runs"])
    col4.metric("Escalation rate", f"{dashboard['escalation_rate']:.0%}")

    st.subheader("Project")
    st.write(project.get("description") or "No description.")
    st.dataframe(
        dataframe(docs, ["id", "filename", "source_type", "chunk_count", "created_at"]),
        use_container_width=True,
        hide_index=True,
    )


def render_documents(project: dict[str, Any]) -> None:
    st.subheader("Upload Project Documents")
    uploaded = st.file_uploader("PDF, TXT, Markdown, CSV, or DOCX", type=["pdf", "txt", "md", "markdown", "csv", "docx"])
    if uploaded and st.button("Upload and index document", type="primary"):
        api_request(
            "POST",
            f"/projects/{project['id']}/documents",
            files={"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")},
        )
        st.success("Document uploaded, chunked, embedded, and indexed.")
        st.rerun()

    docs = api_request("GET", f"/projects/{project['id']}/documents")
    st.dataframe(
        dataframe(docs, ["id", "filename", "source_type", "chunk_count", "created_at"]),
        use_container_width=True,
        hide_index=True,
    )


def render_query(project: dict[str, Any]) -> None:
    st.subheader("Ask a Safety or Requirements Question")
    question = st.text_area(
        "Question",
        value="Are the requirements complete for occluded pedestrian detection at night?",
        height=90,
    )
    standards = st.multiselect(
        "Standards context",
        ["ISO 26262", "ISO 21448", "ISO 8800", "NCAP", "IIHS"],
        default=["ISO 26262", "ISO 21448", "ISO 8800"],
    )
    include_review = st.checkbox("Include requirements review", value=True)

    if st.button("Run analysis", type="primary"):
        result = api_request(
            "POST",
            f"/projects/{project['id']}/query",
            json={
                "question": question,
                "standards": standards,
                "include_requirements_review": include_review,
            },
        )
        st.session_state["last_query_result"] = result

    result = st.session_state.get("last_query_result")
    if result:
        st.markdown("#### Answer")
        st.write(result["answer"])
        if result.get("missing_requirements"):
            st.markdown("#### Missing Requirements")
            for item in result["missing_requirements"]:
                st.warning(item)
        if result.get("recommended_requirements"):
            st.markdown("#### Recommended Requirements")
            st.dataframe(dataframe(result["recommended_requirements"]), use_container_width=True, hide_index=True)
        st.markdown("#### Retrieved Evidence")
        st.dataframe(
            dataframe(result["retrieved_sources"], ["document", "page", "section", "chunk_id", "text"]),
            use_container_width=True,
            hide_index=True,
        )


def render_requirements(project: dict[str, Any]) -> None:
    st.subheader("Requirements Engineering")
    actions = st.columns(3)
    if actions[0].button("Extract requirements", type="primary", use_container_width=True):
        st.session_state["requirements_result"] = api_request("POST", f"/projects/{project['id']}/requirements/extract")
    if actions[1].button("Evaluate quality", use_container_width=True):
        st.session_state["requirements_result"] = api_request("POST", f"/projects/{project['id']}/requirements/evaluate", json={})
    if actions[2].button("Generate test cases", use_container_width=True):
        st.session_state["test_cases"] = api_request("POST", f"/projects/{project['id']}/test-cases/generate")

    result = st.session_state.get("requirements_result")
    if result:
        summary = result.get("quality_summary", {})
        c1, c2, c3 = st.columns(3)
        c1.metric("Requirements", summary.get("count", 0))
        c2.metric("Average quality", summary.get("average_quality_score", 0.0))
        c3.metric("Common issues", len(summary.get("common_issues", [])))
        if summary.get("common_issues"):
            st.caption("Most common issues: " + ", ".join(summary["common_issues"]))
        st.dataframe(
            dataframe(
                result.get("requirements", []),
                ["id", "type", "quality_score", "quality_issues", "linked_hazard", "linked_safety_goal", "text"],
            ),
            use_container_width=True,
            hide_index=True,
        )

    if st.session_state.get("test_cases"):
        st.markdown("#### Generated Test Cases")
        st.dataframe(dataframe(st.session_state["test_cases"]), use_container_width=True, hide_index=True)


def render_traceability(project: dict[str, Any]) -> None:
    st.subheader("Traceability Matrix")
    rows = api_request("GET", f"/projects/{project['id']}/traceability")
    st.dataframe(
        dataframe(
            rows,
            [
                "hazard_id",
                "safety_goal_id",
                "requirement_id",
                "requirement_type",
                "test_case_id",
                "status",
                "quality_score",
                "requirement_text",
            ],
        ),
        use_container_width=True,
        hide_index=True,
    )
    csv_text = api_request("GET", f"/projects/{project['id']}/traceability?format=csv")
    st.download_button("Download traceability CSV", csv_text, "traceability_matrix.csv", "text/csv")


def render_agent_ops(project: dict[str, Any]) -> None:
    st.subheader("Agent Operations")
    dashboard = api_request("GET", f"/projects/{project['id']}/agent-operations/dashboard")
    cols = st.columns(5)
    cols[0].metric("Success rate", f"{dashboard['success_rate']:.0%}")
    cols[1].metric("Escalation rate", f"{dashboard['escalation_rate']:.0%}")
    cols[2].metric("Average latency", f"{dashboard['average_latency_ms']:.0f} ms")
    cols[3].metric("Average cost", f"${dashboard['average_cost_usd']:.4f}")
    cols[4].metric("Pending approvals", dashboard["approval_pending_count"])

    with st.form("agent_tool_run"):
        request = st.text_area("Agent request", value="Review low-confidence requirements and create a ticket if human review is needed.")
        confidence = st.slider("Confidence score", 0.0, 1.0, 0.72, 0.01)
        risk = st.selectbox("Hallucination risk", ["low", "medium", "high", "critical"], index=2)
        submitted = st.form_submit_button("Run tool orchestration")
    if submitted:
        st.session_state["tool_result"] = api_request(
            "POST",
            f"/projects/{project['id']}/agent-tools/run",
            json={
                "user_request": request,
                "confidence_score": confidence,
                "hallucination_risk": risk,
                "tools": [
                    "search_project_docs",
                    "evaluate_requirements",
                    "generate_traceability",
                    "generate_test_cases",
                    "create_issue_ticket",
                ],
            },
        )
        st.rerun()

    if st.session_state.get("tool_result"):
        st.markdown("#### Last Orchestration Result")
        st.json(st.session_state["tool_result"], expanded=False)

    runs = api_request("GET", f"/projects/{project['id']}/agent-runs")
    st.markdown("#### Run Logs")
    st.dataframe(
        dataframe(
            runs,
            [
                "agent_run_id",
                "operation_name",
                "status",
                "model_used",
                "latency_ms",
                "estimated_cost_usd",
                "approval_required",
                "approval_status",
                "human_escalation_required",
                "evaluation_score",
                "created_at",
            ],
        ),
        use_container_width=True,
        hide_index=True,
    )


def render_reports(project: dict[str, Any]) -> None:
    st.subheader("Reports")
    markdown_report = api_request("GET", f"/projects/{project['id']}/report?format=markdown")
    st.download_button("Download Markdown report", markdown_report, "safety_requirements_report.md", "text/markdown")
    st.download_button(
        "Download requirements CSV",
        api_request("GET", f"/projects/{project['id']}/report?format=requirements_csv"),
        "requirements.csv",
        "text/csv",
    )
    st.download_button(
        "Download traceability CSV",
        api_request("GET", f"/projects/{project['id']}/report?format=traceability_csv"),
        "traceability.csv",
        "text/csv",
    )
    st.markdown("#### Preview")
    st.markdown(markdown_report)


st.title("Agentic Document AI Platform for Safety Engineering")
st.caption("FastAPI backend UI for project-specific RAG, requirements engineering, traceability, and agent operations.")

project = render_project_sidebar()
if project:
    st.markdown(f"### {project['name']}")
    st.markdown(
        f"<div class='small-muted'>{project['domain']} | {project['system_type']} | "
        f"Standards: {', '.join(project.get('standards_scope', []))}</div>",
        unsafe_allow_html=True,
    )
    tabs = st.tabs(["Overview", "Documents", "Ask", "Requirements", "Traceability", "Agent Ops", "Reports"])
    with tabs[0]:
        render_overview(project)
    with tabs[1]:
        render_documents(project)
    with tabs[2]:
        render_query(project)
    with tabs[3]:
        render_requirements(project)
    with tabs[4]:
        render_traceability(project)
    with tabs[5]:
        render_agent_ops(project)
    with tabs[6]:
        render_reports(project)
