
-- AEGIS schema_v1.sql
-- DESIGN DRAFT ONLY. DO NOT APPLY TO A LIVE DATABASE.
-- Source: AEGIS Extended Specification, Section 18.
-- Column definitions and constraints below are proposed where the
-- specification lists only table names and purposes.
-- PostgreSQL; pgvector required for document embeddings.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT,
    identity_provider TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE projects (
    id UUID PRIMARY KEY,
    owner_id UUID NOT NULL REFERENCES users(id),
    name TEXT NOT NULL,
    description TEXT,
    settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id),
    created_by UUID NOT NULL REFERENCES users(id),
    objective TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    input_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    result JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE runs (
    id UUID PRIMARY KEY,
    task_id UUID NOT NULL REFERENCES tasks(id),
    status TEXT NOT NULL DEFAULT 'pending',
    attempt INTEGER NOT NULL DEFAULT 1 CHECK (attempt > 0),
    state JSONB NOT NULL DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    error JSONB
);

CREATE TABLE run_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES runs(id),
    event_type TEXT NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    model_id UUID REFERENCES models(id),
    tokens_input INTEGER,
    tokens_output INTEGER,
    estimated_cost NUMERIC(14, 8),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE agents (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (name, version)
);

CREATE TABLE models (
    id UUID PRIMARY KEY,
    provider TEXT NOT NULL,
    model_name TEXT NOT NULL,
    configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (provider, model_name)
);

CREATE TABLE tools (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    input_schema JSONB NOT NULL,
    output_schema JSONB NOT NULL,
    permissions JSONB NOT NULL DEFAULT '[]'::jsonb,
    risk_level TEXT NOT NULL,
    timeout_seconds INTEGER NOT NULL CHECK (timeout_seconds > 0),
    audit_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    origin TEXT NOT NULL CHECK (origin IN ('registered', 'forged')),
    version TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE approvals (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES runs(id),
    requested_by UUID REFERENCES users(id),
    reviewed_by UUID REFERENCES users(id),
    action_type TEXT NOT NULL,
    action_payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    decision_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at TIMESTAMPTZ
);

CREATE TABLE experiments (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    name TEXT NOT NULL,
    configuration JSONB NOT NULL,
    model_version TEXT,
    prompt_version TEXT,
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    artifacts JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE evaluation_runs (
    id UUID PRIMARY KEY,
    experiment_id UUID REFERENCES experiments(id),
    task_id UUID REFERENCES tasks(id),
    run_id UUID REFERENCES runs(id),
    benchmark_name TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    metrics JSONB NOT NULL DEFAULT '{}'::jsonb,
    results JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ
);

CREATE TABLE memories (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    task_id UUID REFERENCES tasks(id),
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES projects(id),
    source_uri TEXT,
    title TEXT,
    content_hash TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE chunks (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL CHECK (chunk_index >= 0),
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (document_id, chunk_index)
);

CREATE TABLE capability_gaps (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES tasks(id),
    run_id UUID REFERENCES runs(id),
    description TEXT NOT NULL,
    task_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'detected',
    priority_score DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);

CREATE TABLE tool_candidates (
    id UUID PRIMARY KEY,
    capability_gap_id UUID NOT NULL REFERENCES capability_gaps(id),
    name TEXT NOT NULL,
    implementation TEXT NOT NULL,
    schema JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'drafted',
    sandbox_results JSONB,
    static_analysis_results JSONB,
    jev_prescreen JSONB,
    promotion_decision JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    reviewed_at TIMESTAMPTZ
);

CREATE TABLE tool_versions (
    id UUID PRIMARY KEY,
    tool_id UUID NOT NULL REFERENCES tools(id),
    version TEXT NOT NULL,
    implementation TEXT NOT NULL,
    schema JSONB NOT NULL,
    test_results JSONB NOT NULL DEFAULT '{}'::jsonb,
    static_analysis_results JSONB NOT NULL DEFAULT '{}'::jsonb,
    promotion_status TEXT NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (tool_id, version)
);

CREATE TABLE decision_log (
    id UUID PRIMARY KEY,
    run_id UUID REFERENCES runs(id),
    state_summary JSONB NOT NULL,
    question_type TEXT NOT NULL CHECK (
        question_type IN ('choice', 'score', 'noul')
    ),
    question JSONB NOT NULL,
    answer JSONB NOT NULL,
    confidence DOUBLE PRECISION CHECK (
        confidence >= 0 AND confidence <= 1
    ),
    escalated BOOLEAN NOT NULL DEFAULT FALSE,
    escalation_outcome JSONB,
    agreement BOOLEAN,
    provider TEXT NOT NULL,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Initial indexes for common lookups and foreign-key joins.
CREATE INDEX idx_projects_owner ON projects(owner_id);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_tasks_creator ON tasks(created_by);
CREATE INDEX idx_runs_task ON runs(task_id);
CREATE INDEX idx_run_events_run_time ON run_events(run_id, created_at);
CREATE INDEX idx_approvals_status ON approvals(status);
CREATE INDEX idx_evaluation_runs_experiment ON evaluation_runs(experiment_id);
CREATE INDEX idx_memories_project ON memories(project_id);
CREATE INDEX idx_documents_project ON documents(project_id);
CREATE INDEX idx_chunks_document ON chunks(document_id);
CREATE INDEX idx_capability_gaps_status ON capability_gaps(status);
CREATE INDEX idx_candidates_gap ON tool_candidates(capability_gap_id);
CREATE INDEX idx_candidates_status ON tool_candidates(status);
CREATE INDEX idx_tool_versions_tool ON tool_versions(tool_id);
CREATE INDEX idx_decision_log_created ON decision_log(created_at);
CREATE INDEX idx_decision_log_run ON decision_log(run_id);

-- Add a vector index after confirming the embedding model and dimensions.
-- The VECTOR(1536) dimension above is a provisional design assumption.
