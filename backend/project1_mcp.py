"""MCP client for the Project 1 Autonomous Driving Safety Analyst."""

from __future__ import annotations

import asyncio
import json
import re
from datetime import timedelta
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

from backend.requirements_engineering import classify_requirement, score_requirement, suggest_requirement_improvement
from backend.schemas import Requirement
from backend.settings import settings


def project1_mcp_status() -> dict[str, Any]:
    if not settings.project1_mcp_enabled:
        return {
            "enabled": False,
            "connected": False,
            "status": "disabled",
            "message": "Project 1 MCP integration is disabled.",
        }
    try:
        payload = call_project1_tool("get_knowledge_base_status", {})
    except Exception as exc:
        return {
            "enabled": True,
            "connected": False,
            "status": "connection_error",
            "message": str(exc),
            "project_dir": str(settings.project1_mcp_project_dir),
        }
    return {
        "enabled": True,
        "connected": payload.get("status") == "ok",
        "status": payload.get("status", "unknown"),
        "message": "Connected to the Autonomous Driving Safety Analyst MCP knowledge base.",
        "project_dir": str(settings.project1_mcp_project_dir),
        "databases": payload.get("databases", {}),
    }


def call_project1_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if not settings.project1_mcp_enabled:
        raise RuntimeError("Project 1 MCP integration is disabled.")
    project_dir = settings.project1_mcp_project_dir
    python_path = settings.project1_mcp_python
    server_path = project_dir / settings.project1_mcp_server
    if not project_dir.exists():
        raise RuntimeError(f"Project 1 directory does not exist: {project_dir}")
    if not python_path.exists():
        raise RuntimeError(f"Project 1 Python executable does not exist: {python_path}")
    if not server_path.exists():
        raise RuntimeError(f"Project 1 MCP server does not exist: {server_path}")
    return asyncio.run(_call_tool(tool_name, arguments))


async def _call_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    parameters = StdioServerParameters(
        command=str(settings.project1_mcp_python),
        args=[settings.project1_mcp_server],
        cwd=str(settings.project1_mcp_project_dir),
    )
    timeout = timedelta(seconds=settings.project1_mcp_timeout)
    async with stdio_client(parameters) as streams:
        async with ClientSession(*streams, read_timeout_seconds=timeout) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments, read_timeout_seconds=timeout)
    if result.isError:
        text = " ".join(getattr(item, "text", "") for item in result.content)
        raise RuntimeError(text or f"Project 1 MCP tool failed: {tool_name}")
    if isinstance(result.structuredContent, dict):
        return result.structuredContent
    for item in result.content:
        text = getattr(item, "text", None)
        if text:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                return parsed
    return {"status": "ok", "content": [item.model_dump(mode="json") for item in result.content]}


def search_project1_standards(
    query: str,
    standards: list[str],
    k_per_standard: int = 4,
) -> dict[str, Any]:
    searches: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    for standard in standards:
        payload = call_project1_tool(
            "search_safety_standards",
            {
                "query": query,
                "k": max(1, min(k_per_standard, 10)),
                "standard": standard,
                "embedding_backend": settings.project1_mcp_embedding_backend,
            },
        )
        searches.append(
            {
                "standard": standard,
                "status": payload.get("status"),
                "result_count": payload.get("result_count", 0),
            }
        )
        for item in payload.get("results", []):
            results.append(item)
    return {
        "status": "ok",
        "query": query,
        "standards": standards,
        "searches": searches,
        "result_count": len(results),
        "results": results,
    }


def generate_grounded_requirements(
    project_name: str,
    domain: str,
    system_type: str,
    standards: list[str],
    existing_requirements: list[Requirement],
    evidence: list[dict[str, Any]],
    max_requirements: int = 8,
) -> list[Requirement]:
    """Generate missing requirement candidates grounded in Project 1 MCP evidence."""
    if not settings.openai_api_key or not evidence:
        return []

    evidence_rows = []
    for index, item in enumerate(evidence, start=1):
        metadata = item.get("metadata") or {}
        evidence_rows.append(
            {
                "index": index,
                "standard": metadata.get("standard"),
                "clause": metadata.get("clause"),
                "page": metadata.get("page"),
                "section": metadata.get("section_title"),
                "filename": metadata.get("filename"),
                "content": item.get("content"),
            }
        )
    existing_rows = [
        {
            "id": requirement.id,
            "text": requirement.text,
            "type": requirement.type.value,
            "linked_hazard": requirement.linked_hazard,
            "linked_safety_goal": requirement.linked_safety_goal,
        }
        for requirement in existing_requirements
    ]
    prompt = (
        "You are a safety requirements engineer. Compare the existing project requirements with the retrieved "
        "standards evidence. Generate only genuinely missing or materially weak requirement candidates. "
        "Every requirement must be atomic, measurable where the evidence supports a threshold, testable, and "
        "tailored to the described system. Do not invent exact clause numbers, thresholds, hazards, or safety goals. "
        "Use only the evidence supplied below. Return strict JSON with this shape: "
        '{"requirements":[{"text":"...","evidence_indices":[1,2]}]}. '
        f"Return at most {max_requirements} requirements.\n\n"
        f"Project: {project_name}\nDomain: {domain}\nSystem type: {system_type}\n"
        f"Standards scope: {', '.join(standards)}\n\n"
        f"Existing requirements:\n{json.dumps(existing_rows, ensure_ascii=False)}\n\n"
        f"Retrieved MCP evidence:\n{json.dumps(evidence_rows, ensure_ascii=False)}"
    )
    response = OpenAI(api_key=settings.openai_api_key).chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": "Generate evidence-grounded safety requirement gaps as strict JSON. Never claim compliance.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    payload = json.loads(content)
    generated: list[Requirement] = []
    existing_texts = {_normalize(requirement.text) for requirement in existing_requirements}
    for index, item in enumerate(payload.get("requirements", [])[:max_requirements], start=1):
        text = " ".join(str(item.get("text") or "").split())
        if len(text) < 25 or _normalize(text) in existing_texts:
            continue
        cited = [
            evidence_rows[evidence_index - 1]
            for evidence_index in item.get("evidence_indices", [])
            if isinstance(evidence_index, int) and 1 <= evidence_index <= len(evidence_rows)
        ]
        if not cited:
            continue
        source = "; ".join(_evidence_citation(row) for row in cited[:3])
        score, issues, _ = score_requirement(text, None, None)
        generated.append(
            Requirement(
                id=f"REQ-MCP-{_standard_slug(cited[0].get('standard'))}-{index:03d}",
                type=classify_requirement(text),
                text=text,
                quality_score=score.overall,
                quality_issues=issues,
                suggested_improvement=suggest_requirement_improvement(
                    issues,
                    None,
                    None,
                    [],
                    source,
                ),
                evidence_source=source,
            )
        )
        existing_texts.add(_normalize(text))
    return generated


def standards_gap_query(
    project_name: str,
    domain: str,
    system_type: str,
    existing_requirements: list[Requirement],
) -> str:
    existing_summary = " ".join(requirement.text for requirement in existing_requirements[:20])
    return (
        f"{project_name}; {domain}; {system_type}. Identify applicable safety requirement, validation, "
        f"monitoring, data, ODD, failure-handling, and evidence expectations that may be missing. "
        f"Existing requirement summary: {existing_summary[:6000]}"
    )


def _evidence_citation(row: dict[str, Any]) -> str:
    standard = row.get("standard") or "Project 1 standards database"
    parts = [str(standard)]
    if row.get("clause"):
        parts.append(f"clause {row['clause']}")
    if row.get("page"):
        parts.append(f"page {row['page']}")
    if row.get("section"):
        parts.append(str(row["section"]))
    return ", ".join(parts)


def _standard_slug(value: Any) -> str:
    slug = re.sub(r"[^A-Z0-9]+", "", str(value or "STANDARD").upper())
    return slug[:18] or "STANDARD"


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
