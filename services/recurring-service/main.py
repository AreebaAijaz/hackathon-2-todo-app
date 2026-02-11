"""Recurring Task Service — auto-creates next task instance on completion.

Listens for task.completed events via Dapr pub/sub. When a recurring task
(daily/weekly/monthly) is completed, creates the next instance with the
appropriate future due date via Dapr service invocation to the backend API.
"""

import calendar
import logging
import os
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import FastAPI, Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("recurring-service")

app = FastAPI(title="Recurring Task Service", version="1.0.0")

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"


@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "recurring-service"}


def calculate_next_due_date(
    current_due: str | None,
    pattern: str,
) -> str:
    """Calculate the next occurrence date based on recurring pattern.

    Args:
        current_due: ISO 8601 due date string, or None.
        pattern: One of 'daily', 'weekly', 'monthly'.

    Returns:
        ISO 8601 string for the next due date.
    """
    if current_due:
        try:
            base = datetime.fromisoformat(current_due.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            base = datetime.now(timezone.utc)
    else:
        base = datetime.now(timezone.utc)

    if pattern == "daily":
        next_date = base + timedelta(days=1)
    elif pattern == "weekly":
        next_date = base + timedelta(days=7)
    elif pattern == "monthly":
        year = base.year
        month = base.month + 1
        if month > 12:
            month = 1
            year += 1
        # Handle month-end edge cases (e.g., Jan 31 -> Feb 28)
        max_day = calendar.monthrange(year, month)[1]
        day = min(base.day, max_day)
        next_date = base.replace(year=year, month=month, day=day)
    else:
        next_date = base + timedelta(days=1)

    return next_date.isoformat()


async def create_successor_task(
    task_data: dict,
    next_due_date: str,
    parent_task_id: int,
    user_id: str,
) -> bool:
    """Create a new task via Dapr service invocation to the backend.

    Args:
        task_data: Original task data from the completed event.
        next_due_date: ISO 8601 due date for the new task.
        parent_task_id: ID of the completed task (for idempotency).
        user_id: User ID who owns the task.

    Returns:
        True if created successfully, False otherwise.
    """
    url = f"{DAPR_BASE_URL}/v1.0/invoke/backend/method/api/tasks"
    payload = {
        "title": task_data.get("title", "Recurring task"),
        "description": task_data.get("description", ""),
        "priority": task_data.get("priority", "medium"),
        "tags": task_data.get("tags", []),
        "due_date": next_due_date,
        "recurring_pattern": task_data.get("recurring_pattern", "none"),
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                json=payload,
                timeout=10.0,
            )
            resp.raise_for_status()
            new_task = resp.json()
            logger.info(
                "Created successor task %s for parent %s (due: %s)",
                new_task.get("id"),
                parent_task_id,
                next_due_date,
            )
            return True
    except Exception as e:
        logger.error("Failed to create successor task for %s: %s", parent_task_id, e)
        return False


@app.post("/task-events")
async def handle_task_event(request: Request):
    """Handle task events from Dapr pub/sub (CloudEvents envelope).

    Only processes task.completed events for recurring tasks.
    All other events are acknowledged and ignored.
    """
    body = await request.json()
    event_data = body.get("data", {})

    event_type = event_data.get("event_type")
    task_id = event_data.get("task_id")
    task_data = event_data.get("task_data", {})
    user_id = event_data.get("user_id", "")

    logger.info("Received event: %s for task %s", event_type, task_id)

    # Only process task.completed events
    if event_type != "task.completed":
        return {"status": "SUCCESS"}

    # Only process recurring tasks
    recurring_pattern = task_data.get("recurring_pattern", "none")
    if recurring_pattern == "none":
        logger.info("Task %s is not recurring, skipping", task_id)
        return {"status": "SUCCESS"}

    logger.info(
        "Processing recurring task %s (pattern: %s)",
        task_id,
        recurring_pattern,
    )

    # Calculate next due date
    current_due = task_data.get("due_date")
    next_due = calculate_next_due_date(current_due, recurring_pattern)

    # Create successor task
    await create_successor_task(task_data, next_due, task_id, user_id)

    return {"status": "SUCCESS"}
