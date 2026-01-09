"""SQLModel models for the Todo application."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """Task model for todo items.

    Attributes:
        id: Auto-incrementing primary key.
        user_id: Foreign key to Better Auth user table.
        title: Task title (required).
        description: Task description (optional).
        completed: Whether task is complete.
        created_at: Task creation timestamp.
        updated_at: Last update timestamp.
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)  # References Better Auth "user" table
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=500)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
