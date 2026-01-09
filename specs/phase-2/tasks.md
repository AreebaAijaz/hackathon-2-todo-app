# Phase II Task Breakdown

**Reference**: [Plan](./plan.md) | [Specification](./spec.md)

---

## Phase 1: Restructure (3 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 1.1 | Move Phase I to `phase-1-console/` | Phase I preserved |
| 1.2 | Initialize Next.js frontend with TypeScript | `frontend/` created |
| 1.3 | Initialize FastAPI backend with SQLModel | `backend/` created |

**CHECKPOINT 1**: Project structure ready

---

## Phase 2: Database (4 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 2.1 | Design schema, create SQLModel models | User, Task models |
| 2.2 | Set up Neon connection in database.py | Connection working |
| 2.3 | Create database tables | Tables exist in Neon |
| 2.4 | Test CRUD operations | Queries work |

**CHECKPOINT 2**: Database operational

---

## Phase 3: Better Auth (5 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 3.1 | Install Better Auth, configure JWT | Auth setup |
| 3.2 | Create signup page | Signup UI working |
| 3.3 | Create login page | Login UI working |
| 3.4 | Set up auth API routes | Auth endpoints exist |
| 3.5 | Test signup/login flow | JWT issued on login |

**CHECKPOINT 3**: Auth working frontend

---

## Phase 4: Backend Auth (4 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 4.1 | Create JWT verification middleware | Verifies tokens |
| 4.2 | Build auth routes (signup, login) | Backend auth endpoints |
| 4.3 | Add CORS configuration | Frontend can call backend |
| 4.4 | Test auth endpoints | Auth flow complete |

**CHECKPOINT 4**: Backend auth ready

---

## Phase 5: Task API (5 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 5.1 | Create task routes skeleton | Routes defined |
| 5.2 | Implement GET /tasks (list with user filter) | List works |
| 5.3 | Implement POST /tasks (create) | Create works |
| 5.4 | Implement PUT, DELETE, PATCH | All CRUD done |
| 5.5 | Test with Postman | API verified |

**CHECKPOINT 5**: API functional

---

## Phase 6: Frontend UI (6 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 6.1 | Create TaskList component | Displays tasks |
| 6.2 | Create TaskForm component | Add/edit form |
| 6.3 | Create TaskItem component | Individual task UI |
| 6.4 | Build API client with JWT | api.ts with auth |
| 6.5 | Connect components to API | Full CRUD in UI |
| 6.6 | Add loading/error states | UX polished |

**CHECKPOINT 6**: UI complete

---

## Phase 7: Integration (4 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 7.1 | Test signup → login → tasks flow | Full flow works |
| 7.2 | Test user isolation (create 2 users) | Data separated |
| 7.3 | Test all CRUD operations | Everything functional |
| 7.4 | Test mobile responsiveness | Responsive UI |

**CHECKPOINT 7**: Integration verified

---

## Phase 8: Docker & Docs (4 tasks)

| Task | Description | Deliverable |
|------|-------------|-------------|
| 8.1 | Create docker-compose.yml | Services defined |
| 8.2 | Create Dockerfiles (frontend, backend) | Containers build |
| 8.3 | Update README.md, CLAUDE.md files | Docs complete |
| 8.4 | Commit and push to GitHub | Phase II deployed |

**CHECKPOINT 8**: Phase II complete

---

## Task Flow

```
Phase 1: Restructure
  [1.1] → [1.2] → [1.3] → CHECKPOINT 1
                              ↓
Phase 2: Database
  [2.1] → [2.2] → [2.3] → [2.4] → CHECKPOINT 2
                                      ↓
Phase 3: Better Auth
  [3.1] → [3.2] → [3.3] → [3.4] → [3.5] → CHECKPOINT 3
                                              ↓
Phase 4: Backend Auth
  [4.1] → [4.2] → [4.3] → [4.4] → CHECKPOINT 4
                                      ↓
Phase 5: Task API
  [5.1] → [5.2] → [5.3] → [5.4] → [5.5] → CHECKPOINT 5
                                              ↓
Phase 6: Frontend UI
  [6.1] → [6.2] → [6.3] → [6.4] → [6.5] → [6.6] → CHECKPOINT 6
                                                      ↓
Phase 7: Integration
  [7.1] → [7.2] → [7.3] → [7.4] → CHECKPOINT 7
                                      ↓
Phase 8: Docker & Docs
  [8.1] → [8.2] → [8.3] → [8.4] → CHECKPOINT 8
```

---

## Summary

| Phase | Tasks | Focus |
|-------|-------|-------|
| 1 | 3 | Restructure |
| 2 | 4 | Database |
| 3 | 5 | Better Auth |
| 4 | 4 | Backend Auth |
| 5 | 5 | Task API |
| 6 | 6 | Frontend UI |
| 7 | 4 | Integration |
| 8 | 4 | Docker & Docs |
| **Total** | **35** | |
