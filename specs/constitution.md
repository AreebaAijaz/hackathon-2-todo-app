# Project Constitution: Evolution of Todo - 5-Phase Hackathon Project

## Core Principles

- **Spec-Driven Development**: Every feature requires Constitution + Specification before implementation
- **AI-Native Approach**: Claude Code generates all code, no manual coding allowed
- **Iterative Refinement**: Refine specs until Claude Code produces correct output
- **Cloud-Native Architecture**: Design for containerization and Kubernetes deployment from Phase I
- **Production Quality**: All phases must be functional, tested, and deployment-ready

---

## Key Standards

### Code Quality

- All Python code: type hints, docstrings, error handling
- All TypeScript/JavaScript: TypeScript strict mode, proper typing
- RESTful API design: proper HTTP methods, status codes, error responses
- Database: normalized schema, foreign keys, indexes where needed
- No hardcoded values: use environment variables for configuration

### Specification Requirements

- Every feature: clear intent, success criteria, constraints, non-goals
- Acceptance criteria: measurable, testable (not vague like "works well")
- API contracts: request/response schemas documented
- Error cases: explicitly defined and handled
- Test cases: minimum 3 per feature (happy path, edge case, error case)

### AI Chatbot Standards (Phases III-V)

- Natural language understanding: handle ambiguous commands
- Context awareness: remember conversation history
- Error recovery: graceful handling of unclear requests
- Action confirmation: confirm destructive operations (delete, update)
- Response format: clear, concise, actionable feedback

### Kubernetes Standards (Phases IV-V)

- All services: containerized with multi-stage Docker builds
- Resource limits: CPU/memory defined for all containers
- Health checks: liveness and readiness probes configured
- Secrets management: no credentials in code or configs
- Logging: structured logs with proper levels (INFO, ERROR, DEBUG)

---

## Advanced Task Features (Phase V)

### Priority System
- Tasks have priority levels: `low`, `medium`, `high`, `urgent`
- Default priority: `medium`
- Priority affects sort order and display styling
- UI shows color-coded priority badges (green/yellow/orange/red)
- API accepts priority as enum string on create/update

### Tag System
- Tasks support multiple tags (e.g., "work", "personal", "urgent")
- Tags are user-defined strings, stored as TEXT[] array column on the tasks table (GIN indexed)
- Tags enable filtering and organization
- Maximum 10 tags per task, max 30 characters per tag
- Tags are per-user (not shared across users)

### Due Dates
- Tasks can have optional due dates (datetime with timezone)
- Overdue tasks highlighted in UI with visual indicator
- Due dates enable time-based sorting and filtering
- Null due date = no deadline (valid state)
- Foundation for Phase 5B reminder/notification system

### Recurring Tasks
- Tasks can repeat on schedules: `daily`, `weekly`, `monthly`, `none`
- Default recurrence: `none`
- Recurring pattern stored on task model
- Completion marks current instance only; auto-creation of next instance deferred to Phase 5B
- Next occurrence date calculated but not auto-generated

### Search, Filter & Sort
- **Search**: full-text search on task title and description
- **Filter by**: status (pending/completed), priority, tags, due date range, overdue
- **Sort by**: created date, due date, priority, title (alphabetical)
- **Sort direction**: ascending or descending
- Filters combinable (e.g., high priority + overdue + tag:"work")
- API supports query parameters for all filter/sort options
- Frontend provides filter UI controls and persistent filter state

### Data Validation Rules

| Field | Constraint |
|-------|------------|
| priority | Enum: low, medium, high, urgent |
| tags | Array, max 10 items, each max 30 chars |
| due_date | ISO 8601 datetime or null |
| recurrence | Enum: none, daily, weekly, monthly |
| search query | Max 200 characters |

---

## Testing Standards

- **Unit tests**: core business logic covered (>80% coverage)
- **Integration tests**: API endpoints tested with real database
- **E2E tests**: critical user flows validated
- **Chatbot tests**: natural language commands verified
- **Kubernetes tests**: deployment manifests validated

---

## Documentation Standards

- **README**: setup instructions, architecture overview, API docs
- **Each phase**: dedicated documentation folder
- **Specifications**: stored in specs/ folder, version controlled
- **API documentation**: OpenAPI/Swagger for all endpoints
- **Deployment guides**: step-by-step for local and cloud

---

## Security Standards

- **Authentication**: secure session management (Phase II+)
- **Input validation**: sanitize all user inputs
- **SQL injection prevention**: parameterized queries only
- **CORS**: proper configuration for web clients
- **Secrets**: never commit to git, use .env with .gitignore

---

## Performance Standards

- API response time: <500ms for CRUD operations
- Database queries: indexed fields, no N+1 queries
- Chatbot response: <3 seconds for simple commands
- Docker images: optimized size (<500MB per service)
- Kubernetes: proper resource allocation, no over-provisioning

---

## Phase Progression Requirements

| Phase | Requirement | Dependency |
|-------|-------------|------------|
| Phase I | Clean architecture for future phases | Foundation |
| Phase II | API-first design for Phase III chatbot integration | Phase I |
| Phase III | Stateless design for Phase IV Kubernetes | Phase II |
| Phase IV | Local K8s working before Phase V cloud deployment | Phase III |
| Phase V | Production-grade with monitoring and scaling | Phase IV |

---

## Success Criteria

| Phase | Deliverable | Points |
|-------|-------------|--------|
| Phase I | Console app with all basic features working | - |
| Phase II | Full-stack web app deployed, API functional | - |
| Phase III | Chatbot manages todos via natural language | - |
| Phase IV | App running on Minikube with Helm charts | - |
| Phase V | Production deployment on DigitalOcean DOKS with Kafka + Dapr | - |
| **Total** | **1000 points achievable, all phases completed on time** | 1000 |

---

*Constitution applies to ALL 5 phases. Phase-specific specifications will reference this Constitution without restating global rules.*
