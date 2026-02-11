# Phase 0 Research: Advanced Task Features

**Feature Branch**: `001-advanced-task-features`
**Created**: 2026-02-08
**Spec**: [spec.md](./spec.md)

## Technical Decisions

### TD-1: Tag Storage — PostgreSQL TEXT[] Array vs Join Table

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **TEXT[] column** (chosen) | Simple schema, fast reads, no joins needed, native PostgreSQL support | No tag metadata (color, description), harder to enforce global uniqueness |
| Join table (task_tags) | Normalized, supports tag metadata, easier global tag queries | Extra joins on every query, more complex migrations, over-engineered for this scale |

**Decision**: Use `TEXT[]` column on the `tasks` table.

**Rationale**: The spec defines tags as user-scoped strings with max 10 per task, max 30 chars each. At this scale (<500 tasks per user), array storage is simpler, faster, and avoids join overhead. PostgreSQL provides `@>`, `&&` operators and GIN indexes for array queries. The autocomplete endpoint can use `SELECT DISTINCT unnest(tags) FROM tasks WHERE user_id = $1`.

> Note: The constitution mentions "stored as a relation (task_tags table)" but this was written before technical research. Array storage better fits the actual constraints (no shared tags, no tag metadata, <500 tasks). The constitution should be updated to reflect this decision.

---

### TD-2: Priority Storage — String Enum vs Integer

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **String enum** (chosen) | Readable in DB, self-documenting, easy to extend | Slightly larger storage, need CHECK constraint |
| Integer (0-3) | Compact, natural sort order | Magic numbers in DB, need mapping layer |

**Decision**: Use `VARCHAR` with CHECK constraint (`low`, `medium`, `high`, `urgent`).

**Rationale**: Readability wins at this scale. String values are self-documenting in queries and API responses. PostgreSQL CHECK constraint enforces valid values. Default is `medium`. For sorting, use a CASE expression or a sort-order mapping in the application layer.

**Sort Mapping** (application layer):
```python
PRIORITY_ORDER = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
```

---

### TD-3: Full-Text Search — PostgreSQL tsvector

**Decision**: Use PostgreSQL `tsvector` generated column with GIN index.

**Implementation**:
- Add `search_vector tsvector` column to tasks table
- Generated from `to_tsvector('english', title || ' ' || coalesce(description, ''))`
- Create GIN index on `search_vector`
- Query with `plainto_tsquery('english', $query)` and `ts_rank()` for relevance

**Why not external search (Elasticsearch, Meilisearch)?**:
- Overkill for <500 tasks per user
- Adds infrastructure dependency
- PostgreSQL tsvector is built-in, no extra service
- Meets the <1 second performance requirement easily

**Why not LIKE/ILIKE?**:
- No relevance ranking
- Poor performance on large text
- No stemming (search "running" won't match "run")

---

### TD-4: Database Migration Strategy — Alembic

**Current State**: The project uses `SQLModel.metadata.create_all()` for table creation. No migration tool is configured.

**Decision**: Introduce Alembic for this migration and all future schema changes.

**Rationale**: Adding 5+ columns to an existing production table with data requires a proper migration tool. `create_all()` only creates missing tables — it cannot alter existing ones. Alembic is the standard SQLAlchemy migration tool and works seamlessly with SQLModel.

**Migration Plan**:
1. Initialize Alembic in `backend/`
2. Create initial migration capturing current schema (baseline)
3. Create Phase 5A migration adding new columns with defaults
4. Migration must be idempotent and reversible

**Default Values for Existing Tasks**:
| Field | Default |
|-------|---------|
| priority | `'medium'` |
| tags | `'{}'` (empty array) |
| due_date | `NULL` |
| recurring_pattern | `'none'` |
| search_vector | Auto-generated from title + description |

---

### TD-5: Due Date Storage — `TIMESTAMPTZ`

**Decision**: Use `TIMESTAMP WITH TIME ZONE` (TIMESTAMPTZ) column.

**Rationale**: Store in UTC, display in user's local timezone (browser handles conversion). TIMESTAMPTZ ensures correct comparison regardless of server timezone. Nullable — `NULL` means no deadline.

**Overdue Detection**: `due_date < NOW() AND completed = FALSE`

---

### TD-6: Recurring Pattern — String Enum

**Decision**: Use `VARCHAR` with CHECK constraint (`none`, `daily`, `weekly`, `monthly`). Default `none`.

**Rationale**: Phase 5A only stores the pattern (no auto-creation). Simple string storage is sufficient. The CHECK constraint ensures only valid values. A separate `recurring_enabled` boolean is unnecessary — `none` serves the same purpose as `enabled=false`.

> Simplification from spec: The spec mentions `recurring_enabled` boolean but this is redundant with `recurring_pattern = 'none'`. Using only the pattern field reduces schema complexity.

---

### TD-7: API Query Parameters for Filtering/Sorting

**Decision**: Use query parameters on `GET /api/tasks` rather than a separate search endpoint.

**Enhanced GET /api/tasks parameters**:
```
GET /api/tasks?
  status=pending|completed|all
  &priority=low,medium,high,urgent    (comma-separated, OR within)
  &tags=work,personal                 (comma-separated, AND within)
  &due_before=2026-02-28T23:59:59Z
  &due_after=2026-02-01T00:00:00Z
  &overdue=true|false
  &search=keyword
  &sort_by=created_at|due_date|priority|title
  &sort_dir=asc|desc
```

**Rationale**: Extending the existing endpoint maintains backward compatibility. Clients that don't send new parameters get the current behavior (all tasks, sorted by created_at desc).

---

### TD-8: Bulk Operations Endpoint

**Decision**: `PATCH /api/tasks/bulk` with JSON body specifying task IDs and operations.

```json
{
  "task_ids": [1, 2, 3],
  "operations": {
    "priority": "high",
    "add_tags": ["work"],
    "due_date": "2026-02-15T17:00:00Z"
  }
}
```

**Rationale**: Single endpoint for all bulk operations. Separate from individual PUT to maintain clear semantics. Uses PATCH because it's a partial update of multiple resources.

---

### TD-9: Frontend State Management — URL Query Params + React State

**Decision**: Filter state lives in URL query parameters (shareable, bookmarkable) backed by React useState for immediate UI responsiveness.

**Rationale**: URL-based filter state means users can share filtered views. React state provides instant feedback while API calls complete. The TaskList component already manages filter state for status (all/pending/completed) — this extends the same pattern.

---

### TD-10: Chatbot Integration — Enhanced MCP Tools + Skills

**Decision**: Extend existing MCP tools and skills rather than creating new ones.

**Changes**:
- `add_task` tool: Add optional `priority`, `tags`, `due_date`, `recurring_pattern` parameters
- `list_tasks` tool: Add filter parameters matching API query params
- `update_task` tool: Add `priority`, `tags`, `due_date`, `recurring_pattern` fields
- `TaskParserSkill`: Extract priority, tags, due dates from NL (e.g., "high priority", "tagged work", "due Friday")
- `FilterMapperSkill`: Map NL to enhanced filter params (e.g., "urgent work tasks" → priority=urgent, tags=work)

**Rationale**: Extending existing tools maintains the established architecture. The orchestrator routing logic doesn't change — only the tool capabilities expand.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Alembic migration on production Neon DB | Data loss | Test migration on local DB first; reversible migration |
| tsvector not supported by SQLModel natively | Build failure | Use `sa_column` with raw SQLAlchemy Column definition |
| Array column not natively supported by SQLModel | Type errors | Use `sa_column` with `ARRAY(Text)` from SQLAlchemy |
| Frontend bundle size increase from date picker | Slow load | Use native HTML date input or lightweight library |
| Chatbot NL parsing accuracy for new features | Poor UX | Fallback to OpenAI function calling for ambiguous inputs |

## Dependencies to Add

**Backend** (`pyproject.toml`):
- `alembic>=1.15.0` — Database migrations

**Frontend** (`package.json`):
- No new dependencies needed. Use native HTML `<input type="date">` for date picker.
