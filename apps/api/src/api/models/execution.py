from sqlalchemy import (
    CheckConstraint,
    BigInteger,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from pgvector.sqlalchemy import VECTOR
from sqlalchemy.orm import Mapped, mapped_column

from api.models.base import Base
class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'awaiting_approval', "
            "'completed', 'failed', 'cancelled')",
            name="chk_tasks_status",
        ),
        Index("idx_tasks_project", "project_id"),
        Index("idx_tasks_creator", "created_by"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[object] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    created_by: Mapped[object] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'pending'")
    )
    input_data: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    result: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = (
        CheckConstraint("attempt > 0", name="runs_attempt_check"),
        CheckConstraint(
            "status IN ('pending', 'running', 'awaiting_approval', "
            "'completed', 'failed', 'cancelled')",
            name="chk_runs_status",
        ),
        Index("idx_runs_task", "task_id"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    task_id: Mapped[object] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'pending'")
    )
    attempt: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
    state: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    started_at: Mapped[object | None] = mapped_column(TIMESTAMP(timezone=True))
    finished_at: Mapped[object | None] = mapped_column(TIMESTAMP(timezone=True))
    error: Mapped[dict[str, object] | None] = mapped_column(JSONB)


class Model(Base):
    __tablename__ = "models"
    __table_args__ = (
        UniqueConstraint("provider", "model_name"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    configuration: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    enabled: Mapped[bool] = mapped_column(
        nullable=False, server_default=text("TRUE")
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class RunEvent(Base):
    __tablename__ = "run_events"
    __table_args__ = (
        Index("idx_run_events_run_time", "run_id", "created_at"),
        Index("idx_run_events_model", "model_id"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    run_id: Mapped[object] = mapped_column(
        UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    event_data: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    model_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("models.id")
    )
    tokens_input: Mapped[int | None] = mapped_column(Integer)
    tokens_output: Mapped[int | None] = mapped_column(Integer)
    estimated_cost: Mapped[object | None] = mapped_column(Numeric(14, 8))
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )




class Agent(Base):
    __tablename__ = "agents"
    __table_args__ = (
        UniqueConstraint("name", "version"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    configuration: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    enabled: Mapped[bool] = mapped_column(
        nullable=False, server_default=text("TRUE")
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Tool(Base):
    __tablename__ = "tools"
    __table_args__ = (
        ForeignKeyConstraint(
            ["id", "version"],
            ["tool_versions.tool_id", "tool_versions.version"],
            name="fk_tools_current_version",
            use_alter=True,
            deferrable=True,
            initially="DEFERRED",
        ),
        CheckConstraint(
            "timeout_seconds > 0",
            name="tools_timeout_seconds_check",
        ),
        CheckConstraint(
            "origin IN ('registered', 'forged')",
            name="tools_origin_check",
        ),
        UniqueConstraint("name", "version", name="uq_tools_name_version"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    input_schema: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    output_schema: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    permissions: Mapped[list[object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    risk_level: Mapped[str] = mapped_column(Text, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    audit_metadata: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    origin: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(Text, nullable=False)
    enabled: Mapped[bool] = mapped_column(
        nullable=False, server_default=text("TRUE")
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Approval(Base):
    __tablename__ = "approvals"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'cancelled')",
            name="chk_approvals_status",
        ),
        Index("idx_approvals_status", "status"),
        Index("idx_approvals_run", "run_id"),
        Index("idx_approvals_requested_by", "requested_by"),
        Index("idx_approvals_reviewed_by", "reviewed_by"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    run_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("runs.id")
    )
    requested_by: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    reviewed_by: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    action_type: Mapped[str] = mapped_column(Text, nullable=False)
    action_payload: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'pending'")
    )
    decision_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    reviewed_at: Mapped[object | None] = mapped_column(TIMESTAMP(timezone=True))


class ApprovalEvent(Base):
    __tablename__ = "approval_events"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('requested', 'approved', 'rejected', "
            "'cancelled', 'reassigned')",
            name="approval_events_event_type_check",
        ),
        Index("idx_approval_events_approval", "approval_id"),
        Index("idx_approval_events_created_at", "created_at"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    approval_id: Mapped[object] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approvals.id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    reason: Mapped[str | None] = mapped_column(Text)
    event_data: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Experiment(Base):
    __tablename__ = "experiments"
    __table_args__ = (
        Index("idx_experiments_project", "project_id"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id")
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    configuration: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    model_version: Mapped[str | None] = mapped_column(Text)
    prompt_version: Mapped[str | None] = mapped_column(Text)
    metrics: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    artifacts: Mapped[list[object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    __table_args__ = (
        Index("idx_evaluation_runs_experiment", "experiment_id"),
        Index("idx_evaluation_runs_task", "task_id"),
        Index("idx_evaluation_runs_run", "run_id"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    experiment_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experiments.id")
    )
    task_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id")
    )
    run_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("runs.id")
    )
    benchmark_name: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'pending'")
    )
    metrics: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    results: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    finished_at: Mapped[object | None] = mapped_column(TIMESTAMP(timezone=True))


class Memory(Base):
    __tablename__ = "memories"
    __table_args__ = (
        Index("idx_memories_project", "project_id"),
        Index("idx_memories_task", "task_id"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id")
    )
    task_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id")
    )
    memory_type: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index("idx_documents_project", "project_id"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[object] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False
    )
    source_uri: Mapped[str | None] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )


class Chunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (
        CheckConstraint("chunk_index >= 0", name="chunks_chunk_index_check"),
        UniqueConstraint("document_id", "chunk_index"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    document_id: Mapped[object] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[object | None] = mapped_column(VECTOR(), nullable=True)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )




class CapabilityGap(Base):
    __tablename__ = "capability_gaps"
    __table_args__ = (
        CheckConstraint(
            "status IN ('detected', 'investigating', 'tool_candidate_created', "
            "'resolved', 'unresolved', 'dismissed')",
            name="chk_capability_gaps_status",
        ),
        Index("idx_capability_gaps_status", "status"),
        Index("idx_capability_gaps_task", "task_id"),
        Index("idx_capability_gaps_run", "run_id"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    task_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id")
    )
    run_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("runs.id")
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    task_context: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'detected'")
    )
    priority_score: Mapped[float | None] = mapped_column()
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    resolved_at: Mapped[object | None] = mapped_column(TIMESTAMP(timezone=True))


class ToolCandidate(Base):
    __tablename__ = "tool_candidates"
    __table_args__ = (
        CheckConstraint(
            "status IN ('drafted', 'sandboxed', 'screened', "
            "'pending-approval', 'promoted', 'rejected')",
            name="chk_tool_candidates_status",
        ),
        Index("idx_candidates_gap", "capability_gap_id"),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    capability_gap_id: Mapped[object] = mapped_column(
        UUID(as_uuid=True), ForeignKey("capability_gaps.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    implementation: Mapped[str] = mapped_column(Text, nullable=False)
    schema_: Mapped[dict[str, object]] = mapped_column(
        "schema", JSONB, nullable=False
    )
    status: Mapped[str] = mapped_column(
        Text, nullable=False, server_default=text("'drafted'")
    )
    sandbox_results: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    static_analysis_results: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    jev_prescreen: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    promotion_decision: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    reviewed_at: Mapped[object | None] = mapped_column(TIMESTAMP(timezone=True))

class ToolVersion(Base):
    """Immutable record of a registered tool implementation version."""

    __tablename__ = "tool_versions"
    __table_args__ = (
        Index("idx_tool_versions_tool", "tool_id"),
        UniqueConstraint("tool_id", "version", name="uq_tool_versions_tool_version"),
        CheckConstraint(
            "promotion_status IN ('pending', 'approved', 'promoted', 'rejected', 'revoked')",
            name="chk_tool_versions_promotion_status",
        ),
        CheckConstraint(
            "(promotion_status = 'revoked' AND revoked_at IS NOT NULL) OR "
            "(promotion_status <> 'revoked' AND revoked_at IS NULL)",
            name="chk_tool_versions_revocation_timestamp",
        ),
    )

    id: Mapped[object] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tool_id: Mapped[object] = mapped_column(UUID(as_uuid=True), ForeignKey("tools.id"), nullable=False)
    candidate_id: Mapped[object | None] = mapped_column(UUID(as_uuid=True),
        ForeignKey("tool_candidates.id"), unique=True
    )
    version: Mapped[str] = mapped_column(Text, nullable=False)
    implementation: Mapped[str] = mapped_column(Text, nullable=False)
    schema_: Mapped[dict[str, object]] = mapped_column("schema", JSONB, nullable=False)
    test_results: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    static_analysis_results: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    promotion_status: Mapped[str] = mapped_column(Text, nullable=False)
    revoked_at: Mapped[object | None] = mapped_column(TIMESTAMP(timezone=True))
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

class DecisionLog(Base):
    __tablename__ = "decision_log"
    __table_args__ = (
        Index("idx_decision_log_created", "created_at"),
        Index("idx_decision_log_run", "run_id"),
        CheckConstraint(
            "question_type IN ('choice', 'score', 'noul')",
            name="decision_log_question_type_check",
        ),
        CheckConstraint(
            "confidence >= 0 AND confidence <= 1",
            name="decision_log_confidence_check",
        ),
    )

    id: Mapped[object] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    run_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("runs.id")
    )
    state_summary: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False
    )
    question_type: Mapped[str] = mapped_column(Text, nullable=False)
    question: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False
    )
    answer: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False
    )
    confidence: Mapped[float | None] = mapped_column()
    escalated: Mapped[bool] = mapped_column(
        nullable=False, server_default=text("false")
    )
    escalation_outcome: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    agreement: Mapped[bool | None] = mapped_column()
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

class ToolAuditEvent(Base):
    __tablename__ = "tool_audit_events"
    __table_args__ = (
        Index("idx_tool_audit_events_candidate", "candidate_id"),
        Index("idx_tool_audit_events_version", "tool_version_id"),
        Index("idx_tool_audit_events_created_at", "created_at"),
        CheckConstraint(
            "event_type IN ("
            "'candidate_created', "
            "'static_analysis_completed', "
            "'sandbox_validation_completed', "
            "'jev_prescreen_completed', "
            "'review_approved', "
            "'promotion_approved', "
            "'promotion_rejected', "
            "'version_promoted', "
            "'version_revoked'"
            ")",
            name="tool_audit_events_event_type_check",
        ),
        CheckConstraint(
            "candidate_id IS NOT NULL OR tool_version_id IS NOT NULL",
            name="chk_tool_audit_event_has_reference",
        ),
    )

    id: Mapped[object] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    candidate_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tool_candidates.id")
    )
    tool_version_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tool_versions.id")
    )
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[object | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    details: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[object] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
