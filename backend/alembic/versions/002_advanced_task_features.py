"""Add advanced task features: priority, tags, due_date, recurring_pattern, search_vector.

Revision ID: 002_advanced_task
Revises: None (baseline - existing schema already in place via create_all)
Create Date: 2026-02-08

Phase 5A migration: Adds priority, tags, due_date, recurring_pattern,
and full-text search support to existing tasks table.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR

# revision identifiers
revision = "002_advanced_task"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Phase 5A columns, constraints, indexes, and search trigger."""

    # Add new columns with safe defaults for existing rows
    op.add_column(
        "tasks",
        sa.Column(
            "priority",
            sa.String(10),
            server_default="medium",
            nullable=False,
        ),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "tags",
            ARRAY(sa.Text),
            server_default=text("'{}'::text[]"),
            nullable=False,
        ),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "due_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "recurring_pattern",
            sa.String(10),
            server_default="none",
            nullable=False,
        ),
    )
    op.add_column(
        "tasks",
        sa.Column(
            "search_vector",
            TSVECTOR,
            nullable=True,
        ),
    )

    # Add CHECK constraints
    op.create_check_constraint(
        "ck_tasks_priority",
        "tasks",
        "priority IN ('low', 'medium', 'high', 'urgent')",
    )
    op.create_check_constraint(
        "ck_tasks_recurring",
        "tasks",
        "recurring_pattern IN ('none', 'daily', 'weekly', 'monthly')",
    )

    # Add indexes for filtering/sorting performance
    op.create_index("ix_tasks_priority", "tasks", ["priority"])
    op.create_index("ix_tasks_due_date", "tasks", ["due_date"])
    op.create_index("ix_tasks_tags", "tasks", ["tags"], postgresql_using="gin")
    op.create_index(
        "ix_tasks_search", "tasks", ["search_vector"], postgresql_using="gin"
    )

    # Create search vector trigger function
    op.execute(
        """
        CREATE OR REPLACE FUNCTION tasks_search_vector_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('english',
                COALESCE(NEW.title, '') || ' ' || COALESCE(NEW.description, ''));
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # Create trigger on INSERT or UPDATE of title/description
    op.execute(
        """
        CREATE TRIGGER tasks_search_vector_trigger
            BEFORE INSERT OR UPDATE OF title, description
            ON tasks
            FOR EACH ROW
            EXECUTE FUNCTION tasks_search_vector_update();
        """
    )

    # Backfill search_vector for all existing rows
    op.execute(
        """
        UPDATE tasks
        SET search_vector = to_tsvector('english',
            COALESCE(title, '') || ' ' || COALESCE(description, ''));
        """
    )


def downgrade() -> None:
    """Remove Phase 5A columns, constraints, indexes, and search trigger."""

    # Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS tasks_search_vector_trigger ON tasks")
    op.execute("DROP FUNCTION IF EXISTS tasks_search_vector_update()")

    # Drop indexes
    op.drop_index("ix_tasks_search", table_name="tasks")
    op.drop_index("ix_tasks_tags", table_name="tasks")
    op.drop_index("ix_tasks_due_date", table_name="tasks")
    op.drop_index("ix_tasks_priority", table_name="tasks")

    # Drop CHECK constraints
    op.drop_constraint("ck_tasks_recurring", "tasks", type_="check")
    op.drop_constraint("ck_tasks_priority", "tasks", type_="check")

    # Drop columns
    op.drop_column("tasks", "search_vector")
    op.drop_column("tasks", "recurring_pattern")
    op.drop_column("tasks", "due_date")
    op.drop_column("tasks", "tags")
    op.drop_column("tasks", "priority")
