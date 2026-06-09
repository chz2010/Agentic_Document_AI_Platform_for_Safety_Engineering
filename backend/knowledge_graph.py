"""Build a lightweight traceability knowledge graph from persisted project data."""

from __future__ import annotations

from collections import Counter
from typing import Any

from backend.models import AgentRunLogRecord, EvaluationRunRecord, Project, ProjectDocument, TestCaseRecord, WorkflowItemRecord
from backend.schemas import KnowledgeGraphEdge, KnowledgeGraphNode, KnowledgeGraphResponse, Requirement, TraceabilityLink


def build_project_knowledge_graph(
    project: Project,
    documents: list[ProjectDocument],
    requirements: list[Requirement],
    traceability: list[TraceabilityLink],
    test_cases: list[TestCaseRecord],
    workflow_items: list[WorkflowItemRecord],
    evaluation_runs: list[EvaluationRunRecord],
    agent_runs: list[AgentRunLogRecord],
) -> KnowledgeGraphResponse:
    nodes: dict[str, KnowledgeGraphNode] = {}
    edges: list[KnowledgeGraphEdge] = []
    edge_keys: set[tuple[str, str, str]] = set()

    def add_node(node_id: str, label: str, node_type: str, group: str | None = None, metadata: dict[str, Any] | None = None) -> None:
        if node_id not in nodes:
            nodes[node_id] = KnowledgeGraphNode(
                id=node_id,
                label=label,
                type=node_type,
                group=group or node_type,
                metadata=metadata or {},
            )

    def add_edge(source: str, target: str, relationship: str, label: str | None = None, metadata: dict[str, Any] | None = None) -> None:
        key = (source, target, relationship)
        if source in nodes and target in nodes and key not in edge_keys:
            edge_keys.add(key)
            edges.append(
                KnowledgeGraphEdge(
                    source=source,
                    target=target,
                    relationship=relationship,
                    label=label or relationship.replace("_", " "),
                    metadata=metadata or {},
                )
            )

    project_id = f"project:{project.id}"
    add_node(
        project_id,
        project.name,
        "project",
        metadata={
            "domain": project.domain,
            "system_type": project.system_type,
            "standards_scope": project.standards_scope,
        },
    )

    for document in documents:
        document_id = f"document:{document.id}"
        add_node(
            document_id,
            document.filename,
            "document",
            metadata={
                "source_type": document.source_type,
                "chunk_count": document.chunk_count,
                "created_at": document.created_at.isoformat(),
            },
        )
        add_edge(project_id, document_id, "contains_document")

    for requirement in requirements:
        requirement_id = f"requirement:{requirement.id}"
        add_node(
            requirement_id,
            requirement.id,
            "requirement",
            metadata={
                "type": requirement.type.value if hasattr(requirement.type, "value") else str(requirement.type),
                "text": requirement.text,
                "quality_score": requirement.quality_score,
                "quality_issues": requirement.quality_issues,
                "suggested_improvement": requirement.suggested_improvement,
                "evidence_source": requirement.evidence_source,
            },
        )
        add_edge(project_id, requirement_id, "contains_requirement")

        if requirement.evidence_source:
            evidence_id = f"evidence:{_slug(requirement.evidence_source)}"
            add_node(evidence_id, _short_label(requirement.evidence_source, 44), "evidence", metadata={"source": requirement.evidence_source})
            add_edge(requirement_id, evidence_id, "supported_by")

        if requirement.linked_hazard:
            hazard_id = f"hazard:{requirement.linked_hazard}"
            add_node(hazard_id, requirement.linked_hazard, "hazard")
            add_edge(requirement_id, hazard_id, "linked_hazard")

        if requirement.linked_safety_goal:
            safety_goal_id = f"safety_goal:{requirement.linked_safety_goal}"
            add_node(safety_goal_id, requirement.linked_safety_goal, "safety_goal")
            add_edge(requirement_id, safety_goal_id, "linked_safety_goal")

        for test_case_id in requirement.linked_test_cases:
            test_node_id = f"test_case:{test_case_id}"
            add_node(test_node_id, test_case_id, "test_case")
            add_edge(requirement_id, test_node_id, "verified_by")

    for row in traceability:
        requirement_node_id = f"requirement:{row.requirement_id}"
        if row.hazard_id:
            hazard_id = f"hazard:{row.hazard_id}"
            add_node(hazard_id, row.hazard_id, "hazard", metadata={"description": row.hazard_description})
            add_edge(requirement_node_id, hazard_id, "linked_hazard")
        if row.safety_goal_id:
            safety_goal_id = f"safety_goal:{row.safety_goal_id}"
            add_node(safety_goal_id, row.safety_goal_id, "safety_goal")
            add_edge(requirement_node_id, safety_goal_id, "linked_safety_goal")
        if row.test_case_id:
            test_node_id = f"test_case:{row.test_case_id}"
            add_node(test_node_id, row.test_case_id, "test_case")
            add_edge(requirement_node_id, test_node_id, "verified_by", metadata={"status": row.status})
        if row.evidence_source:
            evidence_id = f"evidence:{_slug(row.evidence_source)}"
            add_node(evidence_id, _short_label(row.evidence_source, 44), "evidence", metadata={"source": row.evidence_source})
            add_edge(requirement_node_id, evidence_id, "supported_by")

    for record in test_cases:
        payload = record.payload or {}
        test_node_id = f"test_case:{record.test_case_id}"
        add_node(
            test_node_id,
            record.test_case_id,
            "test_case",
            metadata={
                "scenario": payload.get("scenario"),
                "expected_result": payload.get("expected_result"),
                "pass_fail_criteria": payload.get("pass_fail_criteria"),
            },
        )
        add_edge(project_id, test_node_id, "contains_test_case")
        linked_requirement = payload.get("linked_requirement")
        if linked_requirement:
            add_edge(f"requirement:{linked_requirement}", test_node_id, "verified_by")
        for evidence in payload.get("required_evidence") or []:
            evidence_id = f"evidence:{_slug(str(evidence))}"
            add_node(evidence_id, _short_label(str(evidence), 44), "evidence", metadata={"source": evidence})
            add_edge(test_node_id, evidence_id, "requires_evidence")

    for item in workflow_items:
        workflow_id = f"workflow:{item.id}"
        add_node(
            workflow_id,
            item.title,
            "workflow_item",
            group="workflow",
            metadata={
                "stage": item.workflow_stage,
                "status": item.status,
                "priority": item.priority,
                "source_system": item.source_system,
                "description": item.description,
            },
        )
        add_edge(project_id, workflow_id, "tracks_workflow_item")
        if item.linked_requirement_id:
            add_edge(workflow_id, f"requirement:{item.linked_requirement_id}", "tracks_requirement")
        if item.linked_hazard_id:
            hazard_id = f"hazard:{item.linked_hazard_id}"
            add_node(hazard_id, item.linked_hazard_id, "hazard")
            add_edge(workflow_id, hazard_id, "tracks_hazard")
        if item.linked_safety_goal_id:
            safety_goal_id = f"safety_goal:{item.linked_safety_goal_id}"
            add_node(safety_goal_id, item.linked_safety_goal_id, "safety_goal")
            add_edge(workflow_id, safety_goal_id, "tracks_safety_goal")

    for run in evaluation_runs:
        run_id = f"evaluation:{run.id}"
        add_node(
            run_id,
            f"{run.run_type} #{run.id}",
            "evaluation_run",
            group="evaluation",
            metadata={
                "model_used": run.model_used,
                "quality_score": run.quality_score,
                "latency_ms": run.latency_ms,
                "created_at": run.created_at.isoformat(),
            },
        )
        add_edge(project_id, run_id, "has_evaluation_run")

    for run in agent_runs:
        run_id = f"agent_run:{run.id}"
        add_node(
            run_id,
            f"{run.operation_name} #{run.id}",
            "agent_run",
            group="agent_ops",
            metadata={
                "status": run.status,
                "model_used": run.model_used,
                "prompt_version": run.prompt_version,
                "estimated_cost_usd": run.estimated_cost_usd,
                "human_escalation_required": run.human_escalation_required,
            },
        )
        add_edge(project_id, run_id, "has_agent_run")
        if run.evaluation_run_id:
            add_edge(run_id, f"evaluation:{run.evaluation_run_id}", "evaluated_by")

    coverage_summary = _coverage_summary(project.id or 0, requirements, traceability, test_cases, workflow_items, nodes, edges)
    return KnowledgeGraphResponse(
        project_id=project.id or 0,
        nodes=list(nodes.values()),
        edges=edges,
        node_count=len(nodes),
        edge_count=len(edges),
        coverage_summary=coverage_summary,
    )


def _coverage_summary(
    project_id: int,
    requirements: list[Requirement],
    traceability: list[TraceabilityLink],
    test_cases: list[TestCaseRecord],
    workflow_items: list[WorkflowItemRecord],
    nodes: dict[str, KnowledgeGraphNode],
    edges: list[KnowledgeGraphEdge],
) -> dict[str, Any]:
    total_requirements = len(requirements)
    test_case_requirement_links = {
        str((record.payload or {}).get("linked_requirement"))
        for record in test_cases
        if (record.payload or {}).get("linked_requirement")
    }
    linked_hazards = sum(1 for requirement in requirements if requirement.linked_hazard)
    linked_safety_goals = sum(1 for requirement in requirements if requirement.linked_safety_goal)
    linked_test_cases = sum(1 for requirement in requirements if requirement.linked_test_cases or requirement.id in test_case_requirement_links)
    linked_evidence = sum(1 for requirement in requirements if requirement.evidence_source)
    node_types = Counter(node.type for node in nodes.values())
    edge_types = Counter(edge.relationship for edge in edges)

    return {
        "project_id": project_id,
        "requirements_total": total_requirements,
        "traceability_rows": len(traceability),
        "test_cases_total": len(test_cases),
        "workflow_items_total": len(workflow_items),
        "hazard_link_coverage": round(linked_hazards / total_requirements, 3) if total_requirements else 0.0,
        "safety_goal_link_coverage": round(linked_safety_goals / total_requirements, 3) if total_requirements else 0.0,
        "test_case_link_coverage": round(linked_test_cases / total_requirements, 3) if total_requirements else 0.0,
        "evidence_link_coverage": round(linked_evidence / total_requirements, 3) if total_requirements else 0.0,
        "graph_density": round(len(edges) / len(nodes), 3) if nodes else 0.0,
        "node_types": dict(node_types),
        "edge_types": dict(edge_types),
    }


def _short_label(value: str, max_length: int) -> str:
    return value if len(value) <= max_length else value[: max_length - 3].rstrip() + "..."


def _slug(value: str) -> str:
    slug = "".join(character.lower() if character.isalnum() else "-" for character in value)
    slug = "-".join(part for part in slug.split("-") if part)
    return slug[:96] or "unknown"
