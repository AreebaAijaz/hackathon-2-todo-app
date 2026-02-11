# Implementation Plan: Phase 5A - Advanced Task Features

**Branch**: `001-advanced-task-features` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-advanced-task-features/spec.md`

## Summary

Add priority levels, tags, due dates, recurring task patterns, full-text search, and advanced filtering/sorting to the existing task management app. Implementation extends the existing PostgreSQL schema with new columns (priority VARCHAR, tags TEXT[], due_date TIMESTAMPTZ, recurring_pattern VARCHAR, search_vector TSVECTOR), enhances the FastAPI REST endpoints with query parameter filtering, updates MCP tools and NL skills for chatbot integration, and adds frontend UI components (priority badges, tag pills, date picker, filter panel). Uses Alembic for database migration with zero data loss on existing tasks.

## Technical Context

**Language/Version**: Python 3.13 (backend), TypeScript/Next.js 15 (frontend)
**Primary Dependencies**: FastAPI, SQLModel, psycopg3, OpenAI, Alembic (new) | Next.js, React, Tailwind CSS
**Storage**: Neon PostgreSQL (cloud) with ARRAY, TSVECTOR, GIN indexes
**Testing**: pytest + httpx (backend), manual E2E (frontend)
**Target Platform**: Vercel (frontend production), Minikube/Docker (local K8s), Linux containers
**Project Type**: Web application (separate frontend + backend)
**Performance Goals**: <500ms CRUD, <1s search/filter, <3s chatbot response, <500ms autocomplete
**Constraints**: <500 tasks per user, no pagination needed, single-user tag scope
**Scale/Scope**: Hackathon project, single-developer, 2 deployment targets (Vercel + K8s)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Notes |
|------|--------|-------|
| Code Quality: type hints, docstrings, error handling | PASS | All new Python code will have type hints and docstrings |
| TypeScript strict mode | PASS | Frontend already in strict mode |
| RESTful API design | PASS | Extending existing REST endpoints with proper HTTP methods |
| Database: normalized schema, indexes | PASS | New GIN indexes for tags/search, btree for priority/due_date |
| No hardcoded values | PASS | All config via env vars |
| Spec requirements met | PASS | Spec is complete with 20 FRs, 10 SCs, no NEEDS CLARIFICATION |
| Test cases: min 3 per feature | PASS | Will cover happy path, edge case, error case for each feature area |
| AI Chatbot: NL understanding, context | PASS | Extending existing MCP tools + skills, OpenAI fallback |
| K8s: containerized, resource limits, health checks | PASS | Existing Helm chart; only code changes in containers |
| Security: input validation, SQL injection prevention | PASS | Pydantic validation, parameterized queries via SQLModel |

**Post-Phase 1 Re-check**: Constitution mentions "Tags stored as a relation (task_tags table)" but research (TD-1) chose TEXT[] array. Constitution should be updated to reflect this simplification. See [research.md](./research.md) TD-1.

## Project Structure

### Documentation (this feature)

```text
specs/001-advanced-task-features/
├── plan.md              # This file
├── research.md          # Phase 0: 10 technical decisions
├── data-model.md        # Phase 1: Updated Task entity, migration script
├── quickstart.md        # Phase 1: Implementation order guide
├── contracts/
│   └── api-contracts.md # Phase 1: Enhanced API + MCP tool contracts
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── models.py              # MODIFY: Add priority, tags, due_date, recurring_pattern, search_vector to Task
├── schemas.py             # MODIFY: Enhanced TaskCreate, TaskUpdate, TaskResponse + new BulkUpdate, FilterParams
├── database.py            # UNCHANGED
├── pyproject.toml         # MODIFY: Add alembic dependency
├── routes/
│   └── tasks.py           # MODIFY: Filter/sort/search params, bulk endpoint, tags endpoint
├── mcp_server/
│   ├── schemas.py         # MODIFY: Enhanced MCP input/output schemas
│   └── tools.py           # MODIFY: Pass new fields, enhanced tool definitions
├── skills/
│   ├── task_parser.py     # MODIFY: Extract priority, tags, due dates, recurring from NL
│   └── filter_mapper.py   # MODIFY: Map NL to priority, tags, overdue, search filters
├── agents/
│   └── orchestrator.py    # MODIFY: Format tool results with new fields
├── alembic/               # NEW: Migration configuration
│   ├── env.py
│   ├── versions/
│   │   ├── 001_baseline.py
│   │   └── 002_advanced_task_features.py
│   └── alembic.ini
└── tests/
    ├── test_tasks_api.py  # NEW/MODIFY: Enhanced endpoint tests
    └── test_migration.py  # NEW: Migration verification

frontend/
├── src/
│   ├── lib/
│   │   ├── types.ts       # MODIFY: Enhanced Task interface, filter types
│   │   └── api.ts         # MODIFY: Filter params, bulk update, tags endpoint
│   ├── components/
│   │   ├── TaskForm.tsx   # MODIFY: Priority, tags, date, recurring inputs
│   │   ├── TaskItem.tsx   # MODIFY: Priority badge, tag pills, due date, recurring icon
│   │   ├── TaskList.tsx   # MODIFY: Filter panel, enhanced state
│   │   ├── PriorityBadge.tsx  # NEW: Color-coded priority display
│   │   ├── TagPills.tsx       # NEW: Clickable tag pills
│   │   └── FilterPanel.tsx    # NEW: Multi-field filter controls
│   └── app/
│       └── tasks/
│           └── page.tsx   # MINOR: May need layout adjustments
└── tests/                 # Future: component tests
```

**Structure Decision**: Web application structure (Option 2). Both `backend/` and `frontend/` already exist as separate projects. All changes are modifications to existing files plus 3 new frontend components and Alembic migration infrastructure. No new projects or fundamental structural changes.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| TEXT[] array instead of join table (constitution says "relation") | Simpler queries, no joins, GIN indexed | Join table is over-engineered for <500 tasks, no tag metadata needed |
| Alembic introduction (new dependency) | Cannot ALTER TABLE with create_all() | Manual SQL is error-prone and not reversible |

## Implementation Phases

### Phase 1: Database Migration
- Initialize Alembic, create baseline + Phase 5A migration
- Add columns: priority, tags, due_date, recurring_pattern, search_vector
- Add indexes: GIN for tags/search, btree for priority/due_date
- Add search vector trigger function
- Backfill defaults for existing rows

### Phase 2: Backend API
- Update Task model and Pydantic schemas
- Add filter/sort/search query params to GET /api/tasks
- Add PATCH /api/tasks/bulk endpoint
- Add GET /api/tasks/tags endpoint
- Add is_overdue computed field

### Phase 3: MCP Tools & Skills
- Extend MCP tool schemas and definitions
- Enhance TaskParserSkill for priority, tags, due dates
- Enhance FilterMapperSkill for advanced filters
- Update orchestrator result formatting

### Phase 4: Frontend Types & API
- Update TypeScript interfaces
- Update API client with filter params, new endpoints

### Phase 5: Frontend UI
- PriorityBadge component
- TagPills component
- FilterPanel component
- Update TaskForm, TaskItem, TaskList

### Phase 6: Chatbot Testing
- Verify NL commands create tasks with new fields
- Verify NL queries filter correctly

### Phase 7: Testing & Deployment
- Backend API tests
- Migration verification
- Docker image rebuild
- Helm upgrade for K8s
- Verify Vercel deployment

## Follow-ups and Risks

- **Risk**: Alembic migration on production Neon DB could fail if schema differs from expected. **Mitigation**: Test on local DB first, migration is reversible.
- **Risk**: SQLModel doesn't natively support ARRAY or TSVECTOR columns. **Mitigation**: Use `sa_column` with raw SQLAlchemy types (documented in data-model.md).
- **Follow-up**: Update constitution.md to change "stored as a relation (task_tags table)" to "stored as TEXT[] array" after implementation.
