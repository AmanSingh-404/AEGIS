import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url



@pytest.fixture
def integration_engine():
    configured_url = os.getenv("AEGIS_TEST_DATABASE_URL")
    if not configured_url:
        pytest.skip("Set AEGIS_TEST_DATABASE_URL to enable PostgreSQL integration tests")

    url = make_url(configured_url)
    if url.database != "aegis_migration_test":
        pytest.fail(
            "Integration tests may only use the dedicated aegis_migration_test database"
        )

    engine = create_engine(url, pool_pre_ping=True)
    try:
        yield engine
    finally:
        engine.dispose()


def test_postgres_integration_query(integration_engine) -> None:
    with integration_engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()
        result = connection.execute(text("SELECT 1")).scalar_one()

    assert database_name == "aegis_migration_test"
    assert result == 1
