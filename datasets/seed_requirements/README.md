# Seed Requirements Dataset

This dataset is a compact automotive safety engineering sample for the Agentic
Document AI Platform. It is not a replacement for ISO 26262, ISO 21448, or an
OEM requirements database. Its purpose is to provide clean demo material for
the requirements engineering workflow.

## Files

- `automotive_safety_requirements.jsonl`: structured requirements with hazards,
  safety goals, expected quality issues, and test case links.
- `automotive_safety_requirements.csv`: table view for spreadsheet inspection.
- `automotive_safety_requirements.md`: document-style source for upload and RAG
  demonstrations.
- `lidar_perception_safety_case.md`: synthetic LiDAR perception safety-case
  document with hazards, safety goals, strong requirements, intentionally weak
  requirements, evidence sources, and test cases.

## Suggested Demo Flow

1. Ingest the seed dataset into a demo project.
2. Run requirement evaluation.
3. Generate a traceability matrix.
4. Generate test cases.
5. Query the project about gaps such as night-time occlusion or missing
   measurable thresholds.

Example:

```bash
python scripts/ingest_seed_requirements.py
```

Then open:

```text
http://127.0.0.1:8000/docs
```

The seed data intentionally includes both strong and weak requirements so the
quality scoring module has visible behavior.
