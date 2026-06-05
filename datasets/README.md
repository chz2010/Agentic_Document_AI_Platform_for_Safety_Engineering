# Datasets

This folder contains small, tracked datasets for demos and tests. Runtime
uploads, local databases, and vector stores stay in `data/` and `vectordb/`,
which are ignored by Git.

## Seed Requirements Dataset

`seed_requirements/` contains a curated automotive safety requirements seed
dataset. It is intentionally small so the backend can demonstrate requirements
engineering behavior without downloading large public datasets first.

The seed set covers:

- AEB pedestrian detection
- lane keeping and lane departure prevention
- perception monitoring
- dataset coverage
- validation and evidence requirements
- traceability from hazards to safety goals, requirements, and test cases

Use it to verify:

- requirement extraction
- requirement quality scoring
- traceability matrix generation
- test case generation
- project-specific RAG retrieval
- agent operations logging

Public datasets such as PURE or Dronology can be added later as benchmark
sources, but this seed set keeps the first demo focused and recruiter-readable.
