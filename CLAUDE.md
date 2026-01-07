# Claude Code Instructions

## Project Overview

**Evolution of Todo** - A 5-phase hackathon project building a Todo application from console app to cloud-native Kubernetes deployment.

**Current Phase**: Phase I - In-Memory Python Console Todo App

---

## Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Constitution | `specs/constitution.md` | Global project standards |
| Phase I Spec | `specs/phase-1/spec.md` | Feature requirements |
| Phase I Plan | `specs/phase-1/plan.md` | Implementation approach |
| Phase I Tasks | `specs/phase-1/tasks.md` | Task breakdown |

---

## Development Standards

### Code Quality
- All Python code must have type hints
- All functions must have docstrings
- Use dataclasses for data models
- No hardcoded values - use constants or config

### Testing
- Minimum 80% code coverage
- Write tests for all CRUD operations
- Use pytest for testing

### Error Handling
- Catch and handle all expected exceptions
- Provide helpful error messages
- Never crash on user input errors

---

## Phase I Specifics

### Tech Stack
- Python 3.13+
- UV package manager
- Rich library for CLI formatting
- In-memory storage (no database)

### File Structure
```
src/
├── __init__.py
├── main.py      # Entry point
├── models.py    # Task dataclass
├── storage.py   # CRUD operations
└── cli.py       # Rich UI
tests/
├── __init__.py
├── test_models.py
└── test_storage.py
```

### Commands
```bash
# Run application
uv run python -m src.main

# Run tests
uv run pytest -v

# Check coverage
uv run pytest --cov=src --cov-report=term-missing
```

---

## Implementation Rules

1. **Read specs first** - Always check `specs/phase-1/spec.md` before implementing
2. **Follow the plan** - Implement in order defined in `specs/phase-1/plan.md`
3. **Track tasks** - Use `specs/phase-1/tasks.md` checkpoints
4. **Test as you go** - Write tests alongside implementation
5. **No manual coding** - Claude Code generates all code

---

## Validation Rules

| Field | Constraint |
|-------|------------|
| title | Required, 1-100 characters |
| description | Optional, max 500 characters |
| UUID | Valid format, must exist for update/delete/mark |

---

## Error Messages

| Scenario | Message |
|----------|---------|
| Empty title | "Title cannot be empty" |
| Title too long | "Title must be 100 characters or less" |
| Task not found | "Task with ID {uuid} not found" |
| Invalid menu | "Invalid option. Please enter 1-6." |
