# Claude Code Instructions

## Project Overview

**Evolution of Todo** - A 5-phase hackathon project building a Todo application from console app to cloud-native Kubernetes deployment.

**Current Phase**: Phase II - Full-Stack Web Application with Authentication

---

## Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Constitution | `specs/constitution.md` | Global project standards |
| Phase II Spec | `specs/phase-2/spec.md` | Feature requirements |
| Phase II Plan | `specs/phase-2/plan.md` | Implementation approach |
| Phase II Tasks | `specs/phase-2/tasks.md` | Task breakdown |

---

## Project Structure (Monorepo)

```
hackathon-2/
├── phase-1-console/     # Phase I code (preserved)
├── frontend/            # Next.js 15+ app
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── CLAUDE.md
├── backend/             # FastAPI app
│   ├── routes/
│   ├── auth/
│   └── CLAUDE.md
├── specs/
│   ├── constitution.md
│   ├── phase-1/
│   └── phase-2/
├── docker-compose.yml
└── README.md
```

---

## Tech Stack

### Frontend
- Next.js 15+ (App Router)
- TypeScript (strict mode)
- Tailwind CSS
- Better Auth (JWT)

### Backend
- FastAPI
- SQLModel ORM
- Python 3.13+
- UV package manager

### Database
- Neon Serverless Postgres

---

## Development Commands

### Frontend
```bash
cd frontend
npm install
npm run dev          # localhost:3000
```

### Backend
```bash
cd backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

### Docker
```bash
docker-compose up    # Both services
```

---

## Implementation Rules

1. **Read specs first** - Check `specs/phase-2/spec.md` before implementing
2. **Follow the plan** - Implement in order defined in `specs/phase-2/plan.md`
3. **Track tasks** - Use `specs/phase-2/tasks.md` checkpoints
4. **API-first** - Build backend endpoints before frontend UI
5. **No manual coding** - Claude Code generates all code

---

## Authentication Flow

```
User → Better Auth (Frontend) → JWT issued
     → API Request + JWT Header
     → FastAPI verifies JWT → Extract user_id
     → Query tasks WHERE user_id = X
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Create account |
| POST | `/api/auth/login` | Login, get JWT |
| GET | `/api/{user_id}/tasks` | List tasks |
| POST | `/api/{user_id}/tasks` | Create task |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle |

---

## Environment Variables

### Frontend (.env.local)
```
BETTER_AUTH_SECRET=...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
DATABASE_URL=postgresql://...
BETTER_AUTH_SECRET=...
CORS_ORIGINS=http://localhost:3000
```

---

## Validation Rules

| Field | Constraint |
|-------|------------|
| email | Valid format, unique |
| password | Min 8 characters |
| title | Required, 1-200 characters |
| description | Optional, max 500 characters |

---

## Error Messages

| Scenario | Message |
|----------|---------|
| Invalid email | "Invalid email address" |
| Weak password | "Password must be at least 8 characters" |
| Email exists | "Email already registered" |
| Invalid credentials | "Invalid credentials" |
| Task not found | "Task not found" |
| Unauthorized | "Authentication required" |
| Forbidden | "Access denied" |
