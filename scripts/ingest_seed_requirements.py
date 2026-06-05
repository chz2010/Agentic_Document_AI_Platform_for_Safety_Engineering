#!/usr/bin/env python3
"""Ingest the tracked automotive seed requirements into a demo project."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from langchain_core.documents import Document as LangchainDocument
from sqlmodel import Session, select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database import engine, init_db
from backend.document_processing import chunk_documents
from backend.models import DocumentChunk, Project, ProjectDocument, RequirementRecord
from backend.seed_data import SEED_DOCUMENT_PATH, load_seed_requirements, seed_document_text
from backend.settings import settings
from backend.vector_store import get_project_vector_store


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a demo project from the seed requirements dataset.")
    parser.add_argument("--project-name", default="Seed Demo - AEB and Perception Safety Requirements")
    parser.add_argument("--domain", default="Autonomous driving")
    parser.add_argument("--system-type", default="ADAS safety engineering")
    parser.add_argument("--keep-existing", action="store_true", help="Append instead of replacing seed requirements for the project.")
    args = parser.parse_args()

    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    Path(settings.project_chroma_path).mkdir(parents=True, exist_ok=True)
    init_db()

    with Session(engine) as session:
        project = _get_or_create_project(session, args.project_name, args.domain, args.system_type)
        project_id = project.id
        requirements = load_seed_requirements()
        if not args.keep_existing:
            _delete_project_requirements(session, project_id)
        _store_requirements(session, project_id, requirements)
        chunk_count = _store_seed_document(session, project_id)
        session.commit()

    print(f"Seed project ID: {project_id}")
    print(f"Stored requirements: {len(requirements)}")
    print(f"Stored vector chunks: {chunk_count}")
    print("Next: start the API and open http://127.0.0.1:8000/docs")


def _get_or_create_project(session: Session, name: str, domain: str, system_type: str) -> Project:
    project = session.exec(select(Project).where(Project.name == name)).first()
    if project:
        return project
    project = Project(
        name=name,
        domain=domain,
        system_type=system_type,
        standards_scope=["ISO 26262", "ISO 21448", "ISO 8800"],
        description="Demo project populated from the tracked seed requirements dataset.",
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


def _delete_project_requirements(session: Session, project_id: int) -> None:
    for record in session.exec(select(RequirementRecord).where(RequirementRecord.project_id == project_id)).all():
        session.delete(record)


def _store_requirements(session: Session, project_id: int, requirements) -> None:
    existing_ids = {
        record.requirement_id
        for record in session.exec(select(RequirementRecord).where(RequirementRecord.project_id == project_id)).all()
    }
    for req in requirements:
        if req.id in existing_ids:
            continue
        session.add(
            RequirementRecord(
                project_id=project_id,
                requirement_id=req.id,
                requirement_type=req.type.value,
                text=req.text,
                linked_hazard=req.linked_hazard,
                linked_safety_goal=req.linked_safety_goal,
                quality_score=req.quality_score,
                quality_issues=req.quality_issues,
                suggested_improvement=req.suggested_improvement,
                linked_test_cases=req.linked_test_cases,
                evidence_source=req.evidence_source,
            )
        )


def _store_seed_document(session: Session, project_id: int) -> int:
    filename = SEED_DOCUMENT_PATH.name
    vector_store = get_project_vector_store()
    old_chunks = session.exec(
        select(DocumentChunk).where(DocumentChunk.project_id == project_id, DocumentChunk.chunk_id.contains("-seed-"))
    ).all()
    if old_chunks:
        try:
            vector_store.delete(ids=[chunk.chunk_id for chunk in old_chunks])
        except Exception:
            pass
        for chunk in old_chunks:
            session.delete(chunk)
    for document in session.exec(
        select(ProjectDocument).where(ProjectDocument.project_id == project_id, ProjectDocument.filename == filename)
    ).all():
        session.delete(document)
    session.commit()

    db_doc = ProjectDocument(
        project_id=project_id,
        filename=filename,
        source_type="md",
        storage_path=str(SEED_DOCUMENT_PATH),
    )
    session.add(db_doc)
    session.commit()
    session.refresh(db_doc)

    docs = [LangchainDocument(page_content=seed_document_text(), metadata={"page": None, "section": "seed_requirements"})]
    chunks = chunk_documents(docs)
    vector_docs: list[LangchainDocument] = []
    ids: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_id = f"project-{project_id}-seed-{index:04d}"
        ids.append(chunk_id)
        metadata = {
            "project_id": str(project_id),
            "document_id": str(db_doc.id),
            "document": db_doc.filename,
            "source_type": "seed_requirements",
            "chunk_id": chunk_id,
            "section": chunk.metadata.get("section", "seed_requirements"),
        }
        vector_docs.append(LangchainDocument(page_content=chunk.page_content, metadata=metadata))
        session.add(
            DocumentChunk(
                project_id=project_id,
                document_id=db_doc.id,
                chunk_id=chunk_id,
                page=None,
                section=metadata["section"],
                text_preview=chunk.page_content[:400],
            )
        )
    if vector_docs:
        vector_store.add_documents(vector_docs, ids=ids)
    db_doc.chunk_count = len(vector_docs)
    session.add(db_doc)
    return len(vector_docs)


if __name__ == "__main__":
    main()
