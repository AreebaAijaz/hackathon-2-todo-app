# Quickstart: Phase 5A - Advanced Task Features

**Feature Branch**: `001-advanced-task-features`
**Prereqs**: Phase II/III working app (Vercel + Minikube deployments)

## Implementation Order

The implementation follows a bottom-up approach: database → backend API → MCP tools/skills → frontend UI → chatbot integration.

### Phase 1: Database Migration (backend)
1. Add `alembic` dependency to `pyproject.toml`
2. Initialize Alembic: `alembic init alembic`
3. Configure `alembic/env.py` to use SQLModel + DATABASE_URL
4. Create baseline migration (capture current schema)
5. Create Phase 5A migration (add columns, indexes, trigger)
6. Update `Task` model in `backend/models.py` with new fields
7. Run migration locally, verify on Neon

### Phase 2: Backend API Enhancement (backend)
1. Update `backend/schemas.py` with enhanced TaskCreate, TaskUpdate, TaskResponse
2. Update `GET /api/tasks` in `backend/routes/tasks.py` with filter/sort/search params
3. Update `POST /api/tasks` and `PUT /api/tasks/{id}` to accept new fields
4. Add `PATCH /api/tasks/bulk` endpoint
5. Add `GET /api/tasks/tags` endpoint
6. Add `is_overdue` computed property to TaskResponse

### Phase 3: MCP Tools & Skills (backend)
1. Update `backend/mcp_server/schemas.py` with new fields on AddTaskInput, ListTasksInput, UpdateTaskInput, TaskItem
2. Update `backend/mcp_server/tools.py` to pass new fields through
3. Update MCP tool definitions (get_tool_definitions) with new parameters
4. Enhance `TaskParserSkill` to extract priority, tags, due dates from NL
5. Enhance `FilterMapperSkill` to map priority/tag/overdue/search filters

### Phase 4: Frontend Types & API Client (frontend)
1. Update `frontend/src/lib/types.ts` with new Task fields, filter types
2. Update `frontend/src/lib/api.ts` with filter params, bulk update, tags endpoint

### Phase 5: Frontend UI Components (frontend)
1. Add priority badge component (color-coded)
2. Add tag pills component (clickable for filtering)
3. Add due date display with overdue highlighting
4. Add recurring indicator icon
5. Update TaskForm with priority selector, tag input, date picker, recurring selector
6. Update TaskItem to display new fields
7. Add FilterPanel component (priority, tags, date range, overdue, search)
8. Update TaskList to manage enhanced filter state and pass params to API
9. Add empty state for no-results with "clear filters" button

### Phase 6: Chatbot Integration (backend)
1. Update orchestrator's tool result formatting for new fields
2. Test NL commands: "add high priority task tagged work due Friday"
3. Test NL queries: "show overdue tasks", "find urgent work tasks"

### Phase 7: Testing
1. Backend: Test migration, enhanced endpoints, bulk ops, search
2. Frontend: Test filter panel, priority badges, tag pills, date picker
3. Chatbot: Test NL parsing for new features
4. E2E: Test full flow through UI and chat

### Phase 8: Deployment
1. Run Alembic migration on Neon production DB
2. Rebuild Docker images with new code
3. Deploy to Vercel (frontend auto-deploys on push)
4. Helm upgrade for Kubernetes deployment
5. Verify on both platforms

## Key Files to Modify

### Backend
| File | Changes |
|------|---------|
| `backend/pyproject.toml` | Add `alembic` dependency |
| `backend/models.py` | Add new fields to Task model |
| `backend/schemas.py` | Enhanced request/response schemas |
| `backend/routes/tasks.py` | Filter, sort, search, bulk, tags endpoints |
| `backend/mcp_server/schemas.py` | Enhanced MCP input/output schemas |
| `backend/mcp_server/tools.py` | Pass new fields, enhanced tool definitions |
| `backend/skills/task_parser.py` | Extract priority, tags, due dates from NL |
| `backend/skills/filter_mapper.py` | Map NL to enhanced filters |

### Frontend
| File | Changes |
|------|---------|
| `frontend/src/lib/types.ts` | New fields on Task, filter types |
| `frontend/src/lib/api.ts` | Filter params, bulk update, tags endpoint |
| `frontend/src/components/TaskForm.tsx` | Priority, tags, date, recurring inputs |
| `frontend/src/components/TaskItem.tsx` | Priority badge, tags, due date, recurring icon |
| `frontend/src/components/TaskList.tsx` | Filter panel, enhanced state management |

### New Files
| File | Purpose |
|------|---------|
| `backend/alembic/` | Alembic migration config and versions |
| `frontend/src/components/PriorityBadge.tsx` | Priority display component |
| `frontend/src/components/TagPills.tsx` | Tag display/filter component |
| `frontend/src/components/FilterPanel.tsx` | Filter controls panel |

## Quick Verification

After each phase, verify:

1. **Migration**: `alembic upgrade head` succeeds, `\d tasks` shows new columns
2. **API**: `curl GET /api/tasks?priority=high&sort_by=due_date` returns filtered results
3. **MCP Tools**: Chatbot "add high priority task buy milk tagged shopping" creates correct task
4. **Frontend**: Task cards show priority badges, tag pills, due dates
5. **Filters**: Clicking tag pill filters list, priority dropdown works, search returns ranked results
