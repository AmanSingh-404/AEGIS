from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from api.models import EvaluationRun, Experiment


def test_experiment_columns_and_jsonb_defaults() -> None:
    table = Experiment.__table__

    assert set(table.columns.keys()) == {
        "id",
        "project_id",
        "name",
        "configuration",
        "model_version",
        "prompt_version",
        "metrics",
        "artifacts",
        "created_at",
    }

    assert isinstance(table.c.configuration.type, JSONB)
    assert table.c.configuration.nullable is False
    assert isinstance(table.c.metrics.type, JSONB)
    assert table.c.metrics.server_default is not None
    assert isinstance(table.c.artifacts.type, JSONB)
    assert table.c.artifacts.server_default is not None


def test_experiment_project_foreign_key_and_index() -> None:
    table = Experiment.__table__

    assert any(
        foreign_key.target_fullname == "projects.id"
        and foreign_key.parent.name == "project_id"
        for foreign_key in table.foreign_keys
    )
    assert {index.name for index in table.indexes} == {
        "idx_experiments_project"
    }


def test_evaluation_run_columns_and_defaults() -> None:
    table = EvaluationRun.__table__

    assert set(table.columns.keys()) == {
        "id",
        "experiment_id",
        "task_id",
        "run_id",
        "benchmark_name",
        "status",
        "metrics",
        "results",
        "created_at",
        "finished_at",
    }

    assert table.c.status.server_default is not None
    assert str(table.c.status.server_default.arg) == "'pending'"

    for column_name in ("metrics", "results"):
        assert isinstance(table.c[column_name].type, JSONB)
        assert table.c[column_name].nullable is False
        assert table.c[column_name].server_default is not None


def test_evaluation_run_foreign_keys_and_indexes() -> None:
    table = EvaluationRun.__table__

    foreign_keys = {
        (foreign_key.parent.name, foreign_key.target_fullname)
        for foreign_key in table.foreign_keys
    }

    assert foreign_keys == {
        ("experiment_id", "experiments.id"),
        ("task_id", "tasks.id"),
        ("run_id", "runs.id"),
    }

    assert {index.name for index in table.indexes} == {
        "idx_evaluation_runs_experiment",
        "idx_evaluation_runs_task",
        "idx_evaluation_runs_run",
    }
