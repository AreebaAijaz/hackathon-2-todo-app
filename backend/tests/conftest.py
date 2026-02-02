"""Shared test fixtures and configuration."""

import os

# CRITICAL: Set environment variables BEFORE importing any app modules
# This prevents database.py from trying to connect to production database
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

import pytest
from sqlmodel import SQLModel, Session, create_engine
from fastapi.testclient import TestClient

from main import app
from database import get_session
from auth.dependencies import get_current_user


TEST_USER_ID = "test-user-id"


@pytest.fixture(name="engine", scope="function")
def engine_fixture():
    """Create an in-memory SQLite engine for testing."""
    # Use check_same_thread=False to allow SQLite usage across threads in tests
    engine = create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=None  # Disable pooling for simplicity
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    # Clean up
    try:
        SQLModel.metadata.drop_all(engine)
    except:
        pass
    engine.dispose()


@pytest.fixture(name="session")
def session_fixture(engine):
    """Create a database session for testing."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def client_fixture(session, engine):
    """Create a TestClient with overridden dependencies."""

    def get_session_override():
        try:
            yield session
        finally:
            pass

    def get_current_user_override():
        return TEST_USER_ID

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_current_user] = get_current_user_override

    # Use context manager to ensure proper cleanup
    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
