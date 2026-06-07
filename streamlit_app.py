"""Streamlit frontend for the Agentic Document AI Platform."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any

import altair as alt
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
        border: 1px solid #384152;
        border-radius: 8px;
        padding: 0.7rem 0.8rem;
        background: #141923;
        color: #f5f7fb;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] div {
        color: #f5f7fb;
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid #384152;
        border-radius: 8px;
    }
    .wrapped-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        margin: 0.75rem 0 1.25rem 0;
        border: 1px solid #384152;
        border-radius: 8px;
        overflow: hidden;
        display: table;
    }
    .wrapped-table th {
        background: #1b2230;
        color: #f5f7fb;
        font-weight: 650;
        text-align: left;
        padding: 0.65rem;
        border-bottom: 1px solid #384152;
        vertical-align: top;
    }
    .wrapped-table td {
        color: #edf2f7;
        padding: 0.65rem;
        border-top: 1px solid #293241;
        vertical-align: top;
        white-space: normal;
        overflow-wrap: anywhere;
        word-break: break-word;
        line-height: 1.35;
    }
    .wrapped-table tr:nth-child(even) td {
        background: #111722;
    }
    .wrapped-table tr:nth-child(odd) td {
        background: #0d111a;
    }
    .col-id {width: 9%;}
    .col-score {width: 7%;}
    .col-small {width: 11%;}
    .col-medium {width: 16%;}
    .col-large {width: 24%;}
    .col-text {width: 36%;}
    .small-muted {color: #aab4c3; font-size: 0.9rem;}
    .ops-result-banner {
        border: 1px solid #384152;
        border-radius: 8px;
        background: #121824;
        padding: 1rem;
        margin: 0.75rem 0 1rem 0;
    }
    .ops-result-title {
        color: #f5f7fb;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .ops-result-subtitle {
        color: #aab4c3;
        font-size: 0.92rem;
        line-height: 1.4;
    }
    .status-pill {
        display: inline-block;
        border-radius: 999px;
        padding: 0.25rem 0.65rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
        font-size: 0.82rem;
        font-weight: 700;
        border: 1px solid #384152;
    }
    .pill-ok {background: #123024; color: #7ee2a8; border-color: #1f7a4f;}
    .pill-warn {background: #332712; color: #ffd37a; border-color: #8a661d;}
    .pill-bad {background: #351a20; color: #ff9ba7; border-color: #93404d;}
    .pill-neutral {background: #1b2230; color: #cbd5e1; border-color: #465267;}
    .tool-panel {
        border: 1px solid #384152;
        border-radius: 8px;
        background: #0d111a;
        padding: 0.85rem;
        margin: 0.5rem 0 0.85rem 0;
    }
    .tool-panel-title {
        color: #f5f7fb;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .tool-panel-body {
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.45;
    }
    .grafana-hero {
        border: 1px solid #384152;
        border-radius: 8px;
        background: #101620;
        padding: 1rem;
        margin: 0.75rem 0 1rem 0;
    }
    .grafana-kicker {
        color: #8ea0b8;
        font-size: 0.78rem;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 0;
        margin-bottom: 0.25rem;
    }
    .grafana-title {
        color: #f5f7fb;
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    .grafana-subtitle {
        color: #aab4c3;
        font-size: 0.92rem;
        line-height: 1.4;
    }
    .grafana-stat {
        border: 1px solid #384152;
        border-radius: 8px;
        background: #0d111a;
        padding: 0.85rem;
        min-height: 92px;
    }
    .grafana-stat-label {
        color: #8ea0b8;
        font-size: 0.78rem;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 0;
    }
    .grafana-stat-value {
        color: #f5f7fb;
        font-size: 1.75rem;
        font-weight: 800;
        margin-top: 0.2rem;
    }
    .grafana-stat-note {
        color: #aab4c3;
        font-size: 0.82rem;
        margin-top: 0.15rem;
    }
    .grafana-panel-title {
        color: #f5f7fb;
        font-size: 0.98rem;
        font-weight: 800;
        margin: 1rem 0 0.35rem 0;
    }
    .report-cover {
        border: 1px solid #384152;
        border-radius: 8px;
        background: #101620;
        padding: 1rem;
        margin: 0.75rem 0 1rem 0;
    }
    .report-label {
        color: #8ea0b8;
        font-size: 0.78rem;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 0;
        margin-bottom: 0.25rem;
    }
    .report-title {
        color: #f5f7fb;
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }
    .report-subtitle {
        color: #aab4c3;
        font-size: 0.92rem;
        line-height: 1.4;
    }
    .report-section {
        border-top: 1px solid #293241;
        margin-top: 1.1rem;
        padding-top: 0.75rem;
    }
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


def output_tokens_from_usage(token_usage: Any) -> int:
    if not isinstance(token_usage, dict):
        return 0
    return int(token_usage.get("completion_tokens") or token_usage.get("output_tokens") or 0)


def grafana_stat(label: str, value: str | int | float, note: str = "") -> None:
    st.markdown(
        "<div class='grafana-stat'>"
        f"<div class='grafana-stat-label'>{html.escape(label)}</div>"
        f"<div class='grafana-stat-value'>{html.escape(str(value))}</div>"
        f"<div class='grafana-stat-note'>{html.escape(note)}</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def horizontal_bar_chart(
    rows: list[dict[str, Any]] | pd.DataFrame,
    x: str,
    y: str,
    title: str,
    *,
    color: str | None = None,
    height: int = 260,
    x_title: str | None = None,
    y_title: str | None = None,
) -> None:
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    if frame.empty or x not in frame.columns or y not in frame.columns:
        st.info(f"No data available for {title.lower()}.")
        return

    chart = (
        alt.Chart(frame)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X(f"{x}:Q", title=x_title or x.replace("_", " ").title()),
            y=alt.Y(
                f"{y}:N",
                sort="-x",
                title=y_title or y.replace("_", " ").title(),
                axis=alt.Axis(labelLimit=420),
            ),
            tooltip=[alt.Tooltip(column, title=column.replace("_", " ").title()) for column in frame.columns],
        )
        .properties(title=title, height=max(height, min(520, 42 * len(frame) + 70)))
    )
    if color and color in frame.columns:
        chart = chart.encode(color=alt.Color(f"{color}:N", legend=alt.Legend(title=color.replace("_", " ").title())))
    chart = chart.configure_axis(
        labelColor="#cbd5e1",
        titleColor="#aab4c3",
        gridColor="#2a3344",
    ).configure_title(color="#f5f7fb", fontSize=14, anchor="start")
    st.altair_chart(chart, use_container_width=True)


def donut_chart(rows: list[dict[str, Any]] | pd.DataFrame, theta: str, color: str, title: str) -> None:
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    if frame.empty or theta not in frame.columns or color not in frame.columns:
        st.info(f"No data available for {title.lower()}.")
        return

    chart = (
        alt.Chart(frame)
        .mark_arc(innerRadius=62, outerRadius=104)
        .encode(
            theta=alt.Theta(f"{theta}:Q", title="Count"),
            color=alt.Color(f"{color}:N", legend=alt.Legend(title=color.replace("_", " ").title())),
            tooltip=[alt.Tooltip(color, title=color.replace("_", " ").title()), alt.Tooltip(theta, title="Count")],
        )
        .properties(title=title, height=280)
    )
    chart = chart.configure_title(color="#f5f7fb", fontSize=14, anchor="start")
    st.altair_chart(chart, use_container_width=True)


def line_chart(
    rows: list[dict[str, Any]] | pd.DataFrame,
    x: str,
    y: str,
    title: str,
    *,
    color: str | None = None,
    y_title: str | None = None,
) -> None:
    frame = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    if frame.empty or x not in frame.columns or y not in frame.columns:
        st.info(f"No data available for {title.lower()}.")
        return

    chart = (
        alt.Chart(frame)
        .mark_line(point=True)
        .encode(
            x=alt.X(f"{x}:T", title="Run time"),
            y=alt.Y(f"{y}:Q", title=y_title or y.replace("_", " ").title()),
            tooltip=[alt.Tooltip(column, title=column.replace("_", " ").title()) for column in frame.columns],
        )
        .properties(title=title, height=260)
    )
    if color and color in frame.columns:
        chart = chart.encode(color=alt.Color(f"{color}:N", legend=alt.Legend(title=color.replace("_", " ").title())))
    chart = chart.configure_axis(
        labelColor="#cbd5e1",
        titleColor="#aab4c3",
        gridColor="#2a3344",
    ).configure_title(color="#f5f7fb", fontSize=14, anchor="start")
    st.altair_chart(chart, use_container_width=True)


def wrapped_table(
    rows: list[dict[str, Any]] | pd.DataFrame,
    columns: list[str],
    labels: dict[str, str] | None = None,
    widths: dict[str, str] | None = None,
) -> None:
    frame = rows if isinstance(rows, pd.DataFrame) else dataframe(rows, columns)
    if frame.empty:
        st.info("No rows to display.")
        return

    labels = labels or {}
    widths = widths or {}
    header = "".join(
        f"<th class='{html.escape(widths.get(column, ''))}'>{html.escape(labels.get(column, column))}</th>"
        for column in columns
        if column in frame.columns
    )
    body_rows: list[str] = []
    for _, row in frame.iterrows():
        cells: list[str] = []
        for column in columns:
            if column not in frame.columns:
                continue
            value = row[column]
            if isinstance(value, list):
                value = ", ".join(str(item) for item in value)
            elif isinstance(value, dict):
                value = json.dumps(value, ensure_ascii=True, sort_keys=True)
            elif isinstance(value, float):
                value = f"{value:.2f}"
            elif pd.isna(value):
                value = ""
            cells.append(f"<td>{html.escape(str(value))}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    st.markdown(
        "<table class='wrapped-table'><thead><tr>"
        + header
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table>",
        unsafe_allow_html=True,
    )


def status_pill(label: str, variant: str = "neutral") -> str:
    css_class = {
        "ok": "pill-ok",
        "warn": "pill-warn",
        "bad": "pill-bad",
        "neutral": "pill-neutral",
    }.get(variant, "pill-neutral")
    return f"<span class='status-pill {css_class}'>{html.escape(label)}</span>"


def render_orchestration_result(result: dict[str, Any]) -> None:
    status = result.get("status", "unknown")
    approval_required = bool(result.get("approval_required"))
    escalation_required = bool(result.get("human_escalation_required"))
    status_variant = "ok" if status in {"resolved", "completed", "success"} else "warn"
    if status in {"blocked", "failed", "error"} or escalation_required:
        status_variant = "bad"

    st.markdown("#### Last Orchestration Result")
    st.markdown(
        "<div class='ops-result-banner'>"
        "<div class='ops-result-title'>Agent orchestration summary</div>"
        "<div>"
        + status_pill(f"Status: {status.replace('_', ' ').title()}", status_variant)
        + status_pill(
            "Approval required" if approval_required else "No approval required",
            "warn" if approval_required else "ok",
        )
        + status_pill(
            "Human escalation required" if escalation_required else "No human escalation",
            "bad" if escalation_required else "ok",
        )
        + "</div>"
        f"<div class='ops-result-subtitle'>Run ID {html.escape(str(result.get('agent_run_id', 'n/a')))} "
        f"executed {len(result.get('tools_used') or [])} tools: "
        f"{html.escape(', '.join(result.get('tools_used') or []))}.</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    summary_cols = st.columns(4)
    summary_cols[0].metric("Run ID", result.get("agent_run_id", "n/a"))
    summary_cols[1].metric("Tools executed", len(result.get("tools_used") or []))
    summary_cols[2].metric("Approval gate", "Required" if approval_required else "Clear")
    summary_cols[3].metric("Escalation", "Required" if escalation_required else "Clear")

    tool_results = result.get("tool_results") or {}
    if not tool_results:
        st.info("No tool output was returned.")
        return

    tool_rows = []
    for tool_name, payload in tool_results.items():
        tool_rows.append({"tool": tool_name, "result": summarize_tool_result(tool_name, payload)})
    wrapped_table(
        tool_rows,
        ["tool", "result"],
        labels={"tool": "Tool", "result": "Result summary"},
        widths={"tool": "col-medium", "result": "col-text"},
    )

    for tool_name, payload in tool_results.items():
        render_tool_result_panel(tool_name, payload)


def summarize_tool_result(tool_name: str, payload: Any) -> str:
    if not isinstance(payload, dict):
        return str(payload)
    if tool_name == "search_project_docs":
        docs = payload.get("retrieved_docs") or []
        return f"Retrieved {len(docs)} project document matches for query: {payload.get('query', '')}"
    if tool_name == "extract_requirements":
        return f"Found {payload.get('requirements_found', 0)} stored requirements."
    if tool_name == "evaluate_requirements":
        return (
            f"Evaluated {payload.get('requirement_count', 0)} requirements with "
            f"average quality score {float(payload.get('average_quality_score') or 0.0):.2f}."
        )
    if tool_name == "generate_traceability":
        return f"Prepared {payload.get('traceability_rows', 0)} traceability rows."
    if tool_name == "generate_test_cases":
        return f"Found {payload.get('test_cases', 0)} generated test cases."
    if tool_name == "create_issue_ticket":
        return f"Created local ticket {payload.get('ticket_id', 'n/a')} with status {payload.get('status', 'unknown')}."
    if "error" in payload:
        return str(payload["error"])
    return json.dumps(payload, ensure_ascii=True, sort_keys=True)


def render_tool_result_panel(tool_name: str, payload: Any) -> None:
    st.markdown(
        "<div class='tool-panel'>"
        f"<div class='tool-panel-title'>{html.escape(tool_name.replace('_', ' ').title())}</div>"
        f"<div class='tool-panel-body'>{html.escape(summarize_tool_result(tool_name, payload))}</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    if not isinstance(payload, dict):
        return

    if tool_name == "search_project_docs":
        docs = payload.get("retrieved_docs") or []
        if docs:
            rows = [
                {
                    "score": doc.get("score"),
                    "source": doc.get("source"),
                    "title": doc.get("title"),
                    "snippet": doc.get("snippet"),
                }
                for doc in docs[:5]
            ]
            horizontal_bar_chart(
                [{"title": row["title"], "score": float(row.get("score") or 0.0), "source": row.get("source")} for row in rows],
                "score",
                "title",
                "Retrieved Evidence Scores",
                color="source",
                x_title="Relevance score",
                y_title="Evidence",
            )
            wrapped_table(
                rows,
                ["score", "source", "title", "snippet"],
                labels={"score": "Score", "source": "Source", "title": "Title", "snippet": "Evidence snippet"},
                widths={"score": "col-score", "source": "col-small", "title": "col-medium", "snippet": "col-text"},
            )
        return

    if tool_name == "evaluate_requirements":
        metric_cols = st.columns(2)
        metric_cols[0].metric("Requirements evaluated", payload.get("requirement_count", 0))
        metric_cols[1].metric("Average quality", f"{float(payload.get('average_quality_score') or 0.0):.2f}")
        return

    if tool_name == "create_issue_ticket":
        metric_cols = st.columns(2)
        metric_cols[0].metric("Ticket ID", payload.get("ticket_id", "n/a"))
        metric_cols[1].metric("Ticket status", payload.get("status", "unknown"))
        return

    if tool_name in {"extract_requirements", "generate_traceability", "generate_test_cases"}:
        metric_name = {
            "extract_requirements": "Requirements found",
            "generate_traceability": "Traceability rows",
            "generate_test_cases": "Test cases",
        }[tool_name]
        value_key = {
            "extract_requirements": "requirements_found",
            "generate_traceability": "traceability_rows",
            "generate_test_cases": "test_cases",
        }[tool_name]
        st.metric(metric_name, payload.get(value_key, 0))
        return

    with st.expander(f"Raw {tool_name} payload", expanded=False):
        st.json(payload)


def stored_requirements(project_id: int) -> list[dict[str, Any]]:
    result = api_request("POST", f"/projects/{project_id}/requirements/evaluate", json={})
    return result.get("requirements", [])


def quality_review(requirements: list[dict[str, Any]]) -> dict[str, Any]:
    if not requirements:
        return {
            "count": 0,
            "average_quality": 0.0,
            "ready_count": 0,
            "needs_review_count": 0,
            "hazard_coverage": 0.0,
            "safety_goal_coverage": 0.0,
            "test_case_coverage": 0.0,
            "issue_counts": {},
            "needs_review": [],
        }

    issue_counts: dict[str, int] = {}
    needs_review: list[dict[str, Any]] = []
    for req in requirements:
        issues = req.get("quality_issues") or []
        for issue in issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        if issues or float(req.get("quality_score") or 0.0) < 0.75:
            needs_review.append(req)

    count = len(requirements)
    return {
        "count": count,
        "average_quality": round(sum(float(req.get("quality_score") or 0.0) for req in requirements) / count, 2),
        "ready_count": count - len(needs_review),
        "needs_review_count": len(needs_review),
        "hazard_coverage": sum(1 for req in requirements if req.get("linked_hazard")) / count,
        "safety_goal_coverage": sum(1 for req in requirements if req.get("linked_safety_goal")) / count,
        "test_case_coverage": sum(1 for req in requirements if req.get("linked_test_cases")) / count,
        "issue_counts": dict(sorted(issue_counts.items(), key=lambda item: item[1], reverse=True)),
        "needs_review": needs_review,
    }


def backend_health() -> dict[str, Any] | None:
    try:
        response = requests.get(f"{st.session_state.api_url.rstrip('/')}/health", timeout=5)
    except requests.RequestException:
        return None
    if response.status_code != 200:
        return None
    return response.json()


def health_ok() -> bool:
    return backend_health() is not None


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
    health = backend_health()
    if not health:
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
    project = selected_project(projects)
    if project:
        with st.sidebar.expander("Delete active project", expanded=False):
            st.caption("This removes the project, documents, runs, requirements, workflow items, and local vector entries.")
            confirmation = st.text_input("Type the project ID to confirm", key=f"delete_project_confirm_{project['id']}")
            if st.button("Delete project", use_container_width=True, key=f"delete_project_{project['id']}"):
                if confirmation.strip() == str(project["id"]):
                    api_request("DELETE", f"/projects/{project['id']}")
                    st.session_state.pop("last_query_result", None)
                    st.session_state.pop("retrieval_result", None)
                    st.session_state.pop("precision_result", None)
                    st.session_state.pop("tool_result", None)
                    st.success("Project deleted.")
                    st.rerun()
                else:
                    st.error("Project ID confirmation does not match.")
    return project


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
    answer_engine_options = {
        "OpenAI model": "openai",
        "Local model": "local",
        "Deterministic evidence synthesis": "none",
    }
    answer_engine = st.selectbox(
        "Answer engine",
        list(answer_engine_options.keys()),
        help="Choose how the final answer is synthesized after project-specific retrieval.",
    )
    answer_mode = answer_engine_options[answer_engine]
    answer_model = None
    if answer_mode == "openai":
        openai_model_options = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "Custom"]
        selected_model = st.selectbox("OpenAI model", openai_model_options)
        if selected_model == "Custom":
            answer_model = st.text_input("Custom OpenAI model", value="gpt-4o-mini")
        else:
            answer_model = selected_model
    elif answer_mode == "local":
        local_model_options = ["qwen2.5:7b-instruct", "llama3.1:8b", "mistral:7b", "Custom"]
        selected_model = st.selectbox("Local model", local_model_options)
        if selected_model == "Custom":
            answer_model = st.text_input("Custom local model", value="qwen2.5:7b-instruct")
        else:
            answer_model = selected_model

    if st.button("Run analysis", type="primary"):
        result = api_request(
            "POST",
            f"/projects/{project['id']}/query",
            json={
                "question": question,
                "standards": standards,
                "include_requirements_review": include_review,
                "answer_mode": answer_mode,
                "answer_model": answer_model,
            },
        )
        st.session_state["last_query_result"] = result

    result = st.session_state.get("last_query_result")
    if result:
        st.markdown("#### Answer")
        st.caption(f"Answer engine: {result.get('answer_mode', 'unknown')} | Model: {result.get('answer_model', 'unknown')}")
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


def render_retrieval(project: dict[str, Any]) -> None:
    st.subheader("Multi-Source Retrieval")
    query = st.text_input("Search query", value="night occluded pedestrian evidence")
    tool_labels = {
        "project_docs": "Project documents",
        "requirements": "Requirements",
        "traceability": "Traceability",
        "test_cases": "Test cases",
        "evaluation_runs": "Evaluation runs",
        "agent_runs": "Agent runs",
    }
    selected_labels = st.multiselect(
        "Retrieval sources",
        list(tool_labels.values()),
        default=list(tool_labels.values())[:4],
    )
    selected_tools = [tool for tool, label in tool_labels.items() if label in selected_labels]
    top_k = st.slider("Results per source", 1, 10, 5)

    if st.button("Search all selected sources", type="primary"):
        st.session_state["retrieval_result"] = api_request(
            "POST",
            f"/projects/{project['id']}/retrieval/search",
            json={"query": query, "tools": selected_tools, "top_k": top_k},
        )

    result = st.session_state.get("retrieval_result")
    if not result:
        return

    st.caption(f"Tools used: {', '.join(tool_labels.get(tool, tool) for tool in result['tools_used'])}")
    st.metric("Total results", result["total_results"])
    for tool in result["tools_used"]:
        label = tool_labels.get(tool, tool)
        rows = result["results_by_tool"].get(tool, [])
        st.markdown(f"#### {label}")
        if not rows:
            st.info("No results from this source.")
            continue
        display_rows = [
            {
                "source": row.get("source"),
                "score": row.get("score"),
                "title": row.get("title"),
                "snippet": row.get("snippet"),
                "metadata": row.get("metadata"),
            }
            for row in rows
        ]
        wrapped_table(
            display_rows,
            ["source", "score", "title", "snippet", "metadata"],
            labels={
                "source": "Source",
                "score": "Score",
                "title": "Title",
                "snippet": "Matched content",
                "metadata": "Metadata",
            },
            widths={
                "source": "col-small",
                "score": "col-score",
                "title": "col-medium",
                "snippet": "col-text",
                "metadata": "col-large",
            },
        )


def render_precision_review(project: dict[str, Any]) -> None:
    st.subheader("Precision Review")
    query = st.text_area(
        "Review question",
        value="Is night occluded pedestrian detection supported by evidence, requirements, traceability, and ISO clauses?",
        height=90,
    )
    standards = st.multiselect(
        "Standards for candidate clause references",
        ["ISO 26262", "ISO 21448", "ISO 8800"],
        default=project.get("standards_scope") or ["ISO 26262", "ISO 21448", "ISO 8800"],
    )
    top_k = st.slider("Evidence items", 1, 10, 5, key="precision_top_k")
    if st.button("Run precision review", type="primary"):
        st.session_state["precision_review"] = api_request(
            "POST",
            f"/projects/{project['id']}/analysis/precision-review",
            json={"query": query, "top_k": top_k, "standards": standards},
        )

    result = st.session_state.get("precision_review")
    if not result:
        return

    cols = st.columns(4)
    cols[0].metric("Confidence", f"{result['confidence_score']:.0%}")
    cols[1].metric("Routed tools", len(result["routed_tools"]))
    cols[2].metric("Citations", len(result["citations"]))
    cols[3].metric("Review items", len(result["human_review_queue"]))
    st.caption(result["confidence_rationale"])
    st.caption("Routed tools: " + ", ".join(result["routed_tools"]))

    st.markdown("#### Precision Evaluation Charts")
    chart_cols = st.columns(2)
    evidence_rows = [
        {
            "evidence": f"{item.get('source', 'source')} | {item.get('title', 'item')}",
            "score": float(item.get("score") or 0.0),
            "source": item.get("source", "unknown"),
        }
        for item in result.get("reranked_evidence", [])
    ]
    with chart_cols[0]:
        horizontal_bar_chart(
            evidence_rows,
            "score",
            "evidence",
            "Reranked Evidence Score",
            color="source",
            x_title="Relevance score",
            y_title="Evidence",
        )
    review_severity_rows = (
        pd.DataFrame(result.get("human_review_queue", []))
        .groupby("severity")
        .size()
        .reset_index(name="count")
        if result.get("human_review_queue")
        else pd.DataFrame(columns=["severity", "count"])
    )
    with chart_cols[1]:
        donut_chart(review_severity_rows, "count", "severity", "Human Review Severity")

    if result.get("iso_references"):
        st.markdown("#### Candidate ISO Clause References")
        iso_chart_rows = [
            {
                "reference": f"{item['standard']} {item['clause']}",
                "confidence": float(item.get("confidence") or 0.0),
                "standard": item["standard"],
            }
            for item in result["iso_references"]
        ]
        horizontal_bar_chart(
            iso_chart_rows,
            "confidence",
            "reference",
            "Candidate ISO Reference Confidence",
            color="standard",
            x_title="Mapping confidence",
            y_title="Candidate clause",
        )
        render_iso_reference_table(result["iso_references"])

    if result.get("citations"):
        st.markdown("#### Evidence Citations")
        citation_rows = []
        for item in result["citations"]:
            citation_rows.append(
                {
                    "source": item["source"],
                    "score": item["score"],
                    "citation": item["citation"],
                    "snippet": item["snippet"],
                    "iso_references": "; ".join(
                        f"{ref['standard']} {ref['clause']}: {ref['topic']}"
                        for ref in item.get("iso_references", [])
                    ),
                }
            )
        wrapped_table(
            citation_rows,
            ["source", "score", "citation", "snippet", "iso_references"],
            labels={
                "source": "Source",
                "score": "Score",
                "citation": "Citation",
                "snippet": "Evidence snippet",
                "iso_references": "ISO references",
            },
            widths={
                "source": "col-small",
                "score": "col-score",
                "citation": "col-medium",
                "snippet": "col-text",
                "iso_references": "col-large",
            },
        )

    if result.get("compressed_context"):
        st.markdown("#### Compressed Context")
        for item in result["compressed_context"]:
            st.write(item)

    if result.get("requirement_completeness"):
        st.markdown("#### Requirement Completeness")
        completeness_rows = []
        missing_counts: dict[str, int] = {}
        for item in result["requirement_completeness"]:
            for field in item["missing_fields"]:
                missing_counts[field] = missing_counts.get(field, 0) + 1
            completeness_rows.append(
                {
                    "requirement_id": item["requirement_id"],
                    "quality_score": item["quality_score"],
                    "missing_fields": ", ".join(item["missing_fields"]),
                    "issues": ", ".join(item["issues"]),
                    "iso_references": "; ".join(
                        f"{ref['standard']} {ref['clause']}: {ref['topic']}"
                        for ref in item.get("iso_references", [])
                    ),
                }
            )
        completeness_chart_cols = st.columns(2)
        with completeness_chart_cols[0]:
            horizontal_bar_chart(
                completeness_rows,
                "quality_score",
                "requirement_id",
                "Requirement Quality Score",
                x_title="Quality score",
                y_title="Requirement",
            )
        with completeness_chart_cols[1]:
            horizontal_bar_chart(
                [{"missing_field": key, "count": value} for key, value in missing_counts.items()],
                "count",
                "missing_field",
                "Missing Completeness Fields",
                x_title="Count",
                y_title="Missing field",
            )
        wrapped_table(
            completeness_rows,
            ["requirement_id", "quality_score", "missing_fields", "issues", "iso_references"],
            labels={
                "requirement_id": "Requirement",
                "quality_score": "Score",
                "missing_fields": "Missing fields",
                "issues": "Issues",
                "iso_references": "ISO references",
            },
            widths={
                "requirement_id": "col-small",
                "quality_score": "col-score",
                "missing_fields": "col-large",
                "issues": "col-large",
                "iso_references": "col-text",
            },
        )

    if result.get("human_review_queue"):
        st.markdown("#### Human Review Queue")
        wrapped_table(
            result["human_review_queue"],
            ["item_type", "item_id", "severity", "reason", "suggested_action"],
            labels={
                "item_type": "Type",
                "item_id": "ID",
                "severity": "Severity",
                "reason": "Reason",
                "suggested_action": "Suggested action",
            },
            widths={
                "item_type": "col-small",
                "item_id": "col-small",
                "severity": "col-small",
                "reason": "col-text",
                "suggested_action": "col-text",
            },
        )


def render_iso_reference_table(references: list[dict[str, Any]]) -> None:
    wrapped_table(
        references,
        ["standard", "clause", "topic", "rationale", "confidence"],
        labels={
            "standard": "Standard",
            "clause": "Clause",
            "topic": "Clause area",
            "rationale": "Why referenced",
            "confidence": "Mapping confidence",
        },
        widths={
            "standard": "col-medium",
            "clause": "col-small",
            "topic": "col-text",
            "rationale": "col-large",
            "confidence": "col-score",
        },
    )


def render_requirements(project: dict[str, Any]) -> None:
    st.subheader("Requirements Engineering")
    stored_traceability = api_request("GET", f"/projects/{project['id']}/traceability")
    stored_count = len(stored_traceability)
    st.caption(
        f"Stored requirements for this project: {stored_count}. "
        "If this is zero, extract requirements from uploaded documents first."
    )

    standard_defaults = [
        standard
        for standard in ["ISO 26262", "ISO 21448", "ISO 8800"]
        if standard in (project.get("standards_scope") or ["ISO 26262", "ISO 21448", "ISO 8800"])
    ] or ["ISO 26262", "ISO 21448", "ISO 8800"]
    selected_iso_standards = st.multiselect(
        "ISO standards for starter requirement generation",
        ["ISO 26262", "ISO 21448", "ISO 8800"],
        default=standard_defaults,
    )
    replace_iso_requirements = st.checkbox("Replace stored requirements with ISO starter set", value=False)

    actions = st.columns(3)
    if actions[0].button("Extract requirements", type="primary", use_container_width=True):
        st.session_state["requirements_result"] = api_request("POST", f"/projects/{project['id']}/requirements/extract")
        st.session_state["quality_review"] = quality_review(st.session_state["requirements_result"].get("requirements", []))
        st.session_state.pop("test_cases", None)
    if actions[1].button("Generate ISO starter requirements", use_container_width=True):
        st.session_state["requirements_result"] = api_request(
            "POST",
            f"/projects/{project['id']}/requirements/generate-from-standards",
            json={
                "standards": selected_iso_standards,
                "replace_existing": replace_iso_requirements,
            },
        )
        st.session_state["quality_review"] = quality_review(st.session_state["requirements_result"].get("requirements", []))
        st.session_state.pop("test_cases", None)
        st.info("Generated candidate requirements from ISO clause areas. Review them against licensed standards before production use.")
    if actions[2].button("Generate test cases", use_container_width=True):
        if stored_count == 0:
            st.info("No stored requirements found. Extracting requirements before test-case generation.")
            extracted = api_request("POST", f"/projects/{project['id']}/requirements/extract")
            st.session_state["requirements_result"] = extracted
            st.session_state["quality_review"] = quality_review(extracted.get("requirements", []))
            if not extracted.get("requirements"):
                st.warning("No requirements were found. Upload or load a document containing 'shall', 'must', or similar requirement language.")
                return
        st.session_state["test_cases"] = api_request("POST", f"/projects/{project['id']}/test-cases/generate")

    if stored_count == 0 and "requirements_result" not in st.session_state:
        st.warning("No requirements are stored yet. Use 'Extract requirements' after uploading a document, or load the seed demo from the sidebar.")
    elif stored_count > 0 and "requirements_result" not in st.session_state:
        st.session_state["requirements_result"] = api_request("POST", f"/projects/{project['id']}/requirements/evaluate", json={})
        st.session_state["quality_review"] = quality_review(st.session_state["requirements_result"].get("requirements", []))

    result = st.session_state.get("requirements_result")
    if result:
        summary = result.get("quality_summary", {})
        c1, c2, c3 = st.columns(3)
        c1.metric("Requirements", summary.get("count", 0))
        c2.metric("Average quality", summary.get("average_quality_score", 0.0))
        c3.metric("Common issues", len(summary.get("common_issues", [])))
        if summary.get("common_issues"):
            st.caption("Most common issues: " + ", ".join(summary["common_issues"]))
        render_quality_review(st.session_state.get("quality_review") or quality_review(result.get("requirements", [])))
        render_requirements_table(result.get("requirements", []))

    if st.session_state.get("test_cases"):
        st.markdown("#### Generated Test Cases")
        test_case_rows = dataframe(st.session_state["test_cases"])
        if not test_case_rows.empty:
            display = test_case_rows.copy()
            for column in ["preconditions", "test_steps", "required_evidence"]:
                if column in display.columns:
                    display[column] = display[column].apply(lambda values: "\n".join(values) if isinstance(values, list) else values)
            wrapped_table(
                display,
                ["id", "linked_requirement", "scenario", "test_steps", "expected_result", "pass_fail_criteria", "required_evidence"],
                labels={
                    "id": "Test ID",
                    "linked_requirement": "Requirement",
                    "scenario": "Scenario",
                    "test_steps": "Test steps",
                    "expected_result": "Expected result",
                    "pass_fail_criteria": "Pass/fail criteria",
                    "required_evidence": "Evidence",
                },
                widths={
                    "id": "col-small",
                    "linked_requirement": "col-small",
                    "scenario": "col-large",
                    "test_steps": "col-text",
                    "expected_result": "col-text",
                    "pass_fail_criteria": "col-large",
                    "required_evidence": "col-medium",
                },
            )
    elif stored_count > 0:
        st.caption("Click 'Generate test cases' to create verification scenarios from the stored requirements.")


def render_quality_review(review: dict[str, Any]) -> None:
    st.markdown("#### Quality Gap Review")
    cols = st.columns(5)
    cols[0].metric("Ready", review["ready_count"])
    cols[1].metric("Needs review", review["needs_review_count"])
    cols[2].metric("Hazard links", f"{review['hazard_coverage']:.0%}")
    cols[3].metric("Safety goal links", f"{review['safety_goal_coverage']:.0%}")
    cols[4].metric("Test links", f"{review['test_case_coverage']:.0%}")

    st.markdown("#### Requirement Quality Charts")
    chart_cols = st.columns(3)
    with chart_cols[0]:
        donut_chart(
            [
                {"status": "Ready", "count": review["ready_count"]},
                {"status": "Needs review", "count": review["needs_review_count"]},
            ],
            "count",
            "status",
            "Requirement Review Status",
        )
    with chart_cols[1]:
        horizontal_bar_chart(
            [
                {"coverage_area": "Hazard links", "coverage": review["hazard_coverage"]},
                {"coverage_area": "Safety goal links", "coverage": review["safety_goal_coverage"]},
                {"coverage_area": "Test links", "coverage": review["test_case_coverage"]},
            ],
            "coverage",
            "coverage_area",
            "Traceability Coverage",
            x_title="Coverage ratio",
            y_title="Coverage area",
        )
    with chart_cols[2]:
        issue_chart_rows = [
            {"issue": issue, "count": count}
            for issue, count in review.get("issue_counts", {}).items()
        ]
        horizontal_bar_chart(
            issue_chart_rows,
            "count",
            "issue",
            "Quality Issue Frequency",
            x_title="Count",
            y_title="Issue",
        )

    issue_counts = review.get("issue_counts", {})
    if issue_counts:
        st.markdown("#### Issue Breakdown")
        max_count = max(issue_counts.values()) or 1
        for issue, count in issue_counts.items():
            label_col, bar_col, count_col = st.columns([0.34, 0.56, 0.10])
            label_col.write(issue)
            bar_col.progress(count / max_count)
            count_col.write(str(count))

    needs_review = review.get("needs_review", [])
    if needs_review:
        st.markdown("#### Requirements Needing Review")
        review_rows = []
        for req in needs_review:
            review_rows.append(
                {
                    "id": req.get("id"),
                    "quality_score": req.get("quality_score"),
                    "issues": ", ".join(req.get("quality_issues") or []),
                    "suggested_improvement": req.get("suggested_improvement"),
                    "text": req.get("text"),
                }
            )
        wrapped_table(
            pd.DataFrame(review_rows),
            ["id", "quality_score", "issues", "suggested_improvement", "text"],
            labels={
                "id": "ID",
                "quality_score": "Score",
                "issues": "Issues",
                "suggested_improvement": "Suggested improvement",
                "text": "Requirement text",
            },
            widths={
                "id": "col-id",
                "quality_score": "col-score",
                "issues": "col-medium",
                "suggested_improvement": "col-large",
                "text": "col-text",
            },
        )


def render_requirements_table(requirements: list[dict[str, Any]]) -> None:
    st.markdown("#### Requirement Register")
    if not requirements:
        st.info("No requirements to display.")
        return

    rows = dataframe(
        requirements,
        ["id", "type", "quality_score", "quality_issues", "linked_hazard", "linked_safety_goal", "suggested_improvement", "text"],
    )
    if "quality_issues" in rows.columns:
        rows["quality_issues"] = rows["quality_issues"].apply(lambda values: ", ".join(values) if isinstance(values, list) else values)

    chart_cols = st.columns(2)
    with chart_cols[0]:
        quality_rows = rows[["id", "quality_score", "type"]].copy()
        quality_rows["quality_score"] = pd.to_numeric(quality_rows["quality_score"], errors="coerce").fillna(0.0)
        horizontal_bar_chart(
            quality_rows,
            "quality_score",
            "id",
            "Requirement Quality Comparison",
            color="type",
            x_title="Quality score",
            y_title="Requirement",
        )
    with chart_cols[1]:
        type_counts = rows.groupby("type").size().reset_index(name="count") if "type" in rows.columns else pd.DataFrame(columns=["type", "count"])
        donut_chart(type_counts, "count", "type", "Requirement Type Mix")

    wrapped_table(
        rows,
        ["id", "type", "quality_score", "quality_issues", "linked_hazard", "linked_safety_goal", "suggested_improvement", "text"],
        labels={
            "id": "ID",
            "type": "Type",
            "quality_score": "Score",
            "quality_issues": "Quality issues",
            "linked_hazard": "Hazard",
            "linked_safety_goal": "Safety goal",
            "suggested_improvement": "Suggested improvement",
            "text": "Requirement text",
        },
        widths={
            "id": "col-id",
            "type": "col-medium",
            "quality_score": "col-score",
            "quality_issues": "col-large",
            "linked_hazard": "col-small",
            "linked_safety_goal": "col-small",
            "suggested_improvement": "col-large",
            "text": "col-text",
        },
    )

    with st.expander("Read full requirement text", expanded=False):
        for req in requirements:
            st.markdown(f"**{req.get('id')} | score {req.get('quality_score', 0.0):.2f}**")
            st.write(req.get("text", ""))
            issues = req.get("quality_issues") or []
            if issues:
                st.caption("Issues: " + ", ".join(issues))
            if req.get("suggested_improvement"):
                st.caption("Suggested improvement: " + req["suggested_improvement"])
            st.divider()


def render_traceability(project: dict[str, Any]) -> None:
    st.subheader("Traceability Matrix")
    rows = api_request("GET", f"/projects/{project['id']}/traceability")
    traceability_frame = dataframe(
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
    )
    if not traceability_frame.empty:
        traceability_frame["quality_score"] = pd.to_numeric(traceability_frame["quality_score"], errors="coerce").fillna(0.0)
        chart_cols = st.columns(3)
        with chart_cols[0]:
            status_counts = traceability_frame.groupby("status").size().reset_index(name="count")
            donut_chart(status_counts, "count", "status", "Traceability Status")
        with chart_cols[1]:
            requirement_type_counts = traceability_frame.groupby("requirement_type").size().reset_index(name="count")
            horizontal_bar_chart(
                requirement_type_counts,
                "count",
                "requirement_type",
                "Requirements by Type",
                x_title="Count",
                y_title="Requirement type",
            )
        with chart_cols[2]:
            horizontal_bar_chart(
                traceability_frame[["requirement_id", "quality_score", "status"]],
                "quality_score",
                "requirement_id",
                "Traceability Row Quality",
                color="status",
                x_title="Quality score",
                y_title="Requirement",
            )
    wrapped_table(
        traceability_frame,
        ["hazard_id", "safety_goal_id", "requirement_id", "requirement_type", "test_case_id", "status", "quality_score", "requirement_text"],
        labels={
            "hazard_id": "Hazard",
            "safety_goal_id": "Safety goal",
            "requirement_id": "Requirement",
            "requirement_type": "Type",
            "test_case_id": "Test case",
            "status": "Status",
            "quality_score": "Score",
            "requirement_text": "Requirement text",
        },
        widths={
            "hazard_id": "col-small",
            "safety_goal_id": "col-small",
            "requirement_id": "col-small",
            "requirement_type": "col-medium",
            "test_case_id": "col-medium",
            "status": "col-small",
            "quality_score": "col-score",
            "requirement_text": "col-text",
        },
    )
    csv_text = api_request("GET", f"/projects/{project['id']}/traceability?format=csv")
    st.download_button("Download traceability CSV", csv_text, "traceability_matrix.csv", "text/csv")


def render_agent_ops(project: dict[str, Any]) -> None:
    st.subheader("Agent Operations")
    source_options = {
        "All analysis sources": None,
        "Autonomous Driving Safety Analyst": "autonomous_driving_safety_analyst",
        "Agentic Document AI Platform": "agentic_document_ai_platform",
    }
    source_label = st.selectbox(
        "Analysis source",
        list(source_options.keys()),
        index=0,
        help="Use the first-project source to monitor Safety Analyst query/evidence runs, or the backend source to monitor this platform's orchestration runs.",
    )
    source_system = source_options[source_label]
    params = {"source_system": source_system} if source_system else None
    dashboard = api_request("GET", f"/projects/{project['id']}/agent-operations/dashboard", params=params)
    runs = api_request("GET", f"/projects/{project['id']}/agent-runs", params=params)

    st.markdown(
        "<div class='grafana-hero'>"
        "<div class='grafana-kicker'>Analysis source</div>"
        f"<div class='grafana-title'>{html.escape(source_label)}</div>"
        "<div class='grafana-subtitle'>"
        "Evaluation panels for reliability, quality, latency, cost, token output, approval gates, and hallucination risk."
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='grafana-panel-title'>Evaluation health</div>", unsafe_allow_html=True)
    cols = st.columns(6)
    with cols[0]:
        grafana_stat("Success rate", f"{dashboard['success_rate']:.0%}", "Resolved runs")
    with cols[1]:
        grafana_stat("Escalation rate", f"{dashboard['escalation_rate']:.0%}", "Human review load")
    with cols[2]:
        grafana_stat("Avg latency", f"{dashboard['average_latency_ms']:.0f} ms", "Run response time")
    with cols[3]:
        grafana_stat("Avg cost", f"${dashboard['average_cost_usd']:.4f}", "Estimated per run")
    with cols[4]:
        grafana_stat("Avg output tokens", f"{dashboard.get('average_output_tokens', 0):.0f}", "Generated answer size")
    with cols[5]:
        grafana_stat("Pending approvals", dashboard["approval_pending_count"], "Approval gate queue")

    st.markdown("<div class='grafana-panel-title'>Evaluation panels</div>", unsafe_allow_html=True)
    runs_frame = dataframe(runs)
    if runs_frame.empty:
        st.info("No agent runs yet. Run tool orchestration to populate the operations dashboard.")
    else:
        if "token_usage" in runs_frame.columns:
            runs_frame["output_tokens"] = runs_frame["token_usage"].apply(output_tokens_from_usage)
        else:
            runs_frame["output_tokens"] = 0
        for numeric_column in ["latency_ms", "estimated_cost_usd", "evaluation_score", "confidence_score"]:
            if numeric_column in runs_frame.columns:
                runs_frame[numeric_column] = pd.to_numeric(runs_frame[numeric_column], errors="coerce").fillna(0.0)
        runs_frame["output_tokens"] = pd.to_numeric(runs_frame["output_tokens"], errors="coerce").fillna(0).astype(int)
        if "created_at" in runs_frame.columns:
            runs_frame["created_at"] = pd.to_datetime(runs_frame["created_at"], errors="coerce")

        overview_cols = st.columns(3)
        with overview_cols[0]:
            status_counts = runs_frame.groupby("status").size().reset_index(name="count") if "status" in runs_frame.columns else pd.DataFrame()
            donut_chart(status_counts, "count", "status", "Run Status Mix")
        with overview_cols[1]:
            approval_counts = runs_frame.groupby("approval_status").size().reset_index(name="count") if "approval_status" in runs_frame.columns else pd.DataFrame()
            donut_chart(approval_counts, "count", "approval_status", "Approval Status")
        with overview_cols[2]:
            escalation_counts = (
                runs_frame.assign(escalation=runs_frame["human_escalation_required"].map({True: "Escalated", False: "No escalation"}))
                .groupby("escalation")
                .size()
                .reset_index(name="count")
                if "human_escalation_required" in runs_frame.columns
                else pd.DataFrame()
            )
            donut_chart(escalation_counts, "count", "escalation", "Human Escalation")

        trend_cols = st.columns(4)
        ordered_runs = runs_frame.sort_values("created_at") if "created_at" in runs_frame.columns else runs_frame
        with trend_cols[0]:
            line_chart(ordered_runs, "created_at", "latency_ms", "Latency Trend", color="status", y_title="Latency ms")
        with trend_cols[1]:
            line_chart(ordered_runs, "created_at", "estimated_cost_usd", "Cost Trend", color="model_used", y_title="Estimated cost USD")
        with trend_cols[2]:
            line_chart(ordered_runs, "created_at", "evaluation_score", "Evaluation Score Trend", color="status", y_title="Evaluation score")
        with trend_cols[3]:
            line_chart(ordered_runs, "created_at", "output_tokens", "Output Token Trend", color="model_used", y_title="Output tokens")

        flag_counts = dashboard.get("hallucination_flags", {})
        tool_counts: dict[str, int] = {}
        if "tools_used" in runs_frame.columns:
            for tools in runs_frame["tools_used"]:
                if isinstance(tools, list):
                    for tool in tools:
                        tool_counts[str(tool)] = tool_counts.get(str(tool), 0) + 1
        detail_cols = st.columns(3)
        with detail_cols[0]:
            horizontal_bar_chart(
                [{"flag": key, "count": value} for key, value in flag_counts.items()],
                "count",
                "flag",
                "Hallucination Flag Frequency",
                x_title="Count",
                y_title="Flag",
            )
        with detail_cols[1]:
            horizontal_bar_chart(
                [{"tool": key, "count": value} for key, value in tool_counts.items()],
                "count",
                "tool",
                "Tool Usage Frequency",
                x_title="Count",
                y_title="Tool",
            )
        with detail_cols[2]:
            horizontal_bar_chart(
                runs_frame[["agent_run_id", "output_tokens", "operation_name"]],
                "output_tokens",
                "agent_run_id",
                "Output Tokens by Run",
                color="operation_name",
                x_title="Output tokens",
                y_title="Run ID",
            )

    if source_system in {None, "agentic_document_ai_platform"}:
        st.markdown("<div class='grafana-panel-title'>Backend orchestration simulator</div>", unsafe_allow_html=True)
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
    else:
        st.info("To create first-project analysis runs, use the Ask tab. Those query runs appear here with output-token tracking.")

    if st.session_state.get("tool_result"):
        render_orchestration_result(st.session_state["tool_result"])

    st.markdown("#### Run Logs")
    run_log_frame = dataframe(runs)
    if not run_log_frame.empty:
        run_log_frame["output_tokens"] = run_log_frame.get("token_usage", pd.Series(dtype=object)).apply(output_tokens_from_usage)
    st.dataframe(
        dataframe(
            run_log_frame.to_dict("records") if not run_log_frame.empty else [],
            [
                "agent_run_id",
                "operation_name",
                "status",
                "model_used",
                "latency_ms",
                "output_tokens",
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


def render_workflow(project: dict[str, Any]) -> None:
    st.subheader("Workflow Tracking")
    source_options = {
        "Autonomous Driving Safety Analyst": "autonomous_driving_safety_analyst",
        "Generic backend workflow": "agentic_document_ai_platform",
    }
    source_label = st.selectbox(
        "Tracking source",
        list(source_options.keys()),
        index=0,
        help="Choose which workflow source this dashboard tracks. Select the first option for your 1st project.",
    )
    source_system = source_options[source_label]

    st.markdown(
        "<div class='grafana-hero'>"
        "<div class='grafana-kicker'>Workflow source</div>"
        f"<div class='grafana-title'>{html.escape(source_label)}</div>"
        "<div class='grafana-subtitle'>"
        "Grafana-style tracking for safety-analysis work: question intake, evidence retrieval, answer quality review, "
        "requirements, traceability, tests, and report handoff."
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    action_cols = st.columns([0.32, 0.68])
    if source_system == "autonomous_driving_safety_analyst" and action_cols[0].button(
        "Create first-project workflow",
        type="primary",
        use_container_width=True,
    ):
        api_request("POST", f"/projects/{project['id']}/workflow/bootstrap-autonomous-safety-analyst")
        st.rerun()
    if source_system != "autonomous_driving_safety_analyst":
        action_cols[0].info("Use the form below to create generic workflow items.")

    dashboard = api_request("GET", f"/projects/{project['id']}/workflow/dashboard", params={"source_system": source_system})
    items = api_request("GET", f"/projects/{project['id']}/workflow/items", params={"source_system": source_system})

    st.markdown("<div class='grafana-panel-title'>Live workflow stats</div>", unsafe_allow_html=True)
    metric_cols = st.columns(5)
    with metric_cols[0]:
        grafana_stat("Workflow items", dashboard["total_items"], "Total tracked tasks")
    with metric_cols[1]:
        grafana_stat("Completion", f"{dashboard['completion_rate']:.0%}", "Done / total")
    with metric_cols[2]:
        grafana_stat("In progress", dashboard["in_progress_items"], "Active work")
    with metric_cols[3]:
        grafana_stat("Blocked", dashboard["blocked_items"], "Needs intervention")
    with metric_cols[4]:
        grafana_stat("Overdue", dashboard["overdue_items"], "Past due date")

    st.markdown("<div class='grafana-panel-title'>Workflow health panels</div>", unsafe_allow_html=True)
    chart_cols = st.columns(3)
    with chart_cols[0]:
        donut_chart(
            [{"status": key, "count": value} for key, value in dashboard["by_status"].items()],
            "count",
            "status",
            "Workflow Status",
        )
    with chart_cols[1]:
        horizontal_bar_chart(
            [{"stage": key, "count": value} for key, value in dashboard["by_stage"].items()],
            "count",
            "stage",
            "Items by Workflow Stage",
            x_title="Count",
            y_title="Stage",
        )
    with chart_cols[2]:
        donut_chart(
            [{"priority": key, "count": value} for key, value in dashboard["by_priority"].items()],
            "count",
            "priority",
            "Priority Mix",
        )

    st.markdown("#### Add Tracking Item")
    with st.form("create_workflow_item", clear_on_submit=True):
        form_cols = st.columns(2)
        title = form_cols[0].text_input("Title", value="Review safety analyst answer evidence")
        owner = form_cols[1].text_input("Owner", value="")
        description = st.text_area("Description", value="Track evidence, quality review, and follow-up actions for a first-project answer.")
        row_cols = st.columns(3)
        stage = row_cols[0].selectbox(
            "Stage",
            ["intake", "evidence_retrieval", "quality_review", "requirements_engineering", "traceability", "reporting"],
            index=2,
        )
        status = row_cols[1].selectbox("Status", ["open", "in_progress", "blocked", "done"], index=0)
        priority = row_cols[2].selectbox("Priority", ["low", "medium", "high", "critical"], index=1)
        acceptance = st.text_area("Acceptance criteria", value="Evidence is linked\nQuality decision is recorded\nNext action is clear")
        submitted = st.form_submit_button("Add workflow item")
    if submitted:
        api_request(
            "POST",
            f"/projects/{project['id']}/workflow/items",
            json={
                "title": title,
                "description": description,
                "workflow_stage": stage,
                "status": status,
                "priority": priority,
                "owner": owner or None,
                "source_system": source_system,
                "acceptance_criteria": [line.strip() for line in acceptance.splitlines() if line.strip()],
            },
        )
        st.rerun()

    st.markdown("<div class='grafana-panel-title'>Workflow board</div>", unsafe_allow_html=True)
    if not items:
        if source_system == "autonomous_driving_safety_analyst":
            st.info("No workflow items yet. Click 'Create first-project workflow' to generate the standard review steps.")
        else:
            st.info("No workflow items yet. Add a tracking item to start this workflow.")
        return

    board_rows = [
        {
            "id": item["id"],
            "title": item["title"],
            "description": item.get("description") or "",
            "stage": item["workflow_stage"],
            "status": item["status"],
            "priority": item["priority"],
            "owner": item.get("owner"),
            "criteria": "; ".join(item.get("acceptance_criteria") or []),
            "updated_at": item["updated_at"],
        }
        for item in items
    ]
    wrapped_table(
        board_rows,
        ["id", "title", "description", "stage", "status", "priority", "owner", "criteria", "updated_at"],
        labels={
            "id": "ID",
            "title": "Title",
            "description": "Description",
            "stage": "Stage",
            "status": "Status",
            "priority": "Priority",
            "owner": "Owner",
            "criteria": "Acceptance criteria",
            "updated_at": "Updated",
        },
        widths={
            "id": "col-id",
            "title": "col-medium",
            "description": "col-text",
            "stage": "col-medium",
            "status": "col-small",
            "priority": "col-small",
            "owner": "col-small",
            "criteria": "col-text",
            "updated_at": "col-medium",
        },
    )

    st.markdown("#### Quick Update")
    update_cols = st.columns(3)
    selected_id = update_cols[0].selectbox("Workflow item", [item["id"] for item in items], format_func=lambda item_id: next(item["title"] for item in items if item["id"] == item_id))
    selected_item = next(item for item in items if item["id"] == selected_id)
    next_status = update_cols[1].selectbox("New status", ["open", "in_progress", "blocked", "done"], index=1)
    next_owner = update_cols[2].text_input("Owner update", value="")
    st.caption(selected_item.get("description") or "No description recorded for this item.")
    notes = st.text_area("Update notes", value="")
    if st.button("Update workflow item", use_container_width=True):
        payload: dict[str, Any] = {"status": next_status, "notes": notes or None}
        if next_owner:
            payload["owner"] = next_owner
        api_request("PATCH", f"/projects/{project['id']}/workflow/items/{selected_id}", json=payload)
        st.rerun()

    st.markdown("#### Remove Tracking Item")
    remove_cols = st.columns([0.45, 0.30, 0.25])
    remove_id = remove_cols[0].selectbox(
        "Tracking item to remove",
        [item["id"] for item in items],
        format_func=lambda item_id: next(item["title"] for item in items if item["id"] == item_id),
        key="remove_workflow_item_id",
    )
    confirm_remove = remove_cols[1].checkbox("Confirm removal", value=False)
    if remove_cols[2].button("Remove item", use_container_width=True, disabled=not confirm_remove):
        api_request("DELETE", f"/projects/{project['id']}/workflow/items/{remove_id}")
        st.success("Tracking item removed.")
        st.rerun()


def render_reports(project: dict[str, Any]) -> None:
    st.subheader("Reports")
    markdown_report = api_request("GET", f"/projects/{project['id']}/report?format=markdown")
    structured_report = api_request("GET", f"/projects/{project['id']}/report?format=json")
    requirements_csv_text = api_request("GET", f"/projects/{project['id']}/report?format=requirements_csv")
    traceability_csv_text = api_request("GET", f"/projects/{project['id']}/report?format=traceability_csv")

    st.markdown(
        "<div class='report-cover'>"
        "<div class='report-label'>Safety engineering report</div>"
        f"<div class='report-title'>{html.escape(project['name'])}</div>"
        f"<div class='report-subtitle'>{html.escape(project['domain'])} | {html.escape(project['system_type'])} | "
        f"Standards: {html.escape(', '.join(project.get('standards_scope', [])))}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    download_cols = st.columns(4)
    download_cols[0].download_button("Markdown", markdown_report, "safety_requirements_report.md", "text/markdown", use_container_width=True)
    download_cols[1].download_button("Requirements CSV", requirements_csv_text, "requirements.csv", "text/csv", use_container_width=True)
    download_cols[2].download_button("Traceability CSV", traceability_csv_text, "traceability.csv", "text/csv", use_container_width=True)
    download_cols[3].download_button(
        "Structured JSON",
        json.dumps(structured_report, indent=2),
        "structured_safety_report.json",
        "application/json",
        use_container_width=True,
    )

    view = st.selectbox(
        "Report view",
        ["Professional summary", "Structured data", "Markdown preview"],
        index=0,
    )
    if view == "Professional summary":
        render_professional_report(project, structured_report)
    elif view == "Structured data":
        render_structured_report(structured_report)
    else:
        st.markdown("#### Markdown Preview")
        st.markdown(markdown_report.split("## Structured JSON")[0].strip())


def render_professional_report(project: dict[str, Any], payload: dict[str, Any]) -> None:
    requirements = payload.get("requirements", [])
    traceability = payload.get("traceability", [])
    requirement_frame = dataframe(requirements)
    traceability_frame = dataframe(traceability)

    average_quality = 0.0
    if not requirement_frame.empty and "quality_score" in requirement_frame.columns:
        average_quality = float(pd.to_numeric(requirement_frame["quality_score"], errors="coerce").fillna(0.0).mean())
    linked_hazards = sum(1 for row in requirements if row.get("linked_hazard"))
    linked_tests = sum(1 for row in traceability if row.get("test_case_id"))

    st.markdown("<div class='grafana-panel-title'>Executive summary</div>", unsafe_allow_html=True)
    cols = st.columns(5)
    with cols[0]:
        grafana_stat("Requirements", len(requirements), "Structured items")
    with cols[1]:
        grafana_stat("Avg quality", f"{average_quality:.2f}", "Requirement score")
    with cols[2]:
        grafana_stat("Hazard links", f"{linked_hazards}/{len(requirements)}", "Trace coverage")
    with cols[3]:
        grafana_stat("Trace rows", len(traceability), "Matrix entries")
    with cols[4]:
        grafana_stat("Test links", linked_tests, "Verification links")

    st.markdown("<div class='grafana-panel-title'>Report analysis panels</div>", unsafe_allow_html=True)
    chart_cols = st.columns(3)
    if not requirement_frame.empty:
        with chart_cols[0]:
            type_counts = requirement_frame.groupby("type").size().reset_index(name="count") if "type" in requirement_frame.columns else pd.DataFrame()
            donut_chart(type_counts, "count", "type", "Requirement Type Distribution")
        with chart_cols[1]:
            quality_rows = requirement_frame[["id", "quality_score", "type"]].copy() if {"id", "quality_score", "type"}.issubset(requirement_frame.columns) else pd.DataFrame()
            if not quality_rows.empty:
                quality_rows["quality_score"] = pd.to_numeric(quality_rows["quality_score"], errors="coerce").fillna(0.0)
            horizontal_bar_chart(quality_rows, "quality_score", "id", "Requirement Quality", color="type", x_title="Score", y_title="Requirement")
    if not traceability_frame.empty:
        with chart_cols[2]:
            status_counts = traceability_frame.groupby("status").size().reset_index(name="count") if "status" in traceability_frame.columns else pd.DataFrame()
            donut_chart(status_counts, "count", "status", "Traceability Status")

    st.markdown("<div class='report-section'></div>", unsafe_allow_html=True)
    st.markdown("#### Key Findings")
    findings = []
    if requirements:
        findings.append(f"{len(requirements)} requirements are available for review and export.")
    if average_quality < 0.75 and requirements:
        findings.append("Average requirement quality is below the preferred review threshold of 0.75.")
    if linked_hazards < len(requirements):
        findings.append("Some requirements still need hazard links before the traceability case is complete.")
    if linked_tests < len(traceability):
        findings.append("Some traceability rows do not yet have linked test cases.")
    if not findings:
        findings.append("No major report gaps detected from the structured output.")
    for finding in findings:
        st.write(f"- {finding}")

    st.markdown("#### Requirement Register")
    render_report_requirements_table(requirements)
    st.markdown("#### Traceability Matrix")
    render_report_traceability_table(traceability)


def render_structured_report(payload: dict[str, Any]) -> None:
    requirements = payload.get("requirements", [])
    traceability = payload.get("traceability", [])
    st.markdown("<div class='grafana-panel-title'>Structured report data</div>", unsafe_allow_html=True)
    st.caption("This is the same data as the JSON export, rendered into reviewable sections.")

    tabs = st.tabs(["Requirements", "Traceability", "Schema Summary"])
    with tabs[0]:
        render_report_requirements_table(requirements)
    with tabs[1]:
        render_report_traceability_table(traceability)
    with tabs[2]:
        schema_rows = [
            {
                "section": "requirements",
                "rows": len(requirements),
                "main_fields": ", ".join(list(requirements[0].keys())[:8]) if requirements else "",
            },
            {
                "section": "traceability",
                "rows": len(traceability),
                "main_fields": ", ".join(list(traceability[0].keys())[:8]) if traceability else "",
            },
        ]
        wrapped_table(
            schema_rows,
            ["section", "rows", "main_fields"],
            labels={"section": "Section", "rows": "Rows", "main_fields": "Main fields"},
            widths={"section": "col-medium", "rows": "col-score", "main_fields": "col-text"},
        )


def render_report_requirements_table(requirements: list[dict[str, Any]]) -> None:
    rows = []
    for req in requirements:
        rows.append(
            {
                "id": req.get("id"),
                "type": req.get("type"),
                "quality_score": req.get("quality_score"),
                "hazard": req.get("linked_hazard"),
                "safety_goal": req.get("linked_safety_goal"),
                "issues": ", ".join(req.get("quality_issues") or []),
                "evidence": req.get("evidence_source"),
                "text": req.get("text"),
            }
        )
    wrapped_table(
        rows,
        ["id", "type", "quality_score", "hazard", "safety_goal", "issues", "evidence", "text"],
        labels={
            "id": "Requirement",
            "type": "Type",
            "quality_score": "Score",
            "hazard": "Hazard",
            "safety_goal": "Safety goal",
            "issues": "Issues",
            "evidence": "Evidence source",
            "text": "Requirement text",
        },
        widths={
            "id": "col-small",
            "type": "col-medium",
            "quality_score": "col-score",
            "hazard": "col-small",
            "safety_goal": "col-small",
            "issues": "col-large",
            "evidence": "col-large",
            "text": "col-text",
        },
    )


def render_report_traceability_table(traceability: list[dict[str, Any]]) -> None:
    wrapped_table(
        traceability,
        ["hazard_id", "safety_goal_id", "requirement_id", "requirement_type", "test_case_id", "evidence_source", "status", "quality_score"],
        labels={
            "hazard_id": "Hazard",
            "safety_goal_id": "Safety goal",
            "requirement_id": "Requirement",
            "requirement_type": "Type",
            "test_case_id": "Test case",
            "evidence_source": "Evidence source",
            "status": "Status",
            "quality_score": "Score",
        },
        widths={
            "hazard_id": "col-small",
            "safety_goal_id": "col-small",
            "requirement_id": "col-small",
            "requirement_type": "col-medium",
            "test_case_id": "col-medium",
            "evidence_source": "col-text",
            "status": "col-small",
            "quality_score": "col-score",
        },
    )


st.title("Agentic Document AI Platform for Safety Engineering")
st.caption("FastAPI backend UI for project-specific RAG, requirements engineering, traceability, and agent operations.")

project = render_project_sidebar()
if project:
    if st.session_state.get("active_project_id") != project["id"]:
        for key in ["last_query_result", "requirements_result", "test_cases", "tool_result"]:
            st.session_state.pop(key, None)
        st.session_state["active_project_id"] = project["id"]

    st.markdown(f"### {project['name']}")
    st.markdown(
        f"<div class='small-muted'>{project['domain']} | {project['system_type']} | "
        f"Standards: {', '.join(project.get('standards_scope', []))}</div>",
        unsafe_allow_html=True,
    )
    tabs = st.tabs(["Overview", "Documents", "Ask", "Retrieval", "Precision", "Requirements", "Traceability", "Workflow", "Agent Ops", "Reports"])
    with tabs[0]:
        render_overview(project)
    with tabs[1]:
        render_documents(project)
    with tabs[2]:
        render_query(project)
    with tabs[3]:
        render_retrieval(project)
    with tabs[4]:
        render_precision_review(project)
    with tabs[5]:
        render_requirements(project)
    with tabs[6]:
        render_traceability(project)
    with tabs[7]:
        render_workflow(project)
    with tabs[8]:
        render_agent_ops(project)
    with tabs[9]:
        render_reports(project)
