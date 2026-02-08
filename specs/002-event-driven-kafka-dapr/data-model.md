# Data Model: Phase 5B - Event-Driven Architecture

**Date**: 2026-02-08
**Feature**: 002-event-driven-kafka-dapr

## Entity Changes

### Existing Entity: Task (Modified)

Add one new optional column for recurring task lineage tracking:

```sql
-- Migration: 003_add_parent_task_id
ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER NULL REFERENCES tasks(id) ON DELETE SET NULL;
CREATE INDEX ix_tasks_parent_task_id ON tasks(parent_task_id);
```

**Field**: `parent_task_id`
- Type: INTEGER, nullable
- Purpose: Links a recurring task instance to the task it was created from
- Set by: Recurring task service when auto-creating the next instance
- Used by: Recurring task service for idempotency checks
- Not exposed in user-facing API (internal field)

### New Entity: AuditRecord

Stored by the audit service. Uses the same Neon database but a new table.

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    task_id INTEGER NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_audit_log_task_id ON audit_log(task_id);
CREATE INDEX ix_audit_log_user_id ON audit_log(user_id);
CREATE INDEX ix_audit_log_event_type ON audit_log(event_type);
CREATE INDEX ix_audit_log_timestamp ON audit_log(timestamp);
```

**Fields**:
- `id`: Auto-increment primary key
- `event_type`: One of `task.created`, `task.updated`, `task.completed`, `task.deleted`
- `task_id`: Reference to the task (not FK since task may be deleted)
- `user_id`: The user who performed the action
- `timestamp`: When the event occurred (from event payload)
- `data`: Full event payload as JSON
- `created_at`: When the audit record was stored

## Event Schemas

### TaskEvent (Published to `task-events` topic)

```json
{
  "event_type": "task.created | task.updated | task.completed | task.deleted",
  "task_id": 42,
  "task_data": {
    "id": 42,
    "user_id": "abc123",
    "title": "Buy groceries",
    "description": "Get milk, eggs, bread",
    "completed": false,
    "priority": "high",
    "tags": ["shopping", "errands"],
    "due_date": "2026-02-15T12:00:00Z",
    "recurring_pattern": "weekly",
    "created_at": "2026-02-08T10:00:00Z",
    "updated_at": "2026-02-08T10:00:00Z"
  },
  "user_id": "abc123",
  "timestamp": "2026-02-08T10:00:01Z"
}
```

### ReminderEvent (Published to `reminders` topic)

```json
{
  "task_id": 42,
  "title": "Buy groceries",
  "due_at": "2026-02-15T12:00:00Z",
  "remind_at": "2026-02-15T11:00:00Z",
  "user_id": "abc123"
}
```

### CloudEvents Wrapper (Applied by Dapr)

Dapr wraps published messages in CloudEvents format. Consuming services receive:

```json
{
  "id": "unique-event-id",
  "source": "backend",
  "type": "com.dapr.event.sent",
  "specversion": "1.0",
  "datacontenttype": "application/json",
  "data": {
    // The actual event payload (TaskEvent or ReminderEvent)
  }
}
```

Services should read `request.json()["data"]` to get the inner event payload.

## State Transitions

### Task Lifecycle with Events

```text
[Created] --task.created--> (task-events topic)
    |                            |
    v                            v
[Updated] --task.updated--> (task-events topic)
    |                            |
    v                            v
[Completed] --task.completed--> (task-events topic)
    |                                |
    |                                +--> Recurring Service checks pattern
    |                                      |
    |                                      +--> If recurring: creates new task
    |                                      |        (new task.created event)
    |                                      |
    |                                      +--> If not recurring: no action
    v
[Deleted] --task.deleted--> (task-events topic)
```

### Reminder Flow

```text
Task Created/Updated with due_date
    |
    v
Backend publishes to "reminders" topic
    |
    v
Notification Service receives reminder
    |
    +--> If remind_at <= now: log reminder immediately
    |
    +--> If remind_at > now: store and check periodically
    |
    +--> Before logging: check if task still pending
            |
            +--> If completed: skip
            +--> If pending: log "REMINDER: ..."
```

## SQLModel Updates (Backend)

```python
# In backend/models.py - add to Task model
parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
```

## Pydantic Event Schemas (Backend)

```python
# In backend/events/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TaskEventData(BaseModel):
    id: int
    user_id: str
    title: str
    description: str
    completed: bool
    priority: str
    tags: List[str]
    due_date: Optional[datetime]
    recurring_pattern: str
    created_at: datetime
    updated_at: datetime

class TaskEvent(BaseModel):
    event_type: str  # task.created, task.updated, task.completed, task.deleted
    task_id: int
    task_data: TaskEventData
    user_id: str
    timestamp: datetime

class ReminderEvent(BaseModel):
    task_id: int
    title: str
    due_at: datetime
    remind_at: datetime
    user_id: str
```
