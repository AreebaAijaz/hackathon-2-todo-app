"""Audit Service — persists all task events to an audit_log table.

Listens for all task events via Dapr pub/sub and stores them in a
PostgreSQL audit_log table for accountability and debugging.
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Request
from sqlmodel import Field, Session, SQLModel, create_engine
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import JSONB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("audit-service")

app = FastAPI(title="Audit Service", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL", "")


class AuditRecord(SQLModel, table=True):
    """Audit log entry for task events."""

    __tablename__ = "audit_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(max_length=50)
    task_id: int
    user_id: str = Field(max_length=100)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict = Field(sa_column=Column(JSONB, nullable=False))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


engine = None


def get_engine():
    """Get or create the database engine."""
    global engine
    if engine is None:
        if not DATABASE_URL:
            logger.error("DATABASE_URL not set")
            return None
        # Use psycopg (v3) driver instead of psycopg2
        db_url = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
        engine = create_engine(db_url)
    return engine


@app.on_event("startup")
async def startup():
    """Create audit_log table on startup if it doesn't exist."""
    eng = get_engine()
    if eng is None:
        logger.error("Cannot create audit_log table: no database connection")
        return

    with eng.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(50) NOT NULL,
                task_id INTEGER NOT NULL,
                user_id VARCHAR(100) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                data JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_audit_log_task_id ON audit_log(task_id)"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_audit_log_user_id ON audit_log(user_id)"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_audit_log_event_type ON audit_log(event_type)"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_audit_log_timestamp ON audit_log(timestamp)"
        ))
        conn.commit()
        logger.info("audit_log table ready")


@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "audit-service"}


@app.post("/task-events")
async def handle_task_event(request: Request):
    """Handle task events from Dapr pub/sub and persist to audit_log.

    All events (created, updated, completed, deleted) are stored.
    """
    body = await request.json()
    event_data = body.get("data", {})

    event_type = event_data.get("event_type", "unknown")
    task_id = event_data.get("task_id", 0)
    user_id = event_data.get("user_id", "")
    timestamp_str = event_data.get("timestamp")

    # Parse timestamp
    try:
        ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")) if timestamp_str else datetime.now(timezone.utc)
    except (ValueError, TypeError):
        ts = datetime.now(timezone.utc)

    logger.info("Audit: %s for task %s by user %s", event_type, task_id, user_id)

    eng = get_engine()
    if eng is None:
        logger.error("Cannot persist audit record: no database connection")
        return {"status": "SUCCESS"}

    try:
        with Session(eng) as session:
            record = AuditRecord(
                event_type=event_type,
                task_id=task_id,
                user_id=user_id,
                timestamp=ts,
                data=event_data,
            )
            session.add(record)
            session.commit()
            logger.info("Persisted audit record for task %s (%s)", task_id, event_type)
    except Exception as e:
        logger.error("Failed to persist audit record: %s", e)

    return {"status": "SUCCESS"}
