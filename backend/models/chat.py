import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class MessageRole(enum.StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base):
    """A free-form chat thread between a user and the assistant.

    Distinct from a research run: a conversation is interactive and cheap;
    a run is a plan-first, minutes-long pipeline. A run can be spawned *from*
    a conversation (`research_runs.conversation_id`).
    """

    __tablename__ = "conversations"
    __table_args__ = (Index("ix_conversations_user_updated_at", "user_id", "updated_at"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # Set by the fast model after the first exchange; nullable until then.
    title: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at"
    )


class Message(Base):
    __tablename__ = "messages"
    # History loads in order; the table is append-only and partitionable later.
    __table_args__ = (
        Index("ix_messages_conversation_created_at", "conversation_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    # Denormalized like document_chunks.user_id: tenancy filter without a join.
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[MessageRole] = mapped_column(String(10))
    content: Mapped[str] = mapped_column(Text)
    model: Mapped[str | None] = mapped_column(String(100))  # set on assistant messages
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation: Mapped[Conversation] = relationship(back_populates="messages")
