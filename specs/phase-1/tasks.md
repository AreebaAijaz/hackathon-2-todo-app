# Phase I Task Breakdown

**Reference**: [Plan](./plan.md) | [Specification](./spec.md)

---

## Phase 1: Setup (3 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 1.1 | Initialize UV project, install Rich | `pyproject.toml` created |
| 1.2 | Create folder structure | `src/`, `tests/`, `specs/` ready |
| 1.3 | Create Task dataclass in models.py | Task model defined |

**CHECKPOINT 1**: Project structure ready

---

## Phase 2: Storage (4 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2.1 | Build storage.py skeleton, in-memory list | Storage initialized |
| 2.2 | Implement add_task, get_all_tasks | Add/view working |
| 2.3 | Implement get_by_id, update_task, delete_task | Update/delete working |
| 2.4 | Implement toggle_complete | Mark complete working |

**CHECKPOINT 2**: All CRUD operations functional

---

## Phase 3: CLI (5 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 3.1 | Build main.py with menu loop | Menu displays |
| 3.2 | Implement Add Task flow | User can add tasks |
| 3.3 | Implement View Tasks with Rich table | Formatted output |
| 3.4 | Implement Update, Delete, Mark flows | All operations accessible |
| 3.5 | Add error handling and validation | Graceful errors |

**CHECKPOINT 3**: Full CLI working

---

## Phase 4: Testing (3 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 4.1 | Write unit tests for models.py | Model tests passing |
| 4.2 | Write unit tests for storage.py | Storage tests passing |
| 4.3 | Run coverage, achieve 80%+ | Coverage target met |

**CHECKPOINT 4**: Tests complete, 80%+ coverage

---

## Task Flow

```
Phase 1: Setup
  [1.1] → [1.2] → [1.3] → CHECKPOINT 1
                              ↓
Phase 2: Storage
  [2.1] → [2.2] → [2.3] → [2.4] → CHECKPOINT 2
                                      ↓
Phase 3: CLI
  [3.1] → [3.2] → [3.3] → [3.4] → [3.5] → CHECKPOINT 3
                                              ↓
Phase 4: Testing
  [4.1] → [4.2] → [4.3] → CHECKPOINT 4
```

---

## Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| 1 | 3 | Setup |
| 2 | 4 | Storage |
| 3 | 5 | CLI |
| 4 | 3 | Testing |
| **Total** | **15** | |
