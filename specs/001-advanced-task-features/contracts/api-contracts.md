# API Contracts: Advanced Task Features

**Feature Branch**: `001-advanced-task-features`
**Created**: 2026-02-08
**Data Model**: [data-model.md](../data-model.md)

## Base URL

```
{API_URL}/api
```

## Authentication

All endpoints require `Authorization: Bearer <session_token>` header. User ID extracted from session via `get_current_user` dependency.

---

## Enhanced Endpoints

### GET /api/tasks — List Tasks (Enhanced)

**Current**: Returns all user tasks sorted by `created_at desc`.
**Enhanced**: Supports filtering, sorting, and full-text search via query parameters.

**Query Parameters**:

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `status` | string | `all` | Filter: `all`, `pending`, `completed` |
| `priority` | string | — | Filter by priority. Comma-separated: `high,urgent` |
| `tags` | string | — | Filter by tags. Comma-separated (AND logic): `work,urgent` |
| `due_before` | ISO 8601 | — | Tasks with due_date before this datetime |
| `due_after` | ISO 8601 | — | Tasks with due_date after this datetime |
| `overdue` | boolean | — | `true` = only overdue tasks (due_date < now AND !completed) |
| `search` | string | — | Full-text search query (max 200 chars) |
| `sort_by` | string | `created_at` | Sort field: `created_at`, `due_date`, `priority`, `title` |
| `sort_dir` | string | `desc` | Sort direction: `asc`, `desc` |

**Response**: `200 OK`

```json
[
  {
    "id": 1,
    "user_id": "abc123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-08T10:00:00Z",
    "updated_at": "2026-02-08T10:00:00Z",
    "priority": "high",
    "tags": ["shopping", "personal"],
    "due_date": "2026-02-10T17:00:00Z",
    "recurring_pattern": "weekly",
    "is_overdue": false
  }
]
```

**Backward Compatibility**: No query params = current behavior (all tasks, created_at desc).

**Errors**:
- `400 Bad Request`: Invalid filter values (e.g., `priority=invalid`)
- `401 Unauthorized`: Missing/invalid session token

---

### POST /api/tasks — Create Task (Enhanced)

**Current**: Accepts `title` and `description`.
**Enhanced**: Accepts new optional fields.

**Request Body**:

```json
{
  "title": "Call dentist",
  "description": "Schedule annual checkup",
  "priority": "high",
  "tags": ["health", "personal"],
  "due_date": "2026-02-15T09:00:00Z",
  "recurring_pattern": "none"
}
```

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `title` | string (1-200) | Yes | — |
| `description` | string (0-500) | No | `""` |
| `priority` | enum | No | `"medium"` |
| `tags` | string[] (max 10) | No | `[]` |
| `due_date` | ISO 8601 or null | No | `null` |
| `recurring_pattern` | enum | No | `"none"` |

**Response**: `201 Created` — Full TaskResponse object.

**Backward Compatibility**: Omitting new fields = defaults applied. Existing clients work unchanged.

**Errors**:
- `400 Bad Request`: Invalid priority, too many tags, invalid tag format
- `401 Unauthorized`: Missing/invalid session token
- `422 Unprocessable Entity`: Validation failure

---

### PUT /api/tasks/{task_id} — Update Task (Enhanced)

**Current**: Accepts `title` and `description`.
**Enhanced**: Accepts new optional fields.

**Request Body**:

```json
{
  "title": "Call dentist ASAP",
  "priority": "urgent",
  "tags": ["health"],
  "due_date": "2026-02-12T09:00:00Z"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string (1-200) | No | New title |
| `description` | string (0-500) | No | New description |
| `priority` | enum | No | New priority |
| `tags` | string[] | No | Replaces all tags |
| `due_date` | ISO 8601 or null | No | New due date. Send `null` to clear. |
| `recurring_pattern` | enum | No | New recurring pattern |

**Response**: `200 OK` — Full TaskResponse object.

**Errors**:
- `400 Bad Request`: Invalid field values
- `404 Not Found`: Task not found or not owned
- `401 Unauthorized`: Missing/invalid session token

---

### DELETE /api/tasks/{task_id} — Delete Task (Unchanged)

No changes required. Existing contract preserved.

---

### PATCH /api/tasks/{task_id}/complete — Toggle Complete (Unchanged)

No changes required. Existing contract preserved.

---

## New Endpoints

### PATCH /api/tasks/bulk — Bulk Update Tasks

**Description**: Apply operations to multiple tasks at once.

**Request Body**:

```json
{
  "task_ids": [1, 2, 3],
  "operations": {
    "priority": "high",
    "add_tags": ["work"],
    "remove_tags": ["personal"],
    "due_date": "2026-02-15T17:00:00Z",
    "recurring_pattern": "weekly"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task_ids` | int[] (1-50) | Yes | Task IDs to update |
| `operations.priority` | enum | No | Set priority |
| `operations.add_tags` | string[] | No | Tags to add |
| `operations.remove_tags` | string[] | No | Tags to remove |
| `operations.due_date` | ISO 8601 or null | No | Set due date |
| `operations.recurring_pattern` | enum | No | Set recurring pattern |

**Response**: `200 OK`

```json
{
  "updated_count": 3,
  "task_ids": [1, 2, 3]
}
```

**Errors**:
- `400 Bad Request`: Empty task_ids, invalid operations
- `401 Unauthorized`: Missing/invalid session token
- `404 Not Found`: One or more tasks not found or not owned (none updated)

---

### GET /api/tasks/tags — List User Tags

**Description**: Get all unique tags used by the authenticated user, for autocomplete.

**Response**: `200 OK`

```json
{
  "tags": ["health", "personal", "shopping", "work"],
  "count": 4
}
```

**Notes**: Tags returned in alphabetical order. Derived from `SELECT DISTINCT unnest(tags)`.

**Errors**:
- `401 Unauthorized`: Missing/invalid session token

---

## MCP Tool Contracts (Enhanced)

### add_task (Enhanced)

**OpenAI Function Parameters**:

```json
{
  "type": "object",
  "properties": {
    "title": { "type": "string", "description": "The task title/name" },
    "description": { "type": "string", "description": "Optional task description" },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "urgent"],
      "description": "Task priority level. Default: medium"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Tags to categorize the task (e.g., ['work', 'urgent'])"
    },
    "due_date": {
      "type": "string",
      "description": "Due date in ISO 8601 format (e.g., '2026-02-15T17:00:00Z')"
    },
    "recurring_pattern": {
      "type": "string",
      "enum": ["none", "daily", "weekly", "monthly"],
      "description": "Recurring schedule. Default: none"
    }
  },
  "required": ["title"]
}
```

**Output**: `AddTaskOutput` (unchanged structure, task created with new fields).

---

### list_tasks (Enhanced)

**OpenAI Function Parameters**:

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["all", "pending", "completed"],
      "description": "Filter by completion status. Default: all"
    },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "urgent"],
      "description": "Filter by priority level"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Filter by tags (tasks must have ALL specified tags)"
    },
    "overdue": {
      "type": "boolean",
      "description": "If true, only return overdue tasks"
    },
    "search": {
      "type": "string",
      "description": "Search query to find tasks by title or description"
    },
    "sort_by": {
      "type": "string",
      "enum": ["created_at", "due_date", "priority", "title"],
      "description": "Field to sort by. Default: created_at"
    }
  },
  "required": []
}
```

**Output**: `ListTasksOutput` — TaskItem updated to include priority, tags, due_date, recurring_pattern, is_overdue.

---

### update_task (Enhanced)

**OpenAI Function Parameters**:

```json
{
  "type": "object",
  "properties": {
    "task_id": { "type": "integer", "description": "The task ID to update" },
    "title": { "type": "string", "description": "New title (optional)" },
    "description": { "type": "string", "description": "New description (optional)" },
    "completed": { "type": "boolean", "description": "New completion status (optional)" },
    "priority": {
      "type": "string",
      "enum": ["low", "medium", "high", "urgent"],
      "description": "New priority (optional)"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "New tags list (replaces existing)"
    },
    "due_date": {
      "type": "string",
      "description": "New due date in ISO 8601 (optional, null to clear)"
    },
    "recurring_pattern": {
      "type": "string",
      "enum": ["none", "daily", "weekly", "monthly"],
      "description": "New recurring pattern (optional)"
    }
  },
  "required": ["task_id"]
}
```

**Output**: `UpdateTaskOutput` — changes list includes new field names.

---

### complete_task / delete_task (Unchanged)

No changes to these MCP tools.

---

## Enhanced Skill Contracts

### TaskParserSkill (Enhanced)

**Input**: Natural language string
**Output**: `ParsedTask` (enhanced)

```python
@dataclass
class ParsedTask:
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None       # New
    tags: Optional[List[str]] = None     # New
    due_date: Optional[str] = None       # New (ISO 8601)
    recurring_pattern: Optional[str] = None  # New
    has_title: bool = True
```

**NL Patterns**:
- Priority: "high priority", "urgent", "low pri"
- Tags: "tagged work", "tag: personal", "#shopping"
- Due date: "due Friday", "due next Monday", "by Feb 15"
- Recurring: "every day", "weekly", "every month", "recurring daily"

---

### FilterMapperSkill (Enhanced)

**Input**: Natural language string
**Output**: `FilterParams` (enhanced)

```python
@dataclass
class FilterParams:
    status: Literal["all", "pending", "completed"] = "all"
    priority: Optional[List[str]] = None       # New
    tags: Optional[List[str]] = None           # New
    overdue: Optional[bool] = None             # New
    search: Optional[str] = None               # New
    sort_by: Optional[str] = None              # New
    confidence: float = 1.0
```

**NL Patterns**:
- "show urgent tasks" → priority=["urgent"]
- "my work tasks" → tags=["work"]
- "what's overdue" → overdue=True
- "find grocery" → search="grocery"
- "tasks due this week" → due_after=monday, due_before=sunday
