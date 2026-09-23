import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class RunStatus(enum.StrEnum):
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    RUNNING = "running"
    PAUSED = "paused"
    DONE = "done"
    FAILED = "failed"


class StepStatus(enum.StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"
    FAILED = "failed"


class EventType(enum.StrEnum):
    PLAN = "plan"
    SEARCH = "search"
    READ = "read"
    THINK = "think"
    SUBAGENT_START = "subagent_start"
    SUBAGENT_DONE = "subagent_done"
    SYNTHESIS = "synthesis"
    CITATION = "citation"
    ERROR = "error"
    INTERRUPT = "interrupt"


class ResearchRun(Base):
    __tablename__ = "research_runs"
    # Run list queries: "my recent runs by status" / "my recent runs".
    __table_args__ = (
        Index("ix_research_runs_status_created_at", "status", "created_at"),
        Index("ix_research_runs_user_created_at", "user_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # Set when the run was spawned from a conversation.
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"), index=True
    )
    question: Mapped[str] = mapped_column(Text)
    status: Mapped[RunStatus] = mapped_column(String(30), default=RunStatus.PLANNING)
    plan: Mapped[dict | None] = mapped_column(JSONB)
    report: Mapped[str | None] = mapped_column(Text)
    report_json: Mapped[dict | None] = mapped_column(JSONB)
    model: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error: Mapped[str | None] = mapped_column(Text)

    plan_steps: Mapped[list["PlanStep"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", order_by="PlanStep.step_order"
    )
    subagent_tasks: Mapped[list["SubagentTask"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    sources: Mapped[list["Source"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )
    events: Mapped[list["RunEvent"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", order_by="RunEvent.ts"
    )


class PlanStep(Base):
    __tablename__ = "plan_steps"
    # A step order is unique within a run.
    __table_args__ = (UniqueConstraint("run_id", "step_order", name="uq_plan_steps_run_order"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("research_runs.id", ondelete="CASCADE"), index=True
    )
    step_order: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[StepStatus] = mapped_column(String(20), default=StepStatus.PENDING)
    searches: Mapped[list | None] = mapped_column(JSONB)

    run: Mapped[ResearchRun] = relationship(back_populates="plan_steps")


class SubagentTask(Base):
    __tablename__ = "subagent_tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("research_runs.id", ondelete="CASCADE"), index=True
    )
    plan_step_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("plan_steps.id", ondelete="SET NULL"), index=True
    )
    objective: Mapped[str] = mapped_column(Text)
    status: Mapped[StepStatus] = mapped_column(String(20), default=StepStatus.PENDING)
    findings: Mapped[str | None] = mapped_column(Text)
    sources: Mapped[list | None] = mapped_column(JSONB)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)

    run: Mapped[ResearchRun] = relationship(back_populates="subagent_tasks")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("research_runs.id", ondelete="CASCADE"), index=True
    )
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    snippet: Mapped[str | None] = mapped_column(Text)
    first_seen_step: Mapped[int | None] = mapped_column(Integer)
    credibility_hint: Mapped[str | None] = mapped_column(String(50))

    run: Mapped[ResearchRun] = relationship(back_populates="sources")


class RunEvent(Base):
    __tablename__ = "run_events"
    # Hottest table: append-only, polled by SSE. Composite index serves
    # "events for a run in order". Partition by ts when volume demands it.
    __table_args__ = (Index("ix_run_events_run_id_ts", "run_id", "ts"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("research_runs.id", ondelete="CASCADE"))
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    type: Mapped[EventType] = mapped_column(String(30))
    payload: Mapped[dict | None] = mapped_column(JSONB)

    run: Mapped[ResearchRun] = relationship(back_populates="events")


class RunFollowup(Base):
    """A follow-up Q&A on a finished report ("chat with your report")."""

    __tablename__ = "run_followups"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("research_runs.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
