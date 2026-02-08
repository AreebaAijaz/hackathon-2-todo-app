# Tasks: Phase 5A - Advanced Task Features

**Input**: Design documents from `/specs/001-advanced-task-features/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-contracts.md, quickstart.md

**Tests**: Not explicitly requested in spec — test tasks included only at integration checkpoints.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US7 from spec.md)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` (Python 3.13, FastAPI, SQLModel)
- **Frontend**: `frontend/src/` (TypeScript, Next.js 15, React, Tailwind CSS)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add Alembic dependency and update constitution for Phase 5A

- [x] T001 Update constitution tag storage description from "relation (task_tags table)" to "TEXT[] array column" in specs/constitution.md per research decision TD-1
- [x] T002 Add `alembic>=1.15.0` dependency to backend/pyproject.toml and run `uv sync`
- [x] T003 Initialize Alembic in backend/ directory: run `alembic init alembic`, configure backend/alembic/env.py to use SQLModel metadata and DATABASE_URL from environment, set `sqlalchemy.url` in backend/alembic.ini

**Checkpoint**: Alembic configured, `alembic current` runs without error

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database migration and shared model/schema/type updates that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Alembic migration `002_advanced_task_features` in backend/alembic/versions/ that adds 5 columns (priority VARCHAR(10) DEFAULT 'medium', tags TEXT[] DEFAULT '{}', due_date TIMESTAMPTZ NULL, recurring_pattern VARCHAR(10) DEFAULT 'none', search_vector TSVECTOR NULL), CHECK constraints (ck_tasks_priority, ck_tasks_recurring), 4 indexes (ix_tasks_priority btree, ix_tasks_due_date btree, ix_tasks_tags GIN, ix_tasks_search GIN), search_vector trigger function + trigger, and backfills search_vector for existing rows. Include reversible downgrade. Reference data-model.md migration script.
- [x] T005 Run migration against Neon database: `alembic upgrade head`. Verify with `\d tasks` showing new columns, indexes, trigger.
- [x] T006 Update Task SQLModel in backend/models.py: add `priority: str = Field(default="medium", index=True)`, `tags: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(Text), server_default=text("'{}'::text[]")))`, `due_date: Optional[datetime] = Field(default=None, index=True)`, `recurring_pattern: str = Field(default="none")`, `search_vector` with `sa_column=Column(TSVECTOR)`. Import ARRAY, Text, TSVECTOR from sqlalchemy.
- [x] T007 [P] Update Pydantic schemas in backend/schemas.py: enhance TaskCreate with priority, tags (List[str] with max 10, validator for tag format), due_date (Optional[datetime]), recurring_pattern. Enhance TaskUpdate with same optional fields. Enhance TaskResponse with priority, tags, due_date, recurring_pattern, is_overdue (computed property: `due_date < now and not completed`). Add BulkOperations, BulkUpdateRequest, BulkUpdateResponse, TaskFilterParams per data-model.md. Add tag validation: max 30 chars, alphanumeric/hyphens/underscores only.
- [x] T008 [P] Update frontend TypeScript types in frontend/src/lib/types.ts: enhance Task interface with `priority: "low" | "medium" | "high" | "urgent"`, `tags: string[]`, `due_date: string | null`, `recurring_pattern: "none" | "daily" | "weekly" | "monthly"`, `is_overdue: boolean`. Enhance CreateTaskInput and UpdateTaskInput with new optional fields. Add TaskFilters and BulkUpdateRequest interfaces per data-model.md TypeScript section.
- [x] T009 [P] Update API client in frontend/src/lib/api.ts: modify `getTasks()` to accept optional TaskFilters parameter and build query string from it. Add `getTags(): Promise<{tags: string[], count: number}>` method hitting GET /api/tasks/tags. Add `bulkUpdate(data: BulkUpdateRequest): Promise<{updated_count: number, task_ids: number[]}>` method hitting PATCH /api/tasks/bulk. Update `createTask()` and `updateTask()` to pass new fields.

**Checkpoint**: Migration complete, models updated, schemas compiled, frontend types aligned. Existing API still works with no regressions.

---

## Phase 3: User Story 1 - Prioritize Tasks (Priority: P1) MVP

**Goal**: Users can assign priority levels to tasks, see color-coded badges, and sort by priority.

**Independent Test**: Create tasks with different priorities → verify badge colors display → sort by priority descending → urgent appears first.

**Acceptance**: FR-001, FR-002, FR-010 (priority sort), SC-001, SC-005

### Implementation

- [x] T010 [US1] Implement priority filtering and sorting in GET /api/tasks in backend/routes/tasks.py: add `priority: Optional[str] = Query(None)` param that accepts comma-separated values, filter with `Task.priority.in_(priorities)`. Add `sort_by: str = Query("created_at")` and `sort_dir: str = Query("desc")` params. For priority sort, use CASE expression mapping urgent=0, high=1, medium=2, low=3. Handle null due_dates in due_date sort (NULLS LAST).
- [x] T011 [US1] Update POST /api/tasks and PUT /api/tasks/{id} in backend/routes/tasks.py to accept and persist priority field from enhanced TaskCreate/TaskUpdate schemas. Set `task.priority = task_data.priority` on create, conditionally update on PUT.
- [x] T012 [P] [US1] Create PriorityBadge component in frontend/src/components/PriorityBadge.tsx: accepts `priority: "low" | "medium" | "high" | "urgent"` prop. Renders colored badge: gray/bg-gray-100 for low, yellow/bg-yellow-100 for medium, orange/bg-orange-100 for high, red/bg-red-100 for urgent. Display priority text capitalized. Small pill-shaped badge.
- [x] T013 [US1] Update TaskItem in frontend/src/components/TaskItem.tsx: import and render PriorityBadge next to task title. Show priority badge in the metadata row alongside the date.
- [x] T014 [US1] Update TaskForm in frontend/src/components/TaskForm.tsx: add priority selector dropdown (low/medium/high/urgent) with medium as default. Pass priority to createTask API call. Use styled `<select>` matching existing input styles.
- [x] T015 [US1] Update TaskList in frontend/src/components/TaskList.tsx: add sort_by and sort_dir to filter state. Add sort controls (dropdown for field, toggle for direction). Pass sort params to getTasks() API call.

**Checkpoint**: Tasks have priority badges, can be created with priority, sorted by priority. Editing priority persists.

---

## Phase 4: User Story 2 - Tag and Organize Tasks (Priority: P1)

**Goal**: Users can assign tags, see tag pills, click to filter, and get autocomplete suggestions.

**Independent Test**: Create tasks with tags → tag pills display → click tag pill → list filters to matching tasks → type in tag input → autocomplete appears.

**Acceptance**: FR-003, FR-004, FR-005, FR-015, SC-009

### Implementation

- [x] T016 [US2] Implement tag filtering in GET /api/tasks in backend/routes/tasks.py: add `tags: Optional[str] = Query(None)` param, parse comma-separated values, filter with `Task.tags.contains(tag_list)` using PostgreSQL `@>` operator for AND logic.
- [x] T017 [US2] Add GET /api/tasks/tags endpoint in backend/routes/tasks.py: query `SELECT DISTINCT unnest(tags) as tag FROM tasks WHERE user_id = :uid ORDER BY tag`. Return `{"tags": [...], "count": N}`. Uses raw SQL via `session.exec(text(...))`.
- [x] T018 [US2] Update POST /api/tasks and PUT /api/tasks/{id} in backend/routes/tasks.py to accept and persist tags field. On create, set `task.tags = task_data.tags`. On update, replace tags if provided.
- [x] T019 [P] [US2] Create TagPills component in frontend/src/components/TagPills.tsx: accepts `tags: string[]` and `onTagClick?: (tag: string) => void` props. Renders each tag as a clickable pill with bg-blue-50 text-blue-700 rounded-full styling. Truncate display if >5 tags with "+N more" indicator.
- [x] T020 [US2] Update TaskItem in frontend/src/components/TaskItem.tsx: import and render TagPills below task description. Wire onTagClick to propagate tag filter up to TaskList.
- [x] T021 [US2] Update TaskForm in frontend/src/components/TaskForm.tsx: add tag input field with comma-separated entry. Show existing tags as removable pills. Fetch user tags from GET /api/tasks/tags for autocomplete dropdown. Enforce max 10 tags, max 30 chars each, alphanumeric/hyphens/underscores validation with error message.
- [x] T022 [US2] Update TaskList in frontend/src/components/TaskList.tsx: add `tags` to filter state. When user clicks a tag pill on any TaskItem, update filter state to include that tag and re-fetch filtered results.

**Checkpoint**: Tags display as pills, clicking filters by tag, autocomplete works, validation enforced.

---

## Phase 5: User Story 3 - Due Dates with Overdue Highlighting (Priority: P1)

**Goal**: Users can set due dates, see overdue highlighting, filter by date range and overdue status.

**Independent Test**: Create task with past due date → overdue indicator shows (red) → create task with future date → normal styling → filter overdue → only past-due incomplete tasks show.

**Acceptance**: FR-006, FR-007, FR-009 (date range, overdue), FR-011, SC-004

### Implementation

- [x] T023 [US3] Implement due date filtering in GET /api/tasks in backend/routes/tasks.py: add `due_before: Optional[datetime] = Query(None)`, `due_after: Optional[datetime] = Query(None)`, `overdue: Optional[bool] = Query(None)` params. Filter overdue with `Task.due_date < func.now(), Task.completed == False`. Date range uses `Task.due_date.between(due_after, due_before)`.
- [x] T024 [US3] Update POST /api/tasks and PUT /api/tasks/{id} in backend/routes/tasks.py to accept and persist due_date field. Allow setting to null to clear deadline.
- [x] T025 [P] [US3] Create DueDateDisplay component in frontend/src/components/DueDateDisplay.tsx: accepts `due_date: string | null` and `completed: boolean` props. Computes is_overdue locally (due_date < now && !completed). Renders: no date = nothing, future date = gray calendar icon + formatted date, overdue = red calendar icon + "Overdue" + date in red text. Format dates as relative ("Tomorrow", "Feb 15") using existing formatDate pattern from TaskItem.
- [x] T026 [US3] Update TaskItem in frontend/src/components/TaskItem.tsx: import and render DueDateDisplay in the metadata row. Add overdue border styling: if task.is_overdue, add `border-l-[var(--error)]` class override.
- [x] T027 [US3] Update TaskForm in frontend/src/components/TaskForm.tsx: add due date input using native `<input type="datetime-local">` matching existing input styles. Pass due_date as ISO 8601 string to createTask API call. Allow clearing.
- [x] T028 [US3] Update TaskList in frontend/src/components/TaskList.tsx: add overdue toggle button to filter controls. Add due_before/due_after to filter state. Wire overdue toggle to re-fetch with `overdue=true` param.

**Checkpoint**: Due dates display with overdue highlighting, date picker works in form, overdue filter works.

---

## Phase 6: User Story 4 - Search Tasks (Priority: P2)

**Goal**: Users can search tasks by keywords with relevance-ranked results.

**Independent Test**: Create tasks with varied titles/descriptions → search "shop" → tasks containing "shop" appear → search nonsense → empty state "No tasks match your search" shown.

**Acceptance**: FR-008, FR-020 (search empty state), SC-003, SC-010

### Implementation

- [x] T029 [US4] Implement full-text search in GET /api/tasks in backend/routes/tasks.py: add `search: Optional[str] = Query(None, max_length=200)` param. When provided, filter with `Task.search_vector.match(plainto_tsquery('english', search))` and order by `ts_rank(Task.search_vector, plainto_tsquery(...))` descending. Combine with other filters using AND.
- [x] T030 [P] [US4] Create SearchBar component (integrated inline in TaskList.tsx) in frontend/src/components/SearchBar.tsx: accepts `value: string`, `onChange: (query: string) => void`, `onClear: () => void` props. Renders search icon + text input with debounce (300ms) + clear button. Styled with existing input classes, magnifying glass icon.
- [x] T031 [US4] Update TaskList in frontend/src/components/TaskList.tsx: add search string to filter state. Render SearchBar above task list. On search change (debounced), update filter state and re-fetch with `search=query` param. Show "No tasks match your search" empty state when search returns zero results.

**Checkpoint**: Search returns relevant results, empty state shows for no matches, performance <1s.

---

## Phase 7: User Story 5 - Advanced Filtering and Sorting (Priority: P2)

**Goal**: Users can combine multiple filters (priority + tags + date + overdue + status) and sort by any field.

**Independent Test**: Apply priority=high AND tags=work → only matching tasks → change sort to due_date → tasks reorder → click "Clear filters" → full list restored → apply filters with no matches → empty state with clear button.

**Acceptance**: FR-009, FR-010, FR-011, FR-020, SC-002, SC-005, SC-010

### Implementation

- [x] T032 [P] [US5] Create FilterPanel component (integrated inline in TaskList.tsx) in frontend/src/components/FilterPanel.tsx: renders collapsible panel with: priority multi-select checkboxes (low/medium/high/urgent), tag filter pills from user's tags (fetched via getTags()), date range inputs (due_after, due_before), overdue toggle, status selector (all/pending/completed). Includes "Clear all filters" button. Shows active filter count badge. Accepts filter state and onChange callback props.
- [x] T033 [US5] Update TaskList in frontend/src/components/TaskList.tsx: integrate FilterPanel above task list. Wire all filter controls to update shared filter state. Combine all active filters into single getTasks() call. Show active filter count. Add "No tasks match your filters" empty state with "Clear filters" link. Ensure sort controls work with combined filters.
- [x] T034 [US5] Add PATCH /api/tasks/bulk endpoint in backend/routes/tasks.py: accept BulkUpdateRequest body (task_ids + operations). Verify all task_ids belong to user. Apply operations (set priority, add/remove tags using array_append/array_remove, set due_date, set recurring_pattern). Return BulkUpdateResponse with updated_count and task_ids.

**Checkpoint**: Combined filters work correctly, sort by any field, empty states show, bulk update works, "Clear filters" resets all.

---

## Phase 8: User Story 6 - Recurring Task Patterns (Priority: P3)

**Goal**: Users can set recurring patterns on tasks and see a recurring indicator.

**Independent Test**: Create task with weekly recurrence → recurring icon shows → edit to monthly → icon updates → create task without recurrence → no icon shown.

**Acceptance**: FR-012, FR-013, FR-014, SC-001

### Implementation

- [x] T035 [US6] Update POST /api/tasks and PUT /api/tasks/{id} in backend/routes/tasks.py to accept and persist recurring_pattern field. Default "none". Validate against enum.
- [x] T036 [US6] Update TaskItem in frontend/src/components/TaskItem.tsx: add recurring indicator icon (repeat/refresh SVG icon) next to metadata when `recurring_pattern !== "none"`. Show tooltip with pattern text (e.g., "Repeats weekly"). Use gray color matching existing metadata style.
- [x] T037 [US6] Update TaskForm in frontend/src/components/TaskForm.tsx: add recurring pattern selector dropdown (none/daily/weekly/monthly) with "none" default. Only show in expanded/advanced section. Pass recurring_pattern to createTask API call.

**Checkpoint**: Recurring pattern saves, icon displays, editing pattern persists. Completing task does NOT auto-create new instance.

---

## Phase 9: User Story 7 - Chatbot Understands Advanced Features (Priority: P2)

**Goal**: AI chatbot parses and applies priority, tags, due dates, recurring patterns from natural language. Supports NL filtering.

**Independent Test**: Tell chatbot "add high priority task call dentist due next Monday tagged health" → task created with correct fields → ask "show my urgent tasks" → only urgent tasks listed → ask "what's overdue?" → overdue tasks shown.

**Acceptance**: FR-018, FR-019, SC-006

### Implementation

- [x] T038 [P] [US7] Update MCP tool schemas in backend/mcp_server/schemas.py: add priority, tags (List[str]), due_date (Optional[str]), recurring_pattern to AddTaskInput. Add priority, tags, overdue (bool), search (str), sort_by to ListTasksInput. Add priority, tags, due_date, recurring_pattern to UpdateTaskInput. Update TaskItem to include priority, tags, due_date, recurring_pattern, is_overdue fields.
- [x] T039 [US7] Update MCP tools in backend/mcp_server/tools.py: update add_task() to pass priority, tags, due_date, recurring_pattern when creating Task. Update list_tasks() to apply priority filter, tag filter (using @>), overdue filter, search filter (using search_vector.match()), and sort_by. Update update_task() to handle priority, tags, due_date, recurring_pattern changes. Update _task_to_item() to include new fields. Update get_tool_definitions() with new parameters per contracts/api-contracts.md MCP section.
- [x] T040 [US7] Enhance TaskParserSkill in backend/skills/task_parser.py: add regex patterns to extract priority ("high priority", "urgent", "low pri"), tags ("tagged work", "tag: personal", "#shopping"), due date ("due Friday", "due next Monday", "by Feb 15"), recurring ("every day", "weekly", "recurring daily"). Update ParsedTask dataclass with priority, tags, due_date, recurring_pattern fields. Parse due date strings to ISO 8601 using Python dateutil or manual relative date logic.
- [x] T041 [US7] Enhance FilterMapperSkill in backend/skills/filter_mapper.py: add regex patterns for priority ("urgent tasks", "high priority"), tags ("work tasks", "tagged personal"), overdue ("overdue", "past due", "late"), search ("find X", "search for X"). Update FilterParams dataclass with priority, tags, overdue, search fields.
- [x] T042 [US7] Update orchestrator tool result formatting in backend/agents/orchestrator.py: update _format_tool_result() for add_task to include priority, tags, due_date in confirmation message. Update list_tasks formatting to show priority badges and tags in text output. Update update_task to mention new field changes.

**Checkpoint**: "add high priority task tagged work due Friday" creates correct task. "show overdue tasks" returns filtered list. Chatbot accurately handles new features.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Integration testing, deployment, verification

- [x] T043 Test all CRUD operations with new fields via curl/Postman: create task with all fields, read back, update each field individually, verify filter combinations (priority + tag + overdue + search), verify sort by each field, verify bulk update, verify tags endpoint
- [x] T044 Test chatbot integration end-to-end: issue 5 NL commands covering create with advanced fields, query with filters, update with new fields, verify 90%+ accuracy per SC-006
- [x] T045 [P] Rebuild backend Docker image with new code for Kubernetes deployment: switch to minikube docker env, `docker build -t modern-taskflow-backend:v3 .` from backend/
- [x] T046 [P] Rebuild frontend Docker image with new code for Kubernetes deployment: `docker build --build-arg NEXT_PUBLIC_API_URL=http://localhost:30081 -t modern-taskflow-frontend:v3 .` from frontend/
- [x] T047 Update helm-chart/values-local.yaml to use v3 image tags for both frontend and backend, then run `helm upgrade modern-taskflow helm-chart/ -f helm-chart/values-local.yaml`
- [x] T048 Verify deployment on both Vercel (push to main triggers auto-deploy) and Kubernetes (port-forward, test in browser): confirm priority badges, tag pills, due dates, search, filters, chatbot all work

**Checkpoint**: All features working on both deployment targets, no regressions.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (Alembic setup) - BLOCKS all user stories
- **US1 Priority (Phase 3)**: Depends on Phase 2
- **US2 Tags (Phase 4)**: Depends on Phase 2
- **US3 Due Dates (Phase 5)**: Depends on Phase 2
- **US4 Search (Phase 6)**: Depends on Phase 2 (tsvector already in migration)
- **US5 Filtering & Sorting (Phase 7)**: Depends on Phases 3, 4, 5 (needs priority, tags, due_date fields working)
- **US6 Recurring (Phase 8)**: Depends on Phase 2
- **US7 Chatbot (Phase 9)**: Depends on Phases 3, 4, 5 (needs backend features working first)
- **Polish (Phase 10)**: Depends on all user stories

### User Story Dependencies

```text
Phase 1 (Setup) → Phase 2 (Foundational)
                        │
        ┌───────────┬───┼───────────┬───────────┐
        ↓           ↓   ↓           ↓           ↓
   US1 (P1)    US2 (P1) US3 (P1)  US4 (P2)   US6 (P3)
   Phase 3     Phase 4  Phase 5   Phase 6     Phase 8
        │           │       │
        └─────┬─────┘       │
              ↓             ↓
         US5 (P2)      US7 (P2)
         Phase 7       Phase 9
              │             │
              └──────┬──────┘
                     ↓
              Phase 10 (Polish)
```

### Parallel Opportunities

- T007, T008, T009 (Phase 2): Backend schemas, frontend types, frontend API — all different files
- T012 (Phase 3): PriorityBadge is standalone, can parallel with T010-T011
- T019 (Phase 4): TagPills is standalone, can parallel with T016-T018
- T025 (Phase 5): DueDateDisplay is standalone, can parallel with T023-T024
- T030 (Phase 6): SearchBar is standalone, can parallel with T029
- T032 (Phase 7): FilterPanel is standalone, can parallel with T034
- US1/US2/US3/US6 (Phases 3/4/5/8): Can start in parallel after Phase 2
- T038 (Phase 9): MCP schemas can parallel with T040-T041 (different files)
- T045, T046 (Phase 10): Docker builds can run in parallel

---

## Parallel Example: After Phase 2 Completes

```text
# Three P1 stories can start simultaneously:
Developer A: US1 Priority (T010-T015)
Developer B: US2 Tags (T016-T022)
Developer C: US3 Due Dates (T023-T028)

# Within US1, parallel tasks:
T010 (backend priority filter) || T012 (PriorityBadge component)
Then: T011, T013, T014, T015 sequentially
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009)
3. Complete Phase 3: US1 Priority (T010-T015)
4. **STOP and VALIDATE**: Create task with priority, verify badge, sort by priority
5. Deploy if ready — immediate value delivered

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 Priority → Test → Deploy (MVP!)
3. US2 Tags → Test → Deploy
4. US3 Due Dates → Test → Deploy
5. US4 Search → Test → Deploy
6. US5 Filtering → Test → Deploy (ties everything together)
7. US6 Recurring → Test → Deploy
8. US7 Chatbot → Test → Deploy (NL support for all features)
9. Polish → Final verification → Production

### Suggested Execution (Single Developer)

Execute sequentially in priority order: P1 stories first (US1→US2→US3), then P2 (US4→US5→US7), then P3 (US6). This ensures the highest-value features ship first.

---

## Summary

| Phase | Story | Tasks | Parallel |
|-------|-------|-------|----------|
| 1. Setup | — | T001-T003 (3) | 0 |
| 2. Foundational | — | T004-T009 (6) | 3 (T007,T008,T009) |
| 3. US1 Priority | P1 | T010-T015 (6) | 1 (T012) |
| 4. US2 Tags | P1 | T016-T022 (7) | 1 (T019) |
| 5. US3 Due Dates | P1 | T023-T028 (6) | 1 (T025) |
| 6. US4 Search | P2 | T029-T031 (3) | 1 (T030) |
| 7. US5 Filtering | P2 | T032-T034 (3) | 1 (T032) |
| 8. US6 Recurring | P3 | T035-T037 (3) | 0 |
| 9. US7 Chatbot | P2 | T038-T042 (5) | 1 (T038) |
| 10. Polish | — | T043-T048 (6) | 2 (T045,T046) |
| **Total** | | **48 tasks** | **11 parallel** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [US*] label maps task to specific user story for traceability
- Each user story is independently completable and testable after Phase 2
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend route changes (T010, T016, T023, T029) accumulate in same file — execute sequentially within each story, but different stories can be parallel
