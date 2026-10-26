from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import VECTOR

from api.models import Chunk, Document, Memory


def test_memory_columns_defaults_and_indexes() -> None:
    table = Memory.__table__

    assert set(table.columns.keys()) == {
        "id", "project_id", "task_id", "memory_type",
        "content", "metadata", "created_at",
    }
    assert table.c.project_id.nullable is True
    assert table.c.task_id.nullable is True
    assert isinstance(table.c.metadata.type, JSONB)
    assert table.c.metadata.server_default is not None
    assert {index.name for index in table.indexes} == {
        "idx_memories_project",
        "idx_memories_task",
    }


def test_document_columns_defaults_and_project_foreign_key() -> None:
    table = Document.__table__

    assert set(table.columns.keys()) == {
        "id", "project_id", "source_uri", "title",
        "content_hash", "metadata", "created_at",
    }
    assert table.c.project_id.nullable is False
    assert isinstance(table.c.metadata.type, JSONB)
    assert table.c.metadata.server_default is not None
    assert any(
        fk.parent.name == "project_id"
        and fk.target_fullname == "projects.id"
        for fk in table.foreign_keys
    )
    assert {index.name for index in table.indexes} == {
        "idx_documents_project",
    }


def test_chunk_vector_and_document_cascade() -> None:
    table = Chunk.__table__

    assert set(table.columns.keys()) == {
        "id", "document_id", "chunk_index",
        "content", "embedding", "metadata",
    }
    assert isinstance(table.c.embedding.type, VECTOR)
    assert table.c.embedding.type.dim is None
    assert table.c.embedding.nullable is True

    document_fk = next(
        fk for fk in table.c.document_id.foreign_keys
        if fk.target_fullname == "documents.id"
    )
    assert document_fk.ondelete == "CASCADE"
    assert table.c.document_id.nullable is False
    assert table.c.chunk_index.nullable is False


def test_chunk_index_constraint_and_document_uniqueness() -> None:
    table = Chunk.__table__

    check_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, CheckConstraint)
    ]
    assert any(
        constraint.name == "chunks_chunk_index_check"
        and "chunk_index >= 0" in str(constraint.sqltext)
        for constraint in check_constraints
    )

    unique_constraints = [
        constraint
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    assert any(
        {column.name for column in constraint.columns}
        == {"document_id", "chunk_index"}
        for constraint in unique_constraints
    )
