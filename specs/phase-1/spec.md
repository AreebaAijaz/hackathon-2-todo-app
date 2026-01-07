# Phase I Specification: In-Memory Python Console Todo App

**Reference**: [Project Constitution](../constitution.md)

---

## Overview

| Attribute | Value |
|-----------|-------|
| Phase | I |
| Type | Console Application |
| Storage | In-Memory (no persistence) |
| Language | Python 3.13+ |
| Package Manager | UV |

---

## Intent

Build a command-line todo application with in-memory storage that implements all 5 basic CRUD operations. This phase establishes the foundational architecture for subsequent phases.

---

## Features

### Feature 1: Add Task

**Intent**: Allow users to create new tasks with required title and optional description.

**Behavior**:
- Prompt user for title (required)
- Prompt user for description (optional, press Enter to skip)
- Auto-generate UUID for task ID
- Set default status to incomplete (`completed=False`)
- Set `created_at` to current datetime
- Display confirmation with task ID

**Acceptance Criteria**:
- [ ] Task created with valid UUID
- [ ] Title stored correctly (1-100 characters)
- [ ] Description stored correctly (0-500 characters)
- [ ] Default status is incomplete
- [ ] Confirmation message displays task ID

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | title="Buy groceries", desc="" | Task created with UUID |
| 2 | Happy Path | title="Meeting", desc="Team sync at 3pm" | Task created with title and description |
| 3 | Edge Case | title="A" (1 char) | Task created successfully |
| 4 | Error | title="" (empty) | "Title cannot be empty" |
| 5 | Error | title=101 chars | "Title must be 100 characters or less" |

---

### Feature 2: View All Tasks

**Intent**: Display all tasks in a formatted table.

**Behavior**:
- Retrieve all tasks from storage
- Display in Rich table format
- Show columns: ID (truncated), Title, Status, Description (preview)
- Handle empty list gracefully

**Acceptance Criteria**:
- [ ] All tasks displayed in table format
- [ ] UUID displayed (first 8 characters + "...")
- [ ] Status shows "Complete" or "Incomplete"
- [ ] Description truncated to 30 characters with "..."
- [ ] Empty state: "No tasks found. Add a task to get started!"

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | 3 tasks exist | Table with 3 rows |
| 2 | Edge Case | 0 tasks | "No tasks found" message |
| 3 | Edge Case | Task with 500 char description | Description truncated to 30 chars |

---

### Feature 3: Update Task

**Intent**: Allow users to modify title and/or description of existing tasks.

**Behavior**:
- Prompt for task UUID
- Validate task exists
- Show current values
- Prompt for new title (press Enter to keep current)
- Prompt for new description (press Enter to keep current)
- Display confirmation

**Acceptance Criteria**:
- [ ] Task found by UUID
- [ ] Current values displayed before edit
- [ ] Title updated if new value provided
- [ ] Description updated if new value provided
- [ ] Keeping current value works (Enter to skip)
- [ ] Error if task not found

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | Valid UUID, new title | Title updated, confirmation shown |
| 2 | Happy Path | Valid UUID, new description only | Description updated, title unchanged |
| 3 | Edge Case | Valid UUID, Enter for both | No changes, confirmation shown |
| 4 | Error | Invalid UUID format | "Invalid UUID format" |
| 5 | Error | Non-existent UUID | "Task with ID {uuid} not found" |

---

### Feature 4: Delete Task

**Intent**: Allow users to remove tasks with confirmation.

**Behavior**:
- Prompt for task UUID
- Validate task exists
- Show task details
- Prompt for confirmation (y/n)
- Delete on confirmation
- Display success message

**Acceptance Criteria**:
- [ ] Task found by UUID
- [ ] Task details shown before deletion
- [ ] Confirmation required (y/n)
- [ ] Task removed from storage on "y"
- [ ] Cancellation message on "n"
- [ ] Error if task not found

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | Valid UUID, confirm "y" | Task deleted, confirmation |
| 2 | Happy Path | Valid UUID, confirm "n" | Deletion cancelled |
| 3 | Error | Non-existent UUID | "Task with ID {uuid} not found" |
| 4 | Edge Case | Confirm with "Y" (uppercase) | Task deleted (case-insensitive) |

---

### Feature 5: Mark Complete/Incomplete

**Intent**: Toggle task completion status.

**Behavior**:
- Prompt for task UUID
- Validate task exists
- Toggle `completed` status
- Display new status

**Acceptance Criteria**:
- [ ] Task found by UUID
- [ ] Status toggled (True→False, False→True)
- [ ] Confirmation shows new status
- [ ] Error if task not found

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | Incomplete task UUID | Status changed to Complete |
| 2 | Happy Path | Complete task UUID | Status changed to Incomplete |
| 3 | Error | Non-existent UUID | "Task with ID {uuid} not found" |

---

## Data Model

```python
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

@dataclass
class Task:
    """Represents a todo task."""
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

---

## Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| title | Required, non-empty | "Title cannot be empty" |
| title | Max 100 characters | "Title must be 100 characters or less" |
| description | Max 500 characters | "Description must be 500 characters or less" |
| UUID | Valid format | "Invalid UUID format" |
| UUID | Must exist (for update/delete/mark) | "Task with ID {uuid} not found" |

---

## CLI Interface

```
===== Todo App Menu =====
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Complete/Incomplete
6. Exit

Enter choice: _
```

**Navigation**:
- Invalid choice: "Invalid option. Please enter 1-6."
- After each operation: return to menu
- Exit: "Goodbye!" and terminate
- Ctrl+C: "Goodbye!" and terminate gracefully

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Invalid menu choice | Display error, show menu again |
| Task not found | Display specific error with UUID |
| Empty title | Display validation error |
| Ctrl+C interrupt | Catch KeyboardInterrupt, exit gracefully |
| Unexpected error | Display generic error, continue to menu |

---

## Non-Goals

- No database or file persistence
- No web interface
- No user authentication
- No task priorities or categories
- No due dates
- No search/filter functionality

---

## Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| rich | Terminal formatting, tables, colors | Latest |

---

## Success Criteria

- [ ] All 5 features functional and tested
- [ ] CLI is intuitive with clear prompts
- [ ] Error messages are helpful and specific
- [ ] Code has type hints and docstrings
- [ ] Tests achieve minimum 80% coverage
- [ ] README has setup and usage instructions
- [ ] Works on Python 3.13+ with UV
