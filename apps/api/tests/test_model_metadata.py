from api.models import Base


EXPECTED_INDEXES = {
    "idx_projects_owner",
    "idx_project_members_user",
    "idx_tasks_project",
    "idx_tasks_creator",
    "idx_runs_task",
    "idx_run_events_run_time",
    "idx_run_events_model",
    "idx_approvals_status",
    "idx_approvals_run",
    "idx_approvals_requested_by",
    "idx_approvals_reviewed_by",
    "idx_approval_events_approval",
    "idx_approval_events_created_at",
    "idx_experiments_project",
    "idx_evaluation_runs_experiment",
    "idx_evaluation_runs_task",
    "idx_evaluation_runs_run",
    "idx_memories_project",
    "idx_memories_task",
    "idx_documents_project",
    "idx_capability_gaps_status",
    "idx_capability_gaps_task",
    "idx_capability_gaps_run",
    "idx_candidates_gap",
    "idx_tool_audit_events_created_at",
    "idx_tool_audit_events_version",
    "idx_tool_audit_events_candidate",
    "idx_decision_log_run",
    "idx_decision_log_created",
    "idx_tool_versions_tool",
}


def test_current_model_table_set() -> None:
    assert set(Base.metadata.tables) == {
        "users",
        "projects",
        "project_members",
        "tasks",
        "runs",
        "models",
        "run_events",
        "agents",
        "tools",
        "approvals",
        "approval_events",
        "experiments",
        "evaluation_runs",
        "memories",
        "documents",
        "chunks",
        "capability_gaps",
        "tool_candidates",
        "tool_versions",
        "decision_log",
        "tool_audit_events",
    }


def test_current_model_named_indexes() -> None:
    actual_indexes = {
        index.name
        for table in Base.metadata.tables.values()
        for index in table.indexes
    }
    assert actual_indexes == EXPECTED_INDEXES
