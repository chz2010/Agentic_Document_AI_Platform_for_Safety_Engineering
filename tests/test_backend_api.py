from backend.main import app
from backend.settings import settings
from fastapi.testclient import TestClient


def test_health_and_project_create_list():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        health = response.json()
        assert health["status"] == "ok"
        assert health["answer_mode"] in {"none", "openai", "local"}
        assert health["answer_model"]

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


def test_auth_memory_model_registry_versions_and_metrics():
    with TestClient(app) as client:
        login = client.post(
            "/auth/login",
            json={"username": settings.demo_username, "password": settings.demo_password},
        )
        assert login.status_code == 200
        tokens = login.json()
        assert tokens["access_token"]
        assert tokens["refresh_token"]
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        me = client.get("/users/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["username"] == settings.demo_username

        refreshed = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert refreshed.status_code == 200
        refreshed_headers = {"Authorization": f"Bearer {refreshed.json()['access_token']}"}

        memory = client.post(
            "/agent-memory",
            headers=refreshed_headers,
            json={"key": "demo_context", "value": "Use candidate standards references only.", "tags": ["demo", "governance"]},
        )
        assert memory.status_code == 200
        assert memory.json()["created_by"] == settings.demo_username

        memories = client.get("/agent-memory", headers=refreshed_headers)
        assert memories.status_code == 200
        assert any(item["key"] == "demo_context" for item in memories.json())

        models = client.get("/models")
        assert models.status_code == 200
        assert any(model["model_name"] == "deterministic-evidence-synthesis" for model in models.json())

        selected = client.post(
            "/models/select",
            headers=refreshed_headers,
            json={"answer_mode": "none", "model_name": "deterministic-evidence-synthesis"},
        )
        assert selected.status_code == 200
        assert selected.json()["model_name"] == "deterministic-evidence-synthesis"

        versions = client.get("/agent-versions")
        assert versions.status_code == 200
        assert {item["agent_name"] for item in versions.json()} >= {"project_rag_agent", "requirements_agent"}

        metrics = client.get("/metrics")
        assert metrics.status_code == 200
        assert "safety_platform_projects_total" in metrics.text

        health = client.get("/health").json()
        assert health["auth_enabled"] is True
        assert health["model_registry_enabled"] is True


def test_project_delete_removes_project_from_workspace():
    with TestClient(app) as client:
        project = client.post(
            "/projects",
            json={"name": "Temporary Delete Project", "domain": "QA", "system_type": "Cleanup"},
        ).json()

        delete_response = client.delete(f"/projects/{project['id']}")
        assert delete_response.status_code == 200
        assert delete_response.json()["status"] == "deleted"

        list_response = client.get("/projects")
        assert list_response.status_code == 200
        assert all(item["id"] != project["id"] for item in list_response.json())


def test_upload_extract_query_and_traceability_csv():
    settings.openai_api_key = ""
    settings.use_openai_generation = False
    settings.answer_mode = "none"
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
        uploaded_document = upload.json()
        assert uploaded_document["chunk_count"] >= 1

        chunks = client.get(f"/projects/{project['id']}/documents/{uploaded_document['id']}/chunks")
        assert chunks.status_code == 200
        chunk_rows = chunks.json()
        assert len(chunk_rows) == uploaded_document["chunk_count"]
        assert chunk_rows[0]["chunk_id"].startswith(f"project-{project['id']}-doc-{uploaded_document['id']}-chunk-")
        assert "partially occluded pedestrians" in chunk_rows[0]["text_preview"]

        extracted = client.post(f"/projects/{project['id']}/requirements/extract")
        assert extracted.status_code == 200
        assert extracted.json()["requirements"][0]["id"] == "REQ-AEB-101"

        query = client.post(
            f"/projects/{project['id']}/query",
            json={"question": "Is night occlusion covered?", "include_requirements_review": True},
        )
        assert query.status_code == 200
        assert query.json()["answer_mode"] == "none"
        assert query.json()["answer_model"] == "deterministic-evidence-synthesis"
        assert "## Evidence reviewed" in query.json()["answer"]
        assert "## Recommended next actions" in query.json()["answer"]
        assert query.json()["retrieved_sources"]
        runs = client.get(f"/projects/{project['id']}/agent-runs")
        assert runs.status_code == 200
        assert runs.json()[0]["operation_name"] == "project_query"
        assert runs.json()[0]["source_system"] == "autonomous_driving_safety_analyst"
        assert runs.json()[0]["model_used"] == "deterministic-evidence-synthesis"
        assert runs.json()[0]["token_usage"]["completion_tokens"] > 0
        assert runs.json()[0]["prompt_version"] == "query-answer-v1"
        assert runs.json()[0]["evaluation_score"] is not None

        source_dashboard = client.get(
            f"/projects/{project['id']}/agent-operations/dashboard?source_system=autonomous_driving_safety_analyst"
        )
        assert source_dashboard.status_code == 200
        assert source_dashboard.json()["total_output_tokens"] > 0

        csv_response = client.get(f"/projects/{project['id']}/traceability?format=csv")
        assert csv_response.status_code == 200
        assert "hazard_id,hazard_description,safety_goal_id,requirement_id" in csv_response.text


def test_query_can_select_local_answer_engine_without_running_local_model():
    settings.openai_api_key = ""
    settings.use_openai_generation = False
    settings.answer_mode = "none"

    with TestClient(app) as client:
        project = client.post(
            "/projects",
            json={"name": "Local Engine Selection", "domain": "ADAS", "system_type": "AEB"},
        ).json()

        client.post(
            f"/projects/{project['id']}/documents",
            files={
                "file": (
                    "local_engine_requirements.txt",
                    "REQ-AEB-301: The AEB system shall detect pedestrians and verify detection by scenario testing.",
                    "text/plain",
                )
            },
        )

        query = client.post(
            f"/projects/{project['id']}/query",
            json={
                "question": "Is pedestrian detection covered?",
                "answer_mode": "local",
                "answer_model": "mistral:7b",
            },
        )

        assert query.status_code == 200
        assert query.json()["answer_mode"] == "local"
        assert query.json()["answer_model"] == "mistral:7b"
        assert query.json()["retrieved_sources"]


def test_generate_requirements_from_iso_standards():
    with TestClient(app) as client:
        project = client.post(
            "/projects",
            json={
                "name": "ISO Starter Requirements",
                "domain": "Autonomous driving",
                "system_type": "AEB pedestrian detection",
                "standards_scope": ["ISO 26262", "ISO 21448", "ISO 8800"],
            },
        ).json()

        generated = client.post(
            f"/projects/{project['id']}/requirements/generate-from-standards",
            json={
                "standards": ["ISO 26262", "ISO 21448", "ISO 8800"],
                "replace_existing": True,
            },
        )

        assert generated.status_code == 200
        body = generated.json()
        ids = {requirement["id"] for requirement in body["requirements"]}
        assert "REQ-ISO26262-HARA-001" in ids
        assert "REQ-ISO21448-SOTIF-001" in ids
        assert "REQ-ISO8800-DATA-001" in ids
        assert all(requirement["linked_hazard"] for requirement in body["requirements"])
        assert all(requirement["linked_safety_goal"] for requirement in body["requirements"])
        assert any("Clause 6" in requirement["evidence_source"] for requirement in body["requirements"])

        traceability = client.get(f"/projects/{project['id']}/traceability")
        assert traceability.status_code == 200
        assert len(traceability.json()) == len(body["requirements"])
        assert any("ISO 26262" in row["evidence_source"] for row in traceability.json())

        test_cases = client.post(f"/projects/{project['id']}/test-cases/generate")
        assert test_cases.status_code == 200
        assert test_cases.json()

        workflow_item = client.post(
            f"/projects/{project['id']}/workflow/items",
            json={
                "title": "Review ISO starter requirement",
                "workflow_stage": "requirements_engineering",
                "linked_requirement_id": "REQ-ISO26262-HARA-001",
                "linked_hazard_id": "HZ-ISO26262-001",
                "linked_safety_goal_id": "SG-ISO26262-001",
            },
        )
        assert workflow_item.status_code == 200

        graph = client.get(f"/projects/{project['id']}/knowledge-graph")
        assert graph.status_code == 200
        graph_body = graph.json()
        node_types = {node["type"] for node in graph_body["nodes"]}
        edge_relationships = {edge["relationship"] for edge in graph_body["edges"]}
        assert graph_body["node_count"] > len(body["requirements"])
        assert {"project", "requirement", "hazard", "safety_goal", "test_case", "workflow_item"}.issubset(node_types)
        assert {"contains_requirement", "linked_hazard", "linked_safety_goal", "verified_by", "tracks_requirement"}.issubset(edge_relationships)
        assert graph_body["coverage_summary"]["hazard_link_coverage"] == 1.0
        assert graph_body["coverage_summary"]["safety_goal_link_coverage"] == 1.0
        assert graph_body["coverage_summary"]["test_case_link_coverage"] == 1.0


def test_domain_profiles_benchmark_and_graph_layout():
    with TestClient(app) as client:
        profiles = client.get("/domain-profiles")
        assert profiles.status_code == 200
        assert any(profile["id"] == "railway" for profile in profiles.json())

        project = client.post(
            "/projects",
            json={
                "name": "Railway Benchmark Project",
                "domain": "Railway safety engineering",
                "system_type": "ERTMS control system",
                "standards_scope": ["IEC 62278 / EN 50126", "EN 50128", "EN 50129"],
            },
        ).json()

        generated = client.post(
            f"/projects/{project['id']}/requirements/generate-from-standards",
            json={
                "standards": ["IEC 62278 / EN 50126", "EN 50128", "EN 50129", "ERTMS"],
                "replace_existing": True,
            },
        )
        assert generated.status_code == 200
        requirement_ids = {item["id"] for item in generated.json()["requirements"]}
        assert "REQ-RAIL-RAMS-001" in requirement_ids
        assert "REQ-RAIL-SAFETYCASE-001" in requirement_ids

        benchmark = client.get(f"/projects/{project['id']}/benchmark/evaluate")
        assert benchmark.status_code == 200
        body = benchmark.json()
        assert body["domain_profile"] == "Railway safety"
        assert any(metric["name"] == "Average requirement quality" for metric in body["metrics"])
        assert body["recommended_next_steps"]

        layout = {"positions": {"project:1": {"x": 520.5, "y": 340.25}}}
        saved = client.put(f"/projects/{project['id']}/knowledge-graph/layout", json=layout)
        assert saved.status_code == 200
        loaded = client.get(f"/projects/{project['id']}/knowledge-graph/layout")
        assert loaded.status_code == 200
        assert loaded.json()["positions"]["project:1"] == {"x": 520.5, "y": 340.2}


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

        dashboard = client.get(f"/projects/{project['id']}/agent-operations/dashboard")
        assert dashboard.status_code == 200
        assert dashboard.json()["total_output_tokens"] == 500
        assert dashboard.json()["average_output_tokens"] == 500.0


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

        backend_dashboard = client.get(
            f"/projects/{project['id']}/agent-operations/dashboard?source_system=agentic_document_ai_platform"
        )
        assert backend_dashboard.status_code == 200
        assert backend_dashboard.json()["total_runs"] == 1
        first_project_dashboard = client.get(
            f"/projects/{project['id']}/agent-operations/dashboard?source_system=autonomous_driving_safety_analyst"
        )
        assert first_project_dashboard.status_code == 200
        assert first_project_dashboard.json()["total_runs"] == 0


def test_autonomous_safety_analyst_workflow_tracking():
    with TestClient(app) as client:
        project = client.post(
            "/projects",
            json={"name": "First Project Workflow", "domain": "ADAS", "system_type": "Autonomous Driving Safety Analyst"},
        ).json()

        bootstrapped = client.post(f"/projects/{project['id']}/workflow/bootstrap-autonomous-safety-analyst")
        assert bootstrapped.status_code == 200
        items = bootstrapped.json()
        assert len(items) == 6
        assert items[0]["source_system"] == "autonomous_driving_safety_analyst"
        assert any(item["workflow_stage"] == "evidence_retrieval" for item in items)

        dashboard = client.get(f"/projects/{project['id']}/workflow/dashboard")
        assert dashboard.status_code == 200
        body = dashboard.json()
        assert body["total_items"] == 6
        assert body["open_items"] == 6
        assert body["completion_rate"] == 0.0

        created = client.post(
            f"/projects/{project['id']}/workflow/items",
            json={
                "title": "Manual evidence review",
                "source_system": "autonomous_driving_safety_analyst",
                "workflow_stage": "quality_review",
                "status": "in_progress",
                "priority": "critical",
                "linked_requirement_id": "REQ-ISO26262-HARA-001",
                "acceptance_criteria": ["Evidence source reviewed", "Decision recorded"],
            },
        )
        assert created.status_code == 200
        created_body = created.json()
        assert created_body["priority"] == "critical"

        updated = client.patch(
            f"/projects/{project['id']}/workflow/items/{created_body['id']}",
            json={"status": "done", "owner": "safety_engineer", "notes": "Reviewed and accepted."},
        )
        assert updated.status_code == 200
        assert updated.json()["status"] == "done"
        assert updated.json()["owner"] == "safety_engineer"

        filtered = client.get(f"/projects/{project['id']}/workflow/items?status=done")
        assert filtered.status_code == 200
        assert any(item["id"] == created_body["id"] for item in filtered.json())

        generic = client.post(
            f"/projects/{project['id']}/workflow/items",
            json={
                "title": "Generic backend workflow item",
                "source_system": "agentic_document_ai_platform",
                "workflow_stage": "intake",
            },
        )
        assert generic.status_code == 200
        source_filtered = client.get(
            f"/projects/{project['id']}/workflow/items?source_system=agentic_document_ai_platform"
        )
        assert len(source_filtered.json()) == 1
        source_dashboard = client.get(
            f"/projects/{project['id']}/workflow/dashboard?source_system=agentic_document_ai_platform"
        )
        assert source_dashboard.json()["total_items"] == 1

        deleted = client.delete(f"/projects/{project['id']}/workflow/items/{generic.json()['id']}")
        assert deleted.status_code == 200
        assert deleted.json()["status"] == "deleted"
        after_delete = client.get(
            f"/projects/{project['id']}/workflow/items?source_system=agentic_document_ai_platform"
        )
        assert after_delete.status_code == 200
        assert after_delete.json() == []


def test_project_conversation_to_action_workflow():
    with TestClient(app) as client:
        project = client.post(
            "/projects",
            json={"name": "Conversation Action Project", "domain": "ADAS", "system_type": "AEB"},
        ).json()

        conversation = client.post(
            f"/projects/{project['id']}/conversations",
            json={"title": "Requirement follow-up", "mode": "requirements_review"},
        )
        assert conversation.status_code == 200
        conversation_body = conversation.json()
        assert conversation_body["message_count"] == 0

        message = client.post(
            f"/projects/{project['id']}/conversations/{conversation_body['id']}/messages",
            json={
                "role": "user",
                "content": "Please review these requirements for missing thresholds, ODD conditions, and verification methods.",
            },
        )
        assert message.status_code == 200
        assert message.json()["intent"] == "requirements_action"

        intent = client.post(f"/projects/{project['id']}/conversations/{conversation_body['id']}/intent-detect")
        assert intent.status_code == 200
        intent_body = intent.json()
        assert intent_body["intent"] == "requirements_action"
        assert "evaluate_requirements" in intent_body["suggested_tools"]

        actions = client.post(
            f"/projects/{project['id']}/conversations/{conversation_body['id']}/actions",
            json={"owner": "safety_engineer", "priority": "high"},
        )
        assert actions.status_code == 200
        action_body = actions.json()
        assert action_body["intent"] == "requirements_action"
        assert action_body["agent_run_id"]
        assert action_body["workflow_items"]
        assert action_body["workflow_items"][0]["source_system"] == "conversation_to_action"
        assert action_body["workflow_items"][0]["workflow_stage"] == "requirements_engineering"

        workflow_items = client.get(
            f"/projects/{project['id']}/workflow/items?source_system=conversation_to_action"
        )
        assert workflow_items.status_code == 200
        assert len(workflow_items.json()) == 1


def test_multi_retrieval_search_across_project_sources():
    content = (
        "REQ-AEB-201: The AEB system shall detect occluded pedestrians at night "
        "within 35 m and verify the result with scenario test evidence. "
        "Linked hazard HZ-AEB-201 and linked safety goal SG-AEB-201."
    )

    with TestClient(app) as client:
        project = client.post(
            "/projects",
            json={"name": "Multi Retrieval Project", "domain": "ADAS", "system_type": "AEB"},
        ).json()

        upload = client.post(
            f"/projects/{project['id']}/documents",
            files={"file": ("multi_retrieval_requirements.txt", content, "text/plain")},
        )
        assert upload.status_code == 200

        extracted = client.post(f"/projects/{project['id']}/requirements/extract")
        assert extracted.status_code == 200
        assert extracted.json()["requirements"]

        test_cases = client.post(f"/projects/{project['id']}/test-cases/generate")
        assert test_cases.status_code == 200
        assert test_cases.json()

        query = client.post(
            f"/projects/{project['id']}/query",
            json={"question": "Find night occluded pedestrian evidence", "include_requirements_review": True},
        )
        assert query.status_code == 200

        orchestration = client.post(
            f"/projects/{project['id']}/agent-tools/run",
            json={
                "user_request": "Search for night occluded pedestrian evidence.",
                "tools": ["search_project_docs"],
                "confidence_score": 0.9,
                "hallucination_risk": "low",
            },
        )
        assert orchestration.status_code == 200
        assert orchestration.json()["tool_results"]["search_project_docs"]["retrieved_docs"]

        response = client.post(
            f"/projects/{project['id']}/retrieval/search",
            json={
                "query": "night occluded pedestrian evidence",
                "tools": [
                    "project_docs",
                    "requirements",
                    "traceability",
                    "test_cases",
                    "evaluation_runs",
                    "agent_runs",
                ],
                "top_k": 3,
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total_results"] >= 6
        assert body["results_by_tool"]["project_docs"]
        assert body["results_by_tool"]["requirements"][0]["title"] == "REQ-AEB-201"
        assert body["results_by_tool"]["traceability"]
        assert body["results_by_tool"]["test_cases"]
        assert body["results_by_tool"]["evaluation_runs"]
        assert body["results_by_tool"]["agent_runs"]

        review = client.post(
            f"/projects/{project['id']}/analysis/precision-review",
            json={
                "query": "Is night occluded pedestrian detection supported by evidence and ISO clauses?",
                "top_k": 5,
                "standards": ["ISO 26262", "ISO 21448", "ISO 8800"],
            },
        )

        assert review.status_code == 200
        review_body = review.json()
        assert "requirements" in review_body["routed_tools"]
        assert review_body["reranked_evidence"]
        assert review_body["citations"]
        assert review_body["compressed_context"]
        assert review_body["requirement_completeness"][0]["requirement_id"] == "REQ-AEB-201"
        assert review_body["human_review_queue"]
        assert review_body["iso_references"]
        assert any(reference["standard"].startswith("ISO 26262") for reference in review_body["iso_references"])
        assert 0.0 <= review_body["confidence_score"] <= 1.0
