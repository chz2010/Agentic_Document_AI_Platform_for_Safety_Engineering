# Lovable Frontend Prompt

Build a polished frontend for an existing FastAPI backend called **Agentic Document AI Platform for Safety Engineering**.

This is not a landing page. Build the actual application UI. The app helps safety engineers upload safety documents, ask project-specific RAG questions, extract and evaluate requirements, inspect traceability, review a knowledge graph, monitor agent operations, manage workflow items, and export reports.

## Product Positioning

Create a professional SaaS-style safety engineering workspace for:

- automotive safety engineers
- ADAS engineers
- railway safety engineers
- AI safety engineers
- requirements engineers

The visual style should be dark, precise, technical, and dashboard-like. It should feel like a serious engineering operations tool, not a marketing website.

## Backend API

The backend base URL must be configurable in the UI. Default:

```text
http://127.0.0.1:8000
```

Use REST calls to this FastAPI backend.

Core endpoints:

```text
GET  /health

POST /projects
GET  /projects
GET  /projects/{project_id}
DELETE /projects/{project_id}

POST /projects/{project_id}/documents
GET  /projects/{project_id}/documents

POST /projects/{project_id}/query
POST /projects/{project_id}/retrieval/search
POST /projects/{project_id}/analysis/precision-review

POST /projects/{project_id}/requirements/extract
POST /projects/{project_id}/requirements/generate-from-standards
POST /projects/{project_id}/requirements/evaluate

GET  /projects/{project_id}/traceability
GET  /projects/{project_id}/knowledge-graph
POST /projects/{project_id}/test-cases/generate

GET  /projects/{project_id}/evaluation-runs
GET  /projects/{project_id}/agent-runs
GET  /projects/{project_id}/agent-operations/dashboard
POST /projects/{project_id}/agent-tools/run

POST /projects/{project_id}/workflow/bootstrap-autonomous-safety-analyst
POST /projects/{project_id}/workflow/items
GET  /projects/{project_id}/workflow/items
PATCH /projects/{project_id}/workflow/items/{item_id}
DELETE /projects/{project_id}/workflow/items/{item_id}
GET  /projects/{project_id}/workflow/dashboard

GET  /projects/{project_id}/report?format=markdown
GET  /projects/{project_id}/report?format=requirements_csv
GET  /projects/{project_id}/report?format=traceability_csv
GET  /projects/{project_id}/report?format=json
```

## Required Pages / Views

### 1. Workspace

Left sidebar:

- backend URL input
- backend health status
- project selector
- create project form
- delete project action with confirmation

Project create fields:

- name
- domain
- system type
- standards scope
- description

### 2. Overview Dashboard

Show KPI cards:

- project count or active project
- uploaded documents
- requirements
- traceability rows
- evaluation runs
- agent runs
- average quality score
- average latency
- total cost
- output tokens

Use dashboard panels and charts, not plain JSON.

### 3. Documents

Allow upload of PDF, TXT, Markdown, CSV, DOCX if the backend accepts it.

Show uploaded document table:

- filename
- source type
- chunk count
- created at

### 4. Ask / RAG Query

Input:

- question textarea
- standards multiselect
- include requirements review checkbox
- answer engine selector:
  - OpenAI
  - Local model
  - Deterministic evidence synthesis
- model selector, shown only when relevant

Call:

```text
POST /projects/{project_id}/query
```

Display:

- answer in readable Markdown
- retrieved sources
- missing requirements
- recommended requirements
- evaluation run id
- answer engine and model used

### 5. Requirements Engineering

Actions:

- extract requirements
- generate ISO starter requirements
- generate test cases
- evaluate requirements

Display:

- quality score cards
- issue frequency chart
- requirement table with wrapped text
- requirement type badges
- quality issues
- linked hazard
- linked safety goal
- suggested improvement

### 6. Traceability

Display traceability matrix:

```text
Hazard -> Safety Goal -> Requirement -> Test Case -> Evidence -> Status
```

Use a wide table with wrapped text and filters.

Add export button for traceability CSV.

### 7. Knowledge Graph

Call:

```text
GET /projects/{project_id}/knowledge-graph
```

Display:

- node count
- edge count
- hazard coverage
- safety goal coverage
- test coverage
- graph density

Render a clean graph visualization. Nodes should be reasonable size, not huge.

Node types:

- project
- document
- evidence
- hazard
- safety_goal
- requirement
- test_case
- workflow_item
- evaluation_run
- agent_run

Relationship inspection:

- Let the user select a relationship/edge.
- Show source node, relationship type, target node, and metadata.
- Highlight the selected relationship in the graph.

### 8. Agent Operations

Call:

```text
GET /projects/{project_id}/agent-operations/dashboard
GET /projects/{project_id}/agent-runs
```

Display Grafana-style panels:

- success rate
- escalation rate
- average latency
- average cost
- total cost
- output tokens
- hallucination flags
- average evaluation score
- pending approvals

Show agent run table:

- operation
- status
- model
- prompt version
- tools used
- latency
- tokens
- cost
- failure reason
- human escalation required

### 9. Workflow

Call workflow endpoints.

Show a workflow board for:

- intake
- evidence retrieval
- quality review
- requirements engineering
- traceability
- reporting

Allow:

- create workflow item
- update status
- update owner
- remove item
- bootstrap first-project workflow

### 10. Reports

Show:

- Markdown report preview
- structured report summary
- requirements export
- traceability export
- JSON report in a professional grouped view, not raw JSON only

## UI Requirements

- Use a dark, professional, dashboard-like interface.
- Avoid marketing hero sections.
- Do not use oversized cards.
- Text must fit inside tables and panels.
- Long requirement text must wrap.
- Use tabs or a sidebar navigation.
- Use clear badges for status, priority, type, and risk.
- Use charts for agent operations and evaluation metrics.
- Use icons for actions where useful.
- Keep it recruiter-demo ready.

## Technical Requirements

- Use React + TypeScript.
- Use a typed API client.
- Keep the backend URL configurable.
- Handle API errors gracefully.
- Show loading states.
- Keep components modular.
- Do not hardcode API responses.
- Do not require authentication for the first version.

## Demo Flow To Support

The UI should support this video demo flow:

1. Select or create a project.
2. Upload a safety requirements document.
3. Ask a safety/requirements question.
4. Show retrieved evidence.
5. Extract requirements.
6. Show quality scoring.
7. Generate test cases.
8. Show traceability matrix.
9. Show knowledge graph.
10. Show agent operations metrics.
11. Show workflow tracking.
12. Export report.

## Important

The FastAPI backend already exists. Do not mock the entire product. Build a frontend that calls the backend endpoints above. If the backend is unavailable, show a clear offline state and keep the UI usable enough to configure the backend URL.
