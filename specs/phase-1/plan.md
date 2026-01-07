# Phase I Implementation Plan

**Reference**: [Specification](./spec.md) | [Constitution](../constitution.md)

---

## Architecture

```
CLI (main.py) → Storage Layer (storage.py) → Data Models (models.py)
                        ↓
              Rich library for formatted output
```

---

## Implementation Phases

### Phase 1: Project Setup & Data Models

- [ ] Initialize UV project (`uv init`, `pyproject.toml`)
- [ ] Install dependencies (Rich)
- [ ] Create Task dataclass in `models.py`
- [ ] Create project folder structure
- [ ] Set up `.gitignore`

### Phase 2: Storage Layer

- [ ] Build `storage.py` with in-memory list
- [ ] Implement CRUD functions:
  - `add_task(title, description) → Task`
  - `get_all_tasks() → List[Task]`
  - `get_task_by_id(uuid) → Task | None`
  - `update_task(uuid, title, description) → Task`
  - `delete_task(uuid) → bool`
  - `toggle_complete(uuid) → Task`
- [ ] Add validation logic

### Phase 3: CLI Interface

- [ ] Build `main.py` with menu loop
- [ ] Build `cli.py` with Rich formatting
- [ ] Implement user prompts for each operation
- [ ] Format output tables with Rich
- [ ] Add error handling and input validation

### Phase 4: Testing

- [ ] Write unit tests for `storage.py`
- [ ] Write tests for `models.py`
- [ ] Test all CRUD operations
- [ ] Achieve 80%+ code coverage

---

## Execution Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Storage)
    ↓
Phase 3 (CLI)
    ↓
Phase 4 (Testing)
```

---

## Commands Reference

```bash
# Setup
uv init
uv add rich
uv add --dev pytest pytest-cov

# Run application
uv run python -m src.main

# Run tests
uv run pytest -v
uv run pytest --cov=src --cov-report=term-missing
```
