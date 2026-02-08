"""Dapr event publishing helper — fire-and-forget via HTTP API."""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx

from models import Task
from .schemas import TaskEvent, TaskEventData, ReminderEvent

logger = logging.getLogger(__name__)

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"
PUBSUB_NAME = "kafka-pubsub"

# Reminder offset: 1 hour before due date
REMINDER_OFFSET = timedelta(hours=1)


def _build_task_event_data(task: Task) -> TaskEventData:
    """Build a TaskEventData snapshot from a Task model instance."""
    return TaskEventData(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
        priority=task.priority,
        tags=task.tags or [],
        due_date=task.due_date,
        recurring_pattern=task.recurring_pattern,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


async def _publish(topic: str, data: dict) -> bool:
    """Publish a message to a Dapr pub/sub topic. Fire-and-forget."""
    url = f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=data, timeout=5.0)
            resp.raise_for_status()
            logger.info("Published event to %s: %s", topic, data.get("event_type", "reminder"))
            return True
    except Exception as e:
        logger.warning("Failed to publish to %s: %s", topic, e)
        return False


async def publish_task_event(event_type: str, task: Task, user_id: str) -> bool:
    """Publish a task domain event to the task-events topic.

    Args:
        event_type: One of task.created, task.updated, task.completed, task.deleted.
        task: The Task model instance.
        user_id: The user who performed the action.

    Returns:
        True if published successfully, False otherwise.
    """
    event = TaskEvent(
        event_type=event_type,
        task_id=task.id,
        task_data=_build_task_event_data(task),
        user_id=user_id,
        timestamp=datetime.now(timezone.utc),
    )
    return await _publish("task-events", event.model_dump(mode="json"))


async def publish_reminder_event(task: Task, user_id: str) -> Optional[bool]:
    """Publish a reminder event if the task has a due date.

    Args:
        task: The Task model instance.
        user_id: The user who owns the task.

    Returns:
        True if published, False if failed, None if no due date.
    """
    if not task.due_date:
        return None

    remind_at = task.due_date - REMINDER_OFFSET
    event = ReminderEvent(
        task_id=task.id,
        title=task.title,
        due_at=task.due_date,
        remind_at=remind_at,
        user_id=user_id,
    )
    return await _publish("reminders", event.model_dump(mode="json"))


def publish_task_event_sync(event_type: str, task: Task, user_id: str) -> None:
    """Sync wrapper for publish_task_event — fire-and-forget from sync MCP tools.

    Schedules the async publish as a background task on the running event loop.
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(publish_task_event(event_type, task, user_id))
    except RuntimeError:
        logger.warning("No event loop available for sync event publishing")


def publish_reminder_event_sync(task: Task, user_id: str) -> None:
    """Sync wrapper for publish_reminder_event — fire-and-forget from sync MCP tools."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(publish_reminder_event(task, user_id))
    except RuntimeError:
        logger.warning("No event loop available for sync reminder publishing")
