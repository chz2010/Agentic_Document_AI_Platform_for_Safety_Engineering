from backend.main import app
from backend.settings import settings
from fastapi.testclient import TestClient


def test_health_and_project_create_list():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200

        create_response = client.post(
            "/projects",
            json={
                "name": "AEB Pedestrian Platform",
                "domain": "ADAS",
                "system_type": "AEB",
                "standards_scope": ["ISO 26262", "ISO 21448", "ISO 8800"],
                "description": "Night-time pedestrian detection safety case",
            },
        )

        assert create_response.status_code == 200
        project_id = create_response.json()["id"]
        list_response = client.get("/projects")
        assert list_response.status_code == 200
        assert any(project["id"] == project_id for project in list_response.json())


def test_upload_extract_query_and_traceability_csv():
    settings.openai_api_key = ""
    settings.use_openai_generation = False
    content = (
        "REQ-AEB-101: The AEB system shall detect partially occluded pedestrians at night "
        "within 40 m below 50 km/h and verify the result by scenario test evidence."
    )

    with TestClient(app) as client:
        project = client.post(
            "/projects",
            json={"name": "AEB TXT Upload", "domain": "ADAS", "system_type": "AEB"},
        ).json()

        upload = client.post(
            f"/projects/{project['id']}/documents",
            files={"file": ("aeb_requirements.txt", content, "text/plain")},
        )
        assert upload.status_code == 200
        assert upload.json()["chunk_count"] >= 1

        extracted = client.post(f"/projects/{project['id']}/requirements/extract")
        assert extracted.status_code == 200
        assert extracted.json()["requirements"][0]["id"] == "REQ-AEB-101"

        query = client.post(
            f"/projects/{project['id']}/query",
            json={"question": "Is night occlusion covered?", "include_requirements_review": True},
        )
        assert query.status_code == 200
        assert query.json()["retrieved_sources"]
        runs = client.get(f"/projects/{project['id']}/agent-runs")
        assert runs.status_code == 200
        assert runs.json()[0]["operation_name"] == "project_query"
        assert runs.json()[0]["prompt_version"] == "query-answer-v1"
        assert runs.json()[0]["evaluation_score"] is not None

        csv_response = client.get(f"/projects/{project['id']}/traceability?format=csv")
        assert csv_response.status_code == 200
        assert "hazard_id,hazard_description,safety_goal_id,requirement_id" in csv_response.text


def test_agent_operations_log_cost_failure_escalation_and_approval():
    with TestClient(app) as client:
        project = client.post(
            "/projects",
            json={"name": "Agent Ops Project", "domain": "Safety", "system_type": "Backend"},
        ).json()

        create_response = client.post(
            f"/projects/{project['id']}/agent-runs",
            json={
                "operation_name": "requirements_extract",
                "agent_name": "requirements_agent",
                "status": "failed",
                "model_used": "gpt-4o-mini",
                "prompt_version": "requirements-extract-v2",
                "prompt_template_id": "req-extract-template",
                "input_summary": "Extract requirements from uploaded safety case.",
                "output_summary": "Extraction failed during parsing.",
                "token_usage": {"prompt_tokens": 1000, "completion_tokens": 500},
                "failure_reason": "Parser returned invalid structured output.",
                "failure_stage": "structured_output_validation",
                "evaluation_score": 0.4,
            },
        )

        assert create_response.status_code == 200
        run = create_response.json()
        assert run["estimated_cost_usd"] > 0
        assert run["failure_reason"] == "Parser returned invalid structured output."
        assert run["human_escalation_required"] is True
        assert run["approval_required"] is True
        assert run["approval_status"] == "pending"
        assert run["prompt_version"] == "requirements-extract-v2"
        assert run["agent_run_id"] == run["id"]
        assert run["confidence_score"] is None

        approval = client.patch(
            f"/projects/{project['id']}/agent-runs/{run['id']}/approval",
            json={
                "approval_status": "approved",
                "approved_by": "lead_safety_engineer",
                "approval_notes": "Reviewed failure and accepted retry plan.",
                "human_escalation_required": False,
            },
        )

        assert approval.status_code == 200
        approved = approval.json()
        assert approved["approval_status"] == "approved"
        assert approved["approved_by"] == "lead_safety_engineer"
        assert approved["human_escalation_required"] is False

        filtered = client.get(f"/projects/{project['id']}/agent-runs?approval_status=approved")
        assert filtered.status_code == 200
        assert len(filtered.json()) == 1


def test_tool_orchestration_integrations_and_dashboard():
    with TestClient(app) as client:
        project = client.post(
            "/projects",
            json={"name": "Agent Operations Project", "domain": "Safety", "system_type": "AgentOps"},
        ).json()

        orchestration = client.post(
            f"/projects/{project['id']}/agent-tools/run",
            json={
                "user_request": "Review low-confidence requirements and open a ticket.",
                "tools": [
                    "search_project_docs",
                    "evaluate_requirements",
                    "generate_traceability",
                    "generate_test_cases",
                    "create_issue_ticket",
                ],
                "prompt_version": "ops-prompt-v3",
                "model_version": "gpt-4o-mini-2026-06",
                "tool_config_version": "safety-tools-v2",
                "confidence_score": 0.62,
                "hallucination_risk": "high",
            },
        )

        assert orchestration.status_code == 200
        orchestration_body = orchestration.json()
        assert orchestration_body["status"] == "requires_human_review"
        assert orchestration_body["approval_required"] is True
        assert orchestration_body["human_escalation_required"] is True
        assert "create_issue_ticket" in orchestration_body["tools_used"]
        assert orchestration_body["tool_results"]["create_issue_ticket"]["ticket_id"].startswith("JIRA-")

        github_issue = client.post(
            f"/projects/{project['id']}/integrations/github-issue",
            json={
                "integration_type": "github_issue",
                "title": "Review hallucination risk",
                "description": "Mock GitHub issue for human review.",
                "agent_run_id": orchestration_body["agent_run_id"],
                "payload": {"severity": "medium"},
            },
        )
        assert github_issue.status_code == 200
        assert github_issue.json()["external_id"].startswith("GH-")

        slack = client.post(
            f"/projects/{project['id']}/integrations/slack-notification",
            json={
                "integration_type": "slack_notification",
                "title": "Human review required",
                "description": "Mock Slack notification.",
                "payload": {"channel": "#safety-review"},
            },
        )
        assert slack.status_code == 200
        assert slack.json()["external_id"].startswith("SLACK-")

        dashboard = client.get(f"/projects/{project['id']}/agent-operations/dashboard")
        assert dashboard.status_code == 200
        metrics = dashboard.json()
        assert metrics["total_runs"] == 1
        assert metrics["escalation_rate"] == 1.0
        assert metrics["approval_pending_count"] == 1
        assert metrics["hallucination_flags"]["high_hallucination_risk"] == 1
