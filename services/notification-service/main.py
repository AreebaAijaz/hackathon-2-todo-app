"""Notification Service — logs reminders for tasks approaching due dates.

Listens for reminder events via Dapr pub/sub. When a reminder's scheduled
time is reached, logs a console reminder. Checks if the task is still pending
before sending the reminder.
"""

import logging
import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, Request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("notification-service")

app = FastAPI(title="Notification Service", version="1.0.0")

DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"


@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "notification-service"}


async def check_task_completed(task_id: int) -> bool:
    """Check if a task is already completed via Dapr service invocation.

    Args:
        task_id: The task ID to check.

    Returns:
        True if the task is completed, False if pending or on error.
    """
    url = f"{DAPR_BASE_URL}/v1.0/invoke/backend/method/api/tasks/{task_id}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                url,
                timeout=5.0,
            )
            if resp.status_code == 200:
                task = resp.json()
                return task.get("completed", False)
            # Task not found or other error — assume not completed
            return False
    except Exception as e:
        logger.warning("Failed to check task %s status: %s", task_id, e)
        return False


@app.post("/reminders")
async def handle_reminder(request: Request):
    """Handle reminder events from Dapr pub/sub (CloudEvents envelope).

    Logs a console reminder for tasks approaching their due date.
    Skips reminders for tasks that are already completed.
    """
    body = await request.json()
    event_data = body.get("data", {})

    task_id = event_data.get("task_id")
    title = event_data.get("title", "Unknown task")
    due_at = event_data.get("due_at", "")
    remind_at = event_data.get("remind_at", "")
    user_id = event_data.get("user_id", "")

    logger.info("Received reminder for task %s: '%s' (due: %s)", task_id, title, due_at)

    # Check if task is already completed
    if task_id and await check_task_completed(task_id):
        logger.info("Task %s is already completed, skipping reminder", task_id)
        return {"status": "SUCCESS"}

    # Parse remind_at to check if it's time
    now = datetime.now(timezone.utc)
    try:
        remind_time = datetime.fromisoformat(remind_at.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        remind_time = now  # If unparseable, remind immediately

    if remind_time <= now:
        # Reminder time has passed or is now — log immediately
        logger.warning(
            "REMINDER: Task '%s' is due at %s for user %s",
            title,
            due_at,
            user_id,
        )
    else:
        # Future reminder — log it for now (a production service would schedule)
        logger.info(
            "Scheduled reminder: Task '%s' due at %s (remind at %s) for user %s",
            title,
            due_at,
            remind_at,
            user_id,
        )

    return {"status": "SUCCESS"}
