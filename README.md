# Evolution of Todo

A 5-phase hackathon project demonstrating the evolution of a Todo application from console app to cloud-native Kubernetes deployment.

## Current Phase: II - Full-Stack Web Application

Full-stack todo app with Next.js frontend, FastAPI backend, and Neon Postgres database with authentication.

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

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15+, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLModel, Python 3.13+ |
| Database | Neon Serverless Postgres |
| Auth | Better Auth (JWT sessions) |
| Package Mgmt | UV (Python), npm (Node) |

## Features

- User authentication (signup, login, logout)
- Task CRUD operations
- User isolation (users see only their tasks)
- Mobile-responsive UI
- Session-based authentication with JWT

## Project Structure

```
hackathon-2/
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # App Router pages
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities & API client
│   └── Dockerfile
├── backend/                # FastAPI application
│   ├── routes/            # API endpoints
│   ├── auth/              # Auth dependencies
│   ├── models.py          # SQLModel models
│   ├── database.py        # DB connection
│   └── Dockerfile
├── phase-1-console/        # Phase I code (preserved)
├── specs/                  # Specifications
├── docker-compose.yml
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/tasks` | List user's tasks |
| POST | `/api/tasks` | Create task |
| GET | `/api/tasks/{id}` | Get task |
| PUT | `/api/tasks/{id}` | Update task |
| DELETE | `/api/tasks/{id}` | Delete task |
| PATCH | `/api/tasks/{id}/complete` | Toggle completion |

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
BETTER_AUTH_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000
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
| III | AI Chatbot Integration | Pending |
| IV | Kubernetes Deployment | Pending |
| V | Production Cloud | Pending |

## Development Standards

All development follows the [Project Constitution](specs/constitution.md).

- TypeScript strict mode for frontend
- Type hints on all Python code
- SQLModel for ORM
- Better Auth for authentication
- User isolation on all task operations
