import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class MemorySource(enum.StrEnum):
    MANUAL = "manual"  # user wrote it
    AUTO = "auto"  # derived from runs (provenance via origin_run_id)


class DocumentStatus(enum.StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class UserMemory(Base):
    """A fact scout remembers about a user across runs (ChatGPT-style memory)."""

    __tablename__ = "user_memories"
    __table_args__ = (
        Index(
            "ix_user_memories_user_active",
            "user_id",
            postgresql_where=text("is_active"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[MemorySource] = mapped_column(String(10), default=MemorySource.MANUAL)
    # Which run produced this memory (set when source=auto).
    origin_run_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("research_runs.id", ondelete="SET NULL")
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Document(Base):
    """A user-uploaded file (PDF, MD, TXT, …) usable as research context.

    Binary content lives in object storage (or local disk in dev) — never in
    the DB. `storage_key` is the pointer; `sha256` gives per-user dedupe.
    """

    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("user_id", "sha256", name="uq_documents_user_sha256"),
        Index("ix_documents_user_created_at", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    filename: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str | None] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(default=0)
    sha256: Mapped[str] = mapped_column(String(64))
    storage_key: Mapped[str] = mapped_column(Text)
    status: Mapped[DocumentStatus] = mapped_column(String(20), default=DocumentStatus.PENDING)
    error: Mapped[str | None] = mapped_column(Text)
    page_count: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DocumentChunk(Base):
    """A retrievable piece of a document.

    `user_id` is denormalized on purpose: tenant-scoped retrieval (and later,
    tenant-filtered vector search) must filter by user without joining
    documents. The embedding column itself arrives with the RAG step, once we
    pick an embedding model and dimension.
    """

    __tablename__ = "document_chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunks_doc_idx"),
        Index("ix_document_chunks_user_id", "user_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    page_number: Mapped[int | None] = mapped_column(Integer)
