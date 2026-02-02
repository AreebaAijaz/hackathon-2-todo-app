# Evolution of Todo

A 5-phase hackathon project demonstrating the evolution of a Todo application from console app to cloud-native Kubernetes deployment.

## Current Phase: IV - Local Kubernetes Deployment

Full-stack todo app with AI chatbot, deployed on local Kubernetes via Minikube and Helm.

## Quick Start

### Prerequisites
- Node.js 20+
- Python 3.13+
- UV package manager
- Neon Postgres database

### Backend Setup
```bash
cd backend
cp .env.example .env  # Configure DATABASE_URL and BETTER_AUTH_SECRET
uv sync
uv run uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
cp .env.example .env.local  # Configure DATABASE_URL and BETTER_AUTH_SECRET
npm install
npm run dev
```

### Docker Setup
```bash
# Set environment variables in .env file
docker-compose up --build
```

### Kubernetes Setup (Minikube)
```bash
minikube start
# Windows:
.\scripts\deploy-minikube.ps1
# Linux/macOS:
./scripts/deploy-minikube.sh
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15+, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLModel, Python 3.13+ |
| Database | Neon Serverless Postgres |
| Auth | Better Auth (JWT sessions) |
| AI | OpenAI GPT-4o, Multi-Agent Architecture |
| Orchestration | Docker Compose, Kubernetes (Helm) |
| Package Mgmt | UV (Python), npm (Node) |

## Features

### Phase I - Console Application
- Rich CLI with formatted output
- Local JSON file storage
- Basic CRUD operations

### Phase II - Full-Stack Web Application
- User authentication (signup, login, logout)
- Task CRUD operations with REST API
- User isolation (users see only their tasks)
- Mobile-responsive UI with Tailwind CSS
- Session-based authentication with JWT

### Phase III - AI Chatbot Integration
- Natural language task management ("add buy groceries")
- Multi-agent orchestrator with 4 specialized subagents
- 6 reusable skills (task parser, ID resolver, filter mapper, confirmation generator, error handler, context builder)
- MCP tools for database operations
- Conversation history persistence
- Streaming chat UI

### Phase IV - Kubernetes Deployment
- Minikube local cluster deployment
- Helm chart with configmap and secrets separation
- Resource limits and health checks (liveness + readiness)
- Deployment scripts for Windows and Linux/macOS

## Project Structure

```
hackathon-2/
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # App Router pages
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities, API client, types
│   └── Dockerfile
├── backend/                # FastAPI application
│   ├── routes/            # API endpoints (tasks, chat, auth)
│   ├── auth/              # JWT verification dependencies
│   ├── agents/            # Multi-agent orchestrator + subagents
│   ├── skills/            # Reusable NLP skills library
│   ├── mcp_server/        # MCP tools for AI agents
│   ├── models.py          # SQLModel database models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── database.py        # DB connection with pooling
│   └── Dockerfile
├── phase-1-console/        # Phase I console app (preserved)
├── helm-chart/             # Kubernetes Helm chart
│   ├── templates/         # K8s manifests (deployments, services, secrets)
│   └── values.yaml        # Configuration values
├── scripts/                # Deployment automation scripts
├── specs/                  # Specifications and standards
│   ├── constitution.md    # Global project standards
│   ├── phase-1/           # Phase I spec
│   ├── phase-2/           # Phase II spec, plan, tasks
│   └── phase-3/           # Phase III spec, plan, tasks
├── docker-compose.yml
└── README.md
```

## Architecture

### Multi-Agent AI System
```
User Message
  → Orchestrator (intent detection)
    → CRUD Agent (add/update/delete tasks)
    → Query Agent (list/filter tasks)
    → Completion Agent (mark done/undone)
    → Context Agent (conversation history)
  → Skills (task_parser, id_resolver, filter_mapper, ...)
  → MCP Tools (add_task, list_tasks, complete_task, delete_task, update_task)
  → Database
```

### Authentication Flow
```
User → Better Auth (Frontend) → JWT issued
     → API Request + Bearer token
     → FastAPI verifies token against session table
     → Extract user_id → Query tasks WHERE user_id = X
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/auth/verify` | Verify JWT token |
| GET | `/api/auth/me` | Get current user info |
| GET | `/api/tasks` | List user's tasks |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/{id}` | Get task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/{id}/complete` | Toggle completion |
| POST | `/api/chat` | Process chat message (AI) |
| GET | `/api/conversations` | List conversations |
| GET | `/api/conversations/{id}` | Get conversation detail |
| DELETE | `/api/conversations/{id}` | Delete conversation |

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
BETTER_AUTH_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000
OPENAI_API_KEY=sk-your-openai-key
```

### Frontend (.env.local)
```env
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
BETTER_AUTH_SECRET=your-secret-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Phase Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| I | Console Application | **Complete** |
| II | Full-Stack Web App | **Complete** |
| III | AI Chatbot Integration | **Complete** |
| IV | Kubernetes Deployment | **Complete** |
| V | Production Cloud (DigitalOcean DOKS) | Planned |

## Reusable Patterns

| Pattern | Location | Applicable To |
|---------|----------|---------------|
| Abstract base classes (Agent, Skill) | `backend/agents/base.py`, `backend/skills/base.py` | Any AI/plugin system |
| Multi-agent orchestrator | `backend/agents/orchestrator.py` | Any NLP/chatbot project |
| JWT auth with user isolation | `backend/auth/dependencies.py` | Any multi-tenant app |
| Centralized API client | `frontend/src/lib/api.ts` | Any frontend consuming APIs |
| Helm chart with secrets separation | `helm-chart/` | Any Kubernetes deployment |
| Spec-driven development | `specs/constitution.md` | Any team project |

## Development Standards

All development follows the [Project Constitution](specs/constitution.md).

- TypeScript strict mode for frontend
- Type hints on all Python code
- SQLModel for ORM with Pydantic validation
- Better Auth for authentication
- User isolation on all task operations
- Parameterized queries (SQL injection prevention)
- CORS whitelist configuration
