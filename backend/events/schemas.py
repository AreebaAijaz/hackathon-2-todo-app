"""Event schemas for Dapr pub/sub event publishing."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TaskEventData(BaseModel):
    """Snapshot of task data included in events."""

    id: int
    user_id: str
    title: str
    description: str
    completed: bool
    priority: str
    tags: List[str]
    due_date: Optional[datetime] = None
    recurring_pattern: str
    created_at: datetime
    updated_at: datetime


class TaskEvent(BaseModel):
    """Domain event for task mutations, published to task-events topic."""

    event_type: str  # task.created, task.updated, task.completed, task.deleted
    task_id: int
    task_data: TaskEventData
    user_id: str
    timestamp: datetime


class ReminderEvent(BaseModel):
    """Reminder event published to reminders topic for tasks with due dates."""

    task_id: int
    title: str
    due_at: datetime
    remind_at: datetime
    user_id: str
