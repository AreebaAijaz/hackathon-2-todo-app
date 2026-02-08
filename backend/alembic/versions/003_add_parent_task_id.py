"""Add parent_task_id for recurring task lineage tracking.

Revision ID: 003_parent_task_id
Revises: 002_advanced_task
Create Date: 2026-02-08

Phase 5B migration: Adds parent_task_id column to tasks table
for linking recurring task instances to their parent task.
Used by the recurring task service for idempotency checks.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "003_parent_task_id"
down_revision = "002_advanced_task"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add parent_task_id column with foreign key and index."""
    op.add_column(
        "tasks",
        sa.Column("parent_task_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_tasks_parent_task_id",
        "tasks",
        "tasks",
        ["parent_task_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_tasks_parent_task_id", "tasks", ["parent_task_id"])


def downgrade() -> None:
    """Remove parent_task_id column."""
    op.drop_index("ix_tasks_parent_task_id", table_name="tasks")
    op.drop_constraint("fk_tasks_parent_task_id", "tasks", type_="foreignkey")
    op.drop_column("tasks", "parent_task_id")
