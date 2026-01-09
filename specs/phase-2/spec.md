# Phase II Specification: Full-Stack Web Application with Authentication

**Reference**: [Project Constitution](../constitution.md) | [Phase I](../phase-1/spec.md)

---

## Overview

| Attribute | Value |
|-----------|-------|
| Phase | II |
| Type | Full-Stack Web Application |
| Storage | Neon Serverless Postgres |
| Frontend | Next.js 15+, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLModel ORM, Python 3.13+ |
| Auth | Better Auth with JWT tokens |

---

## Intent

Transform the Phase I console app into a multi-user web application with authentication. Users can sign up, log in, and manage their own tasks through a responsive web interface backed by a RESTful API and cloud database.

---

## Project Structure (Monorepo)

```
hackathon-2/
├── specs/
│   ├── phase-1/              # Phase I specs (existing)
│   └── phase-2/              # Phase II specs (this)
├── phase-1-console/          # Phase I code (moved)
├── frontend/                 # Next.js 15+ app
├── backend/                  # FastAPI app
├── docker-compose.yml        # Local development
├── CLAUDE.md                 # Root instructions
└── README.md
```

---

## Features

### Feature 1: User Signup

**Intent**: Allow new users to create an account.

**Behavior**:
- Display signup form (email, password, name)
- Validate inputs (email format, password strength)
- Create user in database via Better Auth
- Redirect to login or auto-login

**Acceptance Criteria**:
- [ ] Signup form displays with all fields
- [ ] Email validation (format check)
- [ ] Password validation (min 8 characters)
- [ ] User created in Neon database
- [ ] Success redirects to dashboard
- [ ] Duplicate email shows error

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | Valid email, password, name | Account created, redirected |
| 2 | Error | Invalid email format | "Invalid email address" |
| 3 | Error | Password < 8 chars | "Password must be at least 8 characters" |
| 4 | Error | Email already exists | "Email already registered" |

---

### Feature 2: User Login

**Intent**: Allow existing users to authenticate.

**Behavior**:
- Display login form (email, password)
- Authenticate via Better Auth
- Issue JWT token on success
- Store session, redirect to dashboard

**Acceptance Criteria**:
- [ ] Login form displays
- [ ] Valid credentials → JWT issued
- [ ] Session persists across page refresh
- [ ] Invalid credentials → error message
- [ ] Redirect to intended page after login

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | Valid credentials | JWT issued, redirected to dashboard |
| 2 | Error | Wrong password | "Invalid credentials" |
| 3 | Error | Non-existent email | "Invalid credentials" |

---

### Feature 3: Add Task (Web Form)

**Intent**: Allow authenticated users to create tasks.

**Behavior**:
- Display task creation form
- Validate title (required, 1-200 chars)
- POST to API with JWT
- Task saved with user_id
- Update task list

**Acceptance Criteria**:
- [ ] Form displays title and description fields
- [ ] Title required validation
- [ ] API call includes JWT header
- [ ] Task created with correct user_id
- [ ] New task appears in list

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | title="Buy groceries" | Task created, shown in list |
| 2 | Error | Empty title | "Title is required" |
| 3 | Error | No JWT | 401 Unauthorized |

---

### Feature 4: View Tasks

**Intent**: Display only the authenticated user's tasks.

**Behavior**:
- Fetch tasks from API (filtered by user_id)
- Display in responsive table/cards
- Show title, status, description preview
- Handle empty state

**Acceptance Criteria**:
- [ ] Only user's own tasks displayed
- [ ] Responsive layout (mobile/desktop)
- [ ] Empty state message when no tasks
- [ ] Status indicator (complete/incomplete)
- [ ] Created date displayed

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | User has 5 tasks | 5 tasks displayed |
| 2 | Edge Case | User has 0 tasks | "No tasks yet" message |
| 3 | Security | Different user's JWT | Only that user's tasks |

---

### Feature 5: Update Task

**Intent**: Allow users to modify their tasks.

**Behavior**:
- Click task to edit
- Inline or modal edit form
- PUT to API with changes
- Validate ownership (user_id)
- Update display

**Acceptance Criteria**:
- [ ] Edit mode accessible
- [ ] Title and description editable
- [ ] Changes saved to database
- [ ] Cannot edit other users' tasks
- [ ] Cancel reverts changes

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | Update title | Task updated in DB |
| 2 | Error | Empty title | Validation error |
| 3 | Security | Edit another user's task | 403 Forbidden |

---

### Feature 6: Delete Task

**Intent**: Allow users to remove their tasks with confirmation.

**Behavior**:
- Click delete button
- Show confirmation dialog
- DELETE to API
- Remove from display

**Acceptance Criteria**:
- [ ] Delete button visible
- [ ] Confirmation required
- [ ] Task removed from database
- [ ] Cannot delete other users' tasks
- [ ] UI updates after deletion

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | Confirm delete | Task removed |
| 2 | Happy Path | Cancel delete | Task unchanged |
| 3 | Security | Delete another user's task | 403 Forbidden |

---

### Feature 7: Mark Complete/Incomplete

**Intent**: Toggle task completion status.

**Behavior**:
- Checkbox or toggle button
- PATCH to API
- Update display immediately (optimistic)

**Acceptance Criteria**:
- [ ] Toggle control visible
- [ ] Status changes on click
- [ ] Database updated
- [ ] Visual feedback (strikethrough, color)

**Test Cases**:
| # | Type | Input | Expected Output |
|---|------|-------|-----------------|
| 1 | Happy Path | Toggle incomplete → complete | Status updated |
| 2 | Happy Path | Toggle complete → incomplete | Status updated |

---

### Feature 8: Protected Routes

**Intent**: Require authentication for task management.

**Behavior**:
- Check JWT on protected pages
- Redirect to login if not authenticated
- Redirect back after login

**Acceptance Criteria**:
- [ ] /tasks requires authentication
- [ ] Unauthenticated → redirect to /login
- [ ] After login → redirect to intended page
- [ ] Logout clears session

---

## API Endpoints

### Tasks API

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/{user_id}/tasks` | List user's tasks | Required |
| POST | `/api/{user_id}/tasks` | Create task | Required |
| GET | `/api/{user_id}/tasks/{id}` | Get task details | Required |
| PUT | `/api/{user_id}/tasks/{id}` | Update task | Required |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task | Required |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle complete | Required |

### Auth API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Create user account |
| POST | `/api/auth/login` | Login, return JWT |
| GET | `/api/auth/verify` | Verify JWT token |

### Response Formats

**Success (200/201)**:
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs",
  "completed": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

**Error (4xx/5xx)**:
```json
{
  "detail": "Error message here"
}
```

---

## Database Schema

### Users Table (Better Auth managed)

```sql
CREATE TABLE users (
  id VARCHAR PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Tasks Table

```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

---

## Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │     │  Frontend   │     │   Backend   │
│             │     │  (Next.js)  │     │  (FastAPI)  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │  1. Login Form    │                   │
       │──────────────────>│                   │
       │                   │                   │
       │                   │  2. Better Auth   │
       │                   │  Issues JWT       │
       │                   │                   │
       │  3. JWT Stored    │                   │
       │<──────────────────│                   │
       │                   │                   │
       │  4. Request Tasks │                   │
       │──────────────────>│                   │
       │                   │  5. API + JWT     │
       │                   │──────────────────>│
       │                   │                   │
       │                   │  6. Verify JWT    │
       │                   │  Extract user_id  │
       │                   │                   │
       │                   │  7. Query tasks   │
       │                   │  WHERE user_id=X  │
       │                   │                   │
       │                   │  8. Return tasks  │
       │                   │<──────────────────│
       │  9. Display tasks │                   │
       │<──────────────────│                   │
```

---

## Frontend Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout with auth provider
│   ├── page.tsx                # Landing/redirect
│   ├── login/page.tsx          # Login page
│   ├── signup/page.tsx         # Signup page
│   ├── tasks/page.tsx          # Main todo UI (protected)
│   └── api/auth/[...all]/route.ts  # Better Auth routes
├── components/
│   ├── TaskList.tsx            # Task list container
│   ├── TaskForm.tsx            # Add/edit task form
│   ├── TaskItem.tsx            # Single task row
│   └── Navbar.tsx              # Navigation with auth state
├── lib/
│   ├── api.ts                  # API client with JWT
│   ├── auth.ts                 # Better Auth config
│   └── types.ts                # TypeScript types
├── CLAUDE.md
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

---

## Backend Structure

```
backend/
├── main.py                     # FastAPI app, CORS, routes
├── models.py                   # SQLModel: User, Task
├── database.py                 # Neon connection
├── auth/
│   ├── jwt.py                  # JWT verification
│   └── dependencies.py         # Auth dependencies
├── routes/
│   ├── tasks.py                # Task CRUD endpoints
│   └── auth.py                 # Auth endpoints
├── schemas.py                  # Pydantic schemas
├── CLAUDE.md
└── requirements.txt
```

---

## Environment Variables

### Frontend (.env.local)
```
BETTER_AUTH_SECRET=your-secret-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@host/db
BETTER_AUTH_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000
```

---

## Security Requirements

| Requirement | Implementation |
|-------------|----------------|
| Password Storage | Hashed with bcrypt (Better Auth) |
| JWT Validation | Verify signature on every API call |
| User Isolation | Filter all queries by user_id |
| CORS | Whitelist frontend origin only |
| SQL Injection | Use SQLModel ORM (parameterized) |
| XSS | React escapes by default |

---

## Error Handling

| Status | Scenario | Response |
|--------|----------|----------|
| 200 | Success | Resource data |
| 201 | Created | New resource data |
| 400 | Bad Request | Validation error details |
| 401 | Unauthorized | "Authentication required" |
| 403 | Forbidden | "Access denied" |
| 404 | Not Found | "Resource not found" |
| 500 | Server Error | "Internal server error" |

---

## Non-Goals

- No password reset (Phase II)
- No OAuth/social login (Phase II)
- No task sharing between users
- No real-time updates (WebSocket)
- No task categories/priorities
- No due dates

---

## Success Criteria

- [ ] User can sign up with email/password
- [ ] User can log in and receive JWT
- [ ] User can CRUD their own tasks only
- [ ] JWT required for all task operations
- [ ] Frontend is responsive (mobile/desktop)
- [ ] API returns proper HTTP status codes
- [ ] CORS configured correctly
- [ ] Docker Compose runs both services
- [ ] No SQL injection vulnerabilities
- [ ] Passwords properly hashed
