"""Remove automated-test projects and duplicate demo workspaces.

The script uses the backend API so relational rows, uploaded files, and Chroma
entries are deleted through the same cleanup path as the application.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from typing import Any

import requests


TEST_PROJECT_NAMES = {
    "AEB Pedestrian Platform",
    "AEB TXT Upload",
    "Agent Operations Project",
    "Agent Ops Project",
    "Conversation Action Project",
    "First Project Workflow",
    "ISO Starter Requirements",
    "Local Engine Selection",
    "Multi Retrieval Project",
    "Neo4j Disabled Query Project",
    "Railway Benchmark Project",
    "Temporary Delete Project",
    "Test",
    "test",
}

DEDUPE_PROJECT_NAMES = {
    "LiDAR",
    "Seed Demo - AEB and Perception Safety Requirements",
}


def request_json(method: str, url: str) -> Any:
    response = requests.request(method, url, timeout=30)
    response.raise_for_status()
    return response.json()


def cleanup_candidates(projects: list[dict[str, Any]]) -> list[tuple[dict[str, Any], str]]:
    candidates: list[tuple[dict[str, Any], str]] = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for project in projects:
        grouped[project.get("name") or ""].append(project)

    for project in projects:
        if project.get("name") in TEST_PROJECT_NAMES:
            candidates.append((project, "automated-test project"))

    for name in DEDUPE_PROJECT_NAMES:
        projects_with_name = sorted(grouped.get(name, []), key=lambda item: item.get("id") or 0)
        if len(projects_with_name) < 2:
            continue
        # Preserve the latest workspace because it is most likely to contain the
        # newest requirements, runs, and presentation state.
        for project in projects_with_name[:-1]:
            candidates.append((project, "duplicate demo workspace"))

    unique: dict[int, tuple[dict[str, Any], str]] = {}
    for project, reason in candidates:
        if project.get("id") is not None:
            unique[int(project["id"])] = (project, reason)
    return sorted(unique.values(), key=lambda item: int(item[0]["id"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-url", default="http://127.0.0.1:8000")
    parser.add_argument("--apply", action="store_true", help="Delete candidates instead of showing a preview.")
    args = parser.parse_args()

    api_url = args.api_url.rstrip("/")
    projects = request_json("GET", f"{api_url}/projects")
    candidates = cleanup_candidates(projects)
    if not candidates:
        print("No automated-test or duplicate demo projects found.")
        return

    for project, reason in candidates:
        print(f"{project['id']:>4}  {project['name']}  [{reason}]")

    if not args.apply:
        print(f"\nPreview only: {len(candidates)} project(s). Re-run with --apply to delete them.")
        return

    for project, _ in candidates:
        request_json("DELETE", f"{api_url}/projects/{project['id']}")
    print(f"\nDeleted {len(candidates)} project(s).")


if __name__ == "__main__":
    main()
