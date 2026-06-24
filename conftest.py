"""Keep automated tests isolated from the local demo workspace."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


TEST_RUNTIME_DIR = Path(tempfile.mkdtemp(prefix="safety-platform-tests-"))

# These values must be set before pytest imports backend.main/backend.database.
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_RUNTIME_DIR / 'test_safety_platform.db'}"
os.environ["UPLOADS_DIR"] = str(TEST_RUNTIME_DIR / "uploads")
os.environ["PROJECT_CHROMA_PATH"] = str(TEST_RUNTIME_DIR / "vectordb")
os.environ["PROJECT_COLLECTION_NAME"] = "test_project_documents"
os.environ["OPENAI_API_KEY"] = ""
os.environ["ANSWER_MODE"] = "none"
os.environ["USE_OPENAI_GENERATION"] = "false"
os.environ["MLFLOW_TRACKING_ENABLED"] = "false"
os.environ["NEO4J_ENABLED"] = "false"
os.environ["PROJECT1_MCP_ENABLED"] = "false"
