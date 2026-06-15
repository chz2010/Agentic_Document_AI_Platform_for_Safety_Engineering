"""Application settings loaded from this standalone project's environment."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_DIR / ".env")


def project_path(value: str) -> str:
    path = Path(value).expanduser()
    if path.is_absolute():
        return str(path)
    return str(PROJECT_DIR / path)


def env_bool(name: str, default: str = "false") -> bool:
    value = os.getenv(name, default).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


class BackendSettings:
    database_url: str = os.getenv("DATABASE_URL") or f"sqlite:///{project_path('./data/safety_platform.db')}"
    uploads_dir: Path = Path(project_path(os.getenv("UPLOADS_DIR", "./data/uploads")))
    project_chroma_path: str = project_path(os.getenv("PROJECT_CHROMA_PATH", "./vectordb/project_docs"))
    project_collection_name: str = os.getenv("PROJECT_COLLECTION_NAME", "project_documents")
    answer_mode: str = os.getenv("ANSWER_MODE", "none").strip().lower()
    use_openai_generation: bool = env_bool("USE_OPENAI_GENERATION", "true")
    chunk_size: int = int(os.getenv("PROJECT_DOC_CHUNK_SIZE", "900"))
    chunk_overlap: int = int(os.getenv("PROJECT_DOC_CHUNK_OVERLAP", "120"))
    retrieval_k: int = int(os.getenv("PROJECT_RETRIEVAL_K", "6"))
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    local_llm_base_url: str = os.getenv("LOCAL_LLM_BASE_URL", "http://localhost:11434")
    local_llm_model: str = os.getenv("LOCAL_LLM_MODEL", "qwen2.5:7b-instruct")
    local_llm_timeout: int = int(os.getenv("LOCAL_LLM_TIMEOUT", "120"))
    local_llm_num_predict: int = int(os.getenv("LOCAL_LLM_NUM_PREDICT", "1200"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    mlflow_tracking_enabled: bool = env_bool("MLFLOW_TRACKING_ENABLED", "false")
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", project_path("./mlruns"))
    mlflow_experiment_name: str = os.getenv("MLFLOW_EXPERIMENT_NAME", "project2-agentic-document-ai")
    neo4j_enabled: bool = env_bool("NEO4J_ENABLED", "false")
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_username: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "safetygraph")
    demo_username: str = os.getenv("DEMO_USERNAME", "demo@safetyflow.local")
    demo_password: str = os.getenv("DEMO_PASSWORD", "demo-password")
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]


settings = BackendSettings()
