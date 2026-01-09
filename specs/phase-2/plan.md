# Phase II Implementation Plan

**Reference**: [Specification](./spec.md) | [Constitution](../constitution.md)

---

## Architecture

```
Next.js (Frontend) ←→ FastAPI (Backend) ←→ Neon Postgres
Auth: Better Auth (Frontend) → JWT → FastAPI verification
```

---

## Implementation Phases

### Phase 1: Project Restructure & Setup

- [ ] Move Phase I to `phase-1-console/` folder
- [ ] Create `frontend/` and `backend/` folders
- [ ] Initialize Next.js 15 with TypeScript
- [ ] Initialize FastAPI with SQLModel
- [ ] Set up Neon Postgres database
- [ ] Create root CLAUDE.md

### Phase 2: Database & Models

- [ ] Design database schema (users, tasks)
- [ ] Create SQLModel models (User, Task)
- [ ] Set up Neon connection in backend
- [ ] Create database tables
- [ ] Test connection

### Phase 3: Better Auth Setup

- [ ] Install Better Auth in frontend
- [ ] Configure JWT plugin
- [ ] Create signup/login pages
- [ ] Set up auth routes in Next.js
- [ ] Configure shared BETTER_AUTH_SECRET
- [ ] Test signup/login flow

### Phase 4: Backend Auth Integration

- [ ] Create JWT verification middleware
- [ ] Build auth routes (signup, login, verify)
- [ ] Implement user_id extraction from JWT
- [ ] Test JWT verification
- [ ] Add CORS configuration

### Phase 5: Backend Task API

- [ ] Create task routes (CRUD endpoints)
- [ ] Implement user_id filtering
- [ ] Add request/response schemas
- [ ] Test all endpoints with Postman/curl
- [ ] Verify user isolation

### Phase 6: Frontend Task UI

- [ ] Create TaskList, TaskForm, TaskItem components
- [ ] Build tasks page
- [ ] Implement API client with JWT
- [ ] Connect UI to backend API
- [ ] Add loading/error states

### Phase 7: Integration & Testing

- [ ] Test full user flow (signup → login → tasks)
- [ ] Verify user isolation (multiple users)
- [ ] Test all CRUD operations
- [ ] Fix bugs and edge cases
- [ ] Verify mobile responsiveness

### Phase 8: Docker & Documentation

- [ ] Create docker-compose.yml
- [ ] Create Dockerfiles for frontend/backend
- [ ] Write README.md
- [ ] Write CLAUDE.md files
- [ ] Test Docker setup
- [ ] Commit to GitHub

---

## Execution Order

```
Phase 1 (Restructure & Setup)
    ↓
Phase 2 (Database & Models)
    ↓
Phase 3 (Better Auth Setup)
    ↓
Phase 4 (Backend Auth Integration)
    ↓
Phase 5 (Backend Task API)
    ↓
Phase 6 (Frontend Task UI)
    ↓
Phase 7 (Integration & Testing)
    ↓
Phase 8 (Docker & Documentation)
```

**Dependencies**: Sequential (Phase 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8)

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Auth | Better Auth with JWT | Requirement |
| Database | Neon cloud DB | No local Postgres needed |
| Structure | Monorepo | Easier for Claude Code |
| Approach | API-first | Backend before frontend UI |

---

## Commands Reference

### Backend
```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up
```
