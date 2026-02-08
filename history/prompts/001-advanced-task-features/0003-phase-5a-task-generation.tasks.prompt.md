---
id: "0003"
title: "Phase 5A Task Generation"
stage: tasks
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 001-advanced-task-features
branch: 001-advanced-task-features
user: san
command: /sp.tasks
labels: ["phase5a", "tasks", "implementation", "48-tasks", "7-user-stories"]
links:
  spec: specs/001-advanced-task-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-advanced-task-features/tasks.md
tests:
  - none (task generation phase)
---

## Prompt

/sp.tasks

Phase 1: Constitution & Database (3 tasks)
1.1 Update constitution.md with advanced features → Constitution updated
1.2 Create database migration script → Migration ready
1.3 Test migration on dev database → Schema updated

Phase 2: Backend API (6 tasks)
2.1 Update Task SQLModel with new fields → Model updated
2.2 Implement enhanced GET /tasks with filters → Filtering works
2.3 Implement search endpoint with tsvector → Search works
2.4 Add bulk operations endpoint → Bulk update works
2.5 Add GET /tags endpoint → Tags endpoint works
2.6 Test all endpoints with Postman → API verified

Phase 3: MCP & Chatbot (5 tasks)
3.1 Update add_task MCP tool → Accepts new params
3.2 Update list_tasks MCP tool → Supports filters
3.3 Add search_tasks MCP tool → Search via chatbot
3.4 Update Task Parser skill → Extracts priority/tags/dates
3.5 Test chatbot commands → Natural language works

Phase 4: Frontend Components (6 tasks)
4.1 Create PriorityBadge component → Priority colors work
4.2 Create TagPill component → Tags display work
4.3 Create DueDateDisplay component → Due dates with overdue
4.4 Create FilterPanel component → Filters work
4.5 Create SearchBar component → Search UI works
4.6 Update TaskCard and CreateTaskForm → Forms updated

Phase 5: Frontend Integration (4 tasks)
5.1-5.4 Integrate components, sort, mobile responsive

Phase 6: Integration Testing (4 tasks)
6.1-6.4 Test CRUD, filters, search, chatbot

Phase 7: Deployment (3 tasks)
7.1 Run migration on Neon

## Response snapshot

Generated comprehensive tasks.md with 48 tasks organized by user story across 10 phases:

- Phase 1 (Setup): 3 tasks — Alembic init, constitution update
- Phase 2 (Foundational): 6 tasks — Migration, model, schemas, types, API client (BLOCKS all stories)
- Phase 3 (US1 Priority, P1): 6 tasks — Backend priority filter/sort, PriorityBadge, TaskForm/Item/List
- Phase 4 (US2 Tags, P1): 7 tasks — Backend tag filter, tags endpoint, TagPills, autocomplete
- Phase 5 (US3 Due Dates, P1): 6 tasks — Backend date filter, DueDateDisplay, overdue highlighting
- Phase 6 (US4 Search, P2): 3 tasks — tsvector search, SearchBar component
- Phase 7 (US5 Filtering, P2): 3 tasks — FilterPanel, combined filters, bulk update
- Phase 8 (US6 Recurring, P3): 3 tasks — Pattern storage, icon, selector
- Phase 9 (US7 Chatbot, P2): 5 tasks — MCP tools, TaskParser, FilterMapper, orchestrator
- Phase 10 (Polish): 6 tasks — Testing, Docker rebuild, Helm upgrade, verification

Reorganized from user's layer-based phasing (7 phases) to user-story-based phasing (10 phases) per template requirements. Dependency graph shows US1/US2/US3/US6 can start in parallel after foundational phase; US5 depends on US1-US3; US7 depends on US1-US3.

## Outcome

- Impact: 48 actionable tasks ready for /sp.implement execution
- Tests: No dedicated test tasks (not requested); integration testing in Phase 10
- Files: specs/001-advanced-task-features/tasks.md
- Next prompts: /sp.implement to begin executing tasks, or /sp.analyze to verify cross-artifact consistency
- Reflection: User-story organization reveals clear parallelization opportunities; foundational phase consolidates shared schema changes to avoid cross-story conflicts in same files

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Format validation PASS (all 48 tasks have checkbox, ID, labels, file paths)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
