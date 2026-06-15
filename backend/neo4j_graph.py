"""Optional Neo4j graph sync and Cypher traceability queries."""

from __future__ import annotations

import json
from typing import Any

from backend.schemas import KnowledgeGraphResponse, Neo4jQueryResponse, Neo4jStatus, Neo4jSyncResponse
from backend.settings import settings

try:
    from neo4j import GraphDatabase
except Exception:  # pragma: no cover - optional dependency may be absent
    GraphDatabase = None


NODE_LABELS = {
    "project": "Project",
    "document": "Document",
    "requirement": "Requirement",
    "hazard": "Hazard",
    "safety_goal": "SafetyGoal",
    "test_case": "TestCase",
    "evidence": "Evidence",
    "workflow_item": "WorkflowItem",
    "evaluation_run": "EvaluationRun",
    "agent_run": "AgentRun",
}

RELATIONSHIP_TYPES = {
    "contains_document": "CONTAINS_DOCUMENT",
    "contains_requirement": "CONTAINS_REQUIREMENT",
    "contains_test_case": "CONTAINS_TEST_CASE",
    "supported_by": "SUPPORTED_BY",
    "linked_hazard": "LINKED_HAZARD",
    "linked_safety_goal": "LINKED_SAFETY_GOAL",
    "verified_by": "VERIFIED_BY",
    "requires_evidence": "REQUIRES_EVIDENCE",
    "tracks_workflow_item": "TRACKS_WORKFLOW_ITEM",
    "tracks_requirement": "TRACKS_REQUIREMENT",
    "tracks_hazard": "TRACKS_HAZARD",
    "tracks_safety_goal": "TRACKS_SAFETY_GOAL",
    "has_evaluation_run": "HAS_EVALUATION_RUN",
    "has_agent_run": "HAS_AGENT_RUN",
    "evaluated_by": "EVALUATED_BY",
}

QUERY_TEMPLATES = {
    "missing_test_cases": """
        MATCH (p:Project {project_id: $project_id})-[:CONTAINS_REQUIREMENT]->(r:Requirement)
        WHERE NOT (r)-[:VERIFIED_BY]->(:TestCase)
        RETURN r.id AS requirement_id, r.text AS requirement_text, r.quality_score AS quality_score
        ORDER BY quality_score ASC, requirement_id ASC
    """,
    "missing_hazards": """
        MATCH (p:Project {project_id: $project_id})-[:CONTAINS_REQUIREMENT]->(r:Requirement)
        WHERE NOT (r)-[:LINKED_HAZARD]->(:Hazard)
        RETURN r.id AS requirement_id, r.text AS requirement_text, r.quality_score AS quality_score
        ORDER BY quality_score ASC, requirement_id ASC
    """,
    "missing_safety_goals": """
        MATCH (p:Project {project_id: $project_id})-[:CONTAINS_REQUIREMENT]->(r:Requirement)
        WHERE NOT (r)-[:LINKED_SAFETY_GOAL]->(:SafetyGoal)
        RETURN r.id AS requirement_id, r.text AS requirement_text, r.quality_score AS quality_score
        ORDER BY quality_score ASC, requirement_id ASC
    """,
    "evidence_chain": """
        MATCH (p:Project {project_id: $project_id})-[:CONTAINS_REQUIREMENT]->(r:Requirement)
        WHERE $requirement_id IS NULL OR r.id = $requirement_id
        OPTIONAL MATCH (r)-[:LINKED_HAZARD]->(h:Hazard)
        OPTIONAL MATCH (r)-[:LINKED_SAFETY_GOAL]->(sg:SafetyGoal)
        OPTIONAL MATCH (r)-[:VERIFIED_BY]->(tc:TestCase)
        OPTIONAL MATCH (r)-[:SUPPORTED_BY]->(ev:Evidence)
        RETURN r.id AS requirement_id,
               collect(DISTINCT h.id) AS hazards,
               collect(DISTINCT sg.id) AS safety_goals,
               collect(DISTINCT tc.id) AS test_cases,
               collect(DISTINCT ev.label) AS evidence
        ORDER BY requirement_id ASC
    """,
}


def neo4j_status() -> Neo4jStatus:
    available = GraphDatabase is not None
    if not settings.neo4j_enabled:
        return Neo4jStatus(
            enabled=False,
            available=available,
            uri=settings.neo4j_uri,
            status="disabled",
            message="Set NEO4J_ENABLED=true to sync the traceability graph into Neo4j.",
        )
    if not available:
        return Neo4jStatus(
            enabled=True,
            available=False,
            uri=settings.neo4j_uri,
            status="unavailable",
            message="Install the neo4j Python package to enable graph database sync.",
        )
    try:
        with _driver() as driver:
            driver.verify_connectivity()
    except Exception as exc:
        return Neo4jStatus(
            enabled=True,
            available=True,
            uri=settings.neo4j_uri,
            status="connection_error",
            message=f"Neo4j connection failed: {exc}",
        )
    return Neo4jStatus(
        enabled=True,
        available=True,
        uri=settings.neo4j_uri,
        status="ready",
        message="Neo4j graph sync and Cypher traceability queries are ready.",
    )


def sync_knowledge_graph_to_neo4j(graph: KnowledgeGraphResponse) -> Neo4jSyncResponse:
    status = neo4j_status()
    if status.status != "ready":
        return Neo4jSyncResponse(
            project_id=graph.project_id,
            synced=False,
            message=status.message,
        )

    with _driver() as driver:
        with driver.session() as session:
            session.run("CREATE CONSTRAINT project2_node_id IF NOT EXISTS FOR (n:Project2Node) REQUIRE n.graph_id IS UNIQUE")
            session.run(
                """
                MATCH (n:Project2Node {project_id: $project_id})
                DETACH DELETE n
                """,
                project_id=graph.project_id,
            )
            for node in graph.nodes:
                label = NODE_LABELS.get(node.type, "GraphNode")
                properties = _node_properties(graph.project_id, node.model_dump(mode="json"))
                session.run(
                    f"""
                    MERGE (n:Project2Node:{label} {{graph_id: $graph_id}})
                    SET n += $properties
                    """,
                    graph_id=node.id,
                    properties=properties,
                )
            for edge in graph.edges:
                relationship = RELATIONSHIP_TYPES.get(edge.relationship)
                if not relationship:
                    continue
                session.run(
                    f"""
                    MATCH (source:Project2Node {{graph_id: $source_id}})
                    MATCH (target:Project2Node {{graph_id: $target_id}})
                    MERGE (source)-[rel:{relationship}]->(target)
                    SET rel.relationship = $relationship,
                        rel.label = $label,
                        rel.metadata_json = $metadata_json,
                        rel.project_id = $project_id
                    """,
                    source_id=edge.source,
                    target_id=edge.target,
                    relationship=edge.relationship,
                    label=edge.label,
                    metadata_json=json.dumps(edge.metadata or {}, sort_keys=True),
                    project_id=graph.project_id,
                )
    return Neo4jSyncResponse(
        project_id=graph.project_id,
        synced=True,
        nodes=graph.node_count,
        edges=graph.edge_count,
        message="Synced project traceability graph to Neo4j.",
    )


def run_neo4j_traceability_query(project_id: int, query_type: str, requirement_id: str | None = None) -> Neo4jQueryResponse:
    if query_type not in QUERY_TEMPLATES:
        raise ValueError(f"Unsupported Neo4j query type: {query_type}")
    status = neo4j_status()
    if status.status != "ready":
        return Neo4jQueryResponse(
            project_id=project_id,
            query_type=query_type,
            cypher=QUERY_TEMPLATES[query_type].strip(),
            rows=[{"status": status.status, "message": status.message}],
            row_count=1,
        )
    with _driver() as driver:
        with driver.session() as session:
            result = session.run(
                QUERY_TEMPLATES[query_type],
                project_id=project_id,
                requirement_id=requirement_id,
            )
            rows = [dict(record) for record in result]
    return Neo4jQueryResponse(
        project_id=project_id,
        query_type=query_type,
        cypher=QUERY_TEMPLATES[query_type].strip(),
        rows=rows,
        row_count=len(rows),
    )


def _driver():
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )


def _node_properties(project_id: int, node: dict[str, Any]) -> dict[str, Any]:
    metadata = node.get("metadata") or {}
    return {
        "graph_id": node["id"],
        "project_id": project_id,
        "id": node["id"].split(":", 1)[-1],
        "label": node.get("label"),
        "node_type": node.get("type"),
        "group": node.get("group"),
        "metadata_json": json.dumps(metadata, sort_keys=True),
        "text": metadata.get("text"),
        "quality_score": metadata.get("quality_score"),
        "evidence_source": metadata.get("evidence_source") or metadata.get("source"),
        "status": metadata.get("status"),
        "model_used": metadata.get("model_used"),
    }

