---
id: "0002"
title: "Phase 5A Implementation Plan"
stage: plan
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 001-advanced-task-features
branch: 001-advanced-task-features
user: san
command: /sp.plan
labels: ["phase5a", "plan", "architecture", "migration", "api-design", "frontend-ui"]
links:
  spec: specs/001-advanced-task-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-advanced-task-features/plan.md
  - specs/001-advanced-task-features/research.md
  - specs/001-advanced-task-features/data-model.md
  - specs/001-advanced-task-features/quickstart.md
  - specs/001-advanced-task-features/contracts/api-contracts.md
tests:
  - none (plan phase)
---

## Prompt

/sp.plan

Phase 5A Advanced Task Features implementation planning. User provided detailed 8-phase implementation approach:
1. Database Migration (Alembic, new columns, indexes, triggers)
2. Backend Model & Schema Updates (SQLModel, Pydantic)
3. Backend API Enhancement (filter/sort/search, bulk ops, tags endpoint)
4. MCP Tool Updates (enhanced tool schemas and definitions)
5. Skill Enhancement (TaskParser + FilterMapper for NL)
6. Frontend Types & API Client Updates
7. Frontend UI Components (PriorityBadge, TagPills, FilterPanel, enhanced TaskForm/TaskItem/TaskList)
8. Chatbot Integration Testing + Deployment

Key architectural decisions to resolve: tag storage (array vs join table), search implementation (tsvector vs external), migration strategy (Alembic vs manual), priority storage format.

## Response snapshot

Generated 5 plan artifacts after thorough codebase exploration:

1. **research.md**: 10 technical decisions (TD-1 through TD-10) covering tag storage (TEXT[] chosen over join table), priority as string enum, tsvector for full-text search, Alembic for migrations, TIMESTAMPTZ for due dates, query parameter filtering on existing endpoints, bulk operations via PATCH, URL-based filter state in frontend, enhanced MCP tools extending existing architecture.

2. **data-model.md**: Complete updated Task entity with SQLModel definition using sa_column for ARRAY(Text) and TSVECTOR. Full migration script (forward + reverse). Updated Pydantic schemas (TaskCreate, TaskUpdate, TaskResponse with is_overdue, BulkUpdateRequest, TaskFilterParams). TypeScript interfaces for frontend.

3. **contracts/api-contracts.md**: Enhanced API contracts for GET/POST/PUT /api/tasks with new fields. New PATCH /api/tasks/bulk and GET /api/tasks/tags endpoints. Enhanced MCP tool definitions with new parameters. Enhanced skill contracts for TaskParserSkill and FilterMapperSkill.

4. **quickstart.md**: Step-by-step implementation order (8 phases), key files to modify (8 backend, 5 frontend), 3 new frontend components, verification checklist.

5. **plan.md**: Complete plan with Technical Context, Constitution Check (all PASS, one deviation noted), Project Structure with file-level change annotations, Complexity Tracking, Implementation Phases, Risks and Mitigations.

## Outcome

- Impact: Complete implementation plan ready for task generation via /sp.tasks
- Tests: No tests in plan phase
- Files: 5 artifacts (plan.md, research.md, data-model.md, quickstart.md, contracts/api-contracts.md)
- Next prompts: /sp.tasks to generate actionable task list, or /sp.adr for tag storage decision
- Reflection: Thorough codebase exploration was essential — discovered no Alembic setup exists, SQLModel uses create_all(), MCP tools need sa_column for PostgreSQL-specific types

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASS (all gates), one deviation documented (tags array vs join table)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
