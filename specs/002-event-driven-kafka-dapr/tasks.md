# Tasks: Phase 5B - Event-Driven Architecture with Kafka & Dapr

**Input**: Design documents from `/specs/002-event-driven-kafka-dapr/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-contracts.md, quickstart.md
**Branch**: `002-event-driven-kafka-dapr`

**Tests**: Manual integration testing only (per spec). No automated test tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. Infrastructure stories (US5) come first as they are prerequisites for all other stories.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US5)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Dapr runtime and Redpanda broker on Minikube — the prerequisites for all event-driven functionality.

- [x] T001 Install Dapr on Minikube cluster by running `dapr init -k` and verify all control plane pods are healthy via `dapr status -k`
- [x] T002 Create Redpanda StatefulSet manifest in k8s/redpanda/redpanda-statefulset.yaml with single-node config (--smp=1, --memory=512M, --overprovisioned, --check=false), resource limits (512Mi-1Gi), and health probes on port 9644
- [x] T003 [P] Create Redpanda Service manifest in k8s/redpanda/redpanda-service.yaml exposing ports 9092 (kafka), 8082 (proxy), 9644 (admin)
- [x] T004 Deploy Redpanda to Minikube by running `kubectl apply -f k8s/redpanda/` and wait for pod ready
- [x] T005 Create 3 Kafka topics on Redpanda: `task-events` (3 partitions), `reminders` (1 partition), `task-updates` (3 partitions) via `kubectl exec redpanda-0 -- rpk topic create`
- [x] T006 [P] Create Dapr kafka-pubsub component in k8s/dapr-components/kafka-pubsub.yaml with broker address `redpanda.default.svc.cluster.local:9092`, authRequired false, initialOffset oldest
- [x] T007 [P] Create Dapr notification subscription in k8s/subscriptions/notification-sub.yaml routing `reminders` topic to `/reminders` endpoint, scoped to `notification-service`
- [x] T008 [P] Create Dapr recurring subscription in k8s/subscriptions/recurring-sub.yaml routing `task-events` topic to `/task-events` endpoint, scoped to `recurring-service`
- [x] T009 [P] Create Dapr audit subscription in k8s/subscriptions/audit-sub.yaml routing `task-events` topic to `/task-events` endpoint, scoped to `audit-service`
- [x] T010 Deploy Dapr components and subscriptions by running `kubectl apply -f k8s/dapr-components/` and `kubectl apply -f k8s/subscriptions/`, verify via `kubectl get components.dapr.io` and `kubectl get subscriptions.dapr.io`

**CHECKPOINT 1**: `dapr status -k` shows all healthy, `rpk topic list` shows 3 topics, Dapr components and subscriptions are active.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend event publishing infrastructure that MUST be complete before any consumer service can be tested.

**⚠️ CRITICAL**: No consumer service work (US2, US3, US4) can be verified until this phase is complete.

- [x] T011 Add `httpx>=0.27` to main dependencies in backend/pyproject.toml (currently only in test extras) and run `uv lock`
- [x] T012 [P] Create event schema models (TaskEventData, TaskEvent, ReminderEvent) in backend/events/schemas.py per data-model.md Pydantic schemas
- [x] T013 [P] Create `backend/events/__init__.py` with exports for publisher and schemas
- [x] T014 Create async event publisher helper `publish_event(topic, data)` in backend/events/publisher.py using httpx.AsyncClient to POST to `http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/kafka-pubsub/{topic}` with fire-and-forget error handling (try/except, log warning on failure) and `DAPR_HTTP_PORT` env var support (default 3500)
- [x] T015 Add `parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")` to Task model in backend/models.py
- [x] T016 Create Alembic migration for `parent_task_id` column: `ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER NULL REFERENCES tasks(id) ON DELETE SET NULL` with index in backend/alembic/versions/

**CHECKPOINT 2**: Event publisher module exists, Task model has parent_task_id, migration ready.

---

## Phase 3: User Story 5 - Infrastructure Runs on Local Kubernetes (Priority: P1) 🎯 MVP

**Goal**: All services deploy on Minikube with Dapr sidecars and pass health checks.

**Independent Test**: `kubectl get pods` shows all pods with 2/2 containers (app + daprd sidecar), `dapr status -k` shows all components running, health checks pass.

### Implementation for User Story 5

- [x] T017 [US5] Add Dapr annotations to backend deployment template in helm-chart/templates/backend-deployment.yaml: `dapr.io/enabled: "true"`, `dapr.io/app-id: "backend"`, `dapr.io/app-port: "8000"`, `dapr.io/log-level: "info"` on pod template metadata
- [x] T018 [US5] Add `DAPR_HTTP_PORT` env var to backend deployment template in helm-chart/templates/backend-deployment.yaml with value "3500"
- [x] T019 [P] [US5] Add notification service config to helm-chart/values.yaml: name, replicaCount, image (notification-service:latest), service (port 8001), resources (256Mi limit)
- [x] T020 [P] [US5] Add recurring service config to helm-chart/values.yaml: name, replicaCount, image (recurring-service:latest), service (port 8002), resources (256Mi limit)
- [x] T021 [P] [US5] Add audit service config to helm-chart/values.yaml: name, replicaCount, image (audit-service:latest), service (port 8003), resources (256Mi limit)
- [x] T022 [P] [US5] Create notification service deployment template in helm-chart/templates/notification-deployment.yaml with Dapr annotations (app-id: notification-service, app-port: 8001), DATABASE_URL env from secret, resource limits
- [x] T023 [P] [US5] Create notification service K8s service template in helm-chart/templates/notification-service.yaml (ClusterIP, port 8001)
- [x] T024 [P] [US5] Create recurring service deployment template in helm-chart/templates/recurring-deployment.yaml with Dapr annotations (app-id: recurring-service, app-port: 8002), resource limits
- [x] T025 [P] [US5] Create recurring service K8s service template in helm-chart/templates/recurring-service.yaml (ClusterIP, port 8002)
- [x] T026 [P] [US5] Create audit service deployment template in helm-chart/templates/audit-deployment.yaml with Dapr annotations (app-id: audit-service, app-port: 8003), DATABASE_URL env from secret, resource limits
- [x] T027 [P] [US5] Create audit service K8s service template in helm-chart/templates/audit-service.yaml (ClusterIP, port 8003)
- [x] T028 [US5] Update helm-chart/values-local.yaml with v4 backend tag, new service image tags (notification-service:v1, recurring-service:v1, audit-service:v1), pullPolicy Never

**CHECKPOINT 3**: Helm templates ready for all services with Dapr annotations. Values configured for local deployment.

---

## Phase 4: User Story 1 - Task Events Published to Message Broker (Priority: P1) 🎯 MVP

**Goal**: All task mutations (create, update, complete, delete) from both REST API and MCP tools publish structured events to Kafka via Dapr.

**Independent Test**: Create a task via curl, then consume from `task-events` topic using `kubectl exec redpanda-0 -- rpk topic consume task-events --num 1` and verify event contains event_type, task_id, task_data, user_id, timestamp.

### Implementation for User Story 1

- [x] T029 [US1] Add event publishing to POST /api/tasks (task create) in backend/routes/tasks.py: after successful DB commit, call `publish_event("task-events", TaskEvent(...))` and if due_date present, also publish to "reminders" topic with ReminderEvent (remind_at = due_date - 1 hour)
- [x] T030 [US1] Add event publishing to PUT /api/tasks/{id} (task update) in backend/routes/tasks.py: after successful DB commit, call `publish_event("task-events", TaskEvent(event_type="task.updated", ...))` and re-publish reminder if due_date changed
- [x] T031 [US1] Add event publishing to PUT /api/tasks/{id}/complete (task complete) in backend/routes/tasks.py: after successful DB commit, call `publish_event("task-events", TaskEvent(event_type="task.completed", ...))`
- [x] T032 [US1] Add event publishing to DELETE /api/tasks/{id} (task delete) in backend/routes/tasks.py: after successful DB commit, call `publish_event("task-events", TaskEvent(event_type="task.deleted", ...))`
- [x] T033 [US1] Add event publishing to MCP add_task tool in backend/mcp_server/tools.py: after successful DB commit, publish task.created event and reminder if due_date present
- [x] T034 [US1] Add event publishing to MCP complete_task tool in backend/mcp_server/tools.py: after successful DB commit, publish task.completed event
- [x] T035 [US1] Add event publishing to MCP delete_task tool in backend/mcp_server/tools.py: after successful DB commit, publish task.deleted event
- [x] T036 [US1] Add event publishing to MCP update_task tool in backend/mcp_server/tools.py: after successful DB commit, publish task.updated event and re-publish reminder if due_date changed
- [x] T037 [US1] Rebuild backend Docker image as v4 in minikube docker env: `docker build -t modern-taskflow-backend:v4 backend/`
- [x] T038 [US1] Deploy updated backend via `helm upgrade` and verify events appear in Kafka topics by creating/updating/completing/deleting tasks via curl and consuming from topics via rpk

**CHECKPOINT 4**: All 4 event types (created, updated, completed, deleted) appear in task-events topic. Reminders appear in reminders topic for tasks with due dates. MCP tools also publish events.

---

## Phase 5: User Story 2 - Recurring Tasks Auto-Create on Completion (Priority: P1)

**Goal**: Completing a recurring task (daily/weekly/monthly) automatically creates the next instance with the correct future due date.

**Independent Test**: Create a task with `recurring_pattern: "daily"` and due date of today, complete it, verify a new uncompleted task appears with due date of tomorrow, same title/priority/tags.

### Implementation for User Story 2

- [x] T039 [P] [US2] Create services/recurring-service/pyproject.toml with dependencies: fastapi, uvicorn, httpx
- [x] T040 [US2] Create services/recurring-service/main.py with FastAPI app: `/health` endpoint returning `{"status": "healthy", "service": "recurring-service"}`, and `/task-events` POST handler that receives CloudEvents-wrapped messages
- [x] T041 [US2] Implement task.completed event filter in services/recurring-service/main.py: extract `data` from CloudEvents envelope, check `event_type == "task.completed"` and `recurring_pattern != "none"`, ignore all other events with 200 SUCCESS
- [x] T042 [US2] Implement next-occurrence date calculation in services/recurring-service/main.py: daily (+1 day via timedelta), weekly (+7 days), monthly (+1 calendar month handling month-end edge cases using calendar.monthrange)
- [x] T043 [US2] Implement idempotent task creation in services/recurring-service/main.py: call backend API via Dapr service invocation (`POST http://localhost:3500/v1.0/invoke/backend/method/api/tasks`) to create new task with parent_task_id set, check for existing successor first
- [x] T044 [US2] Add internal service authentication support to backend: in backend/auth/dependencies.py, allow requests with `dapr-app-id` header from known internal services (recurring-service, notification-service, audit-service) to bypass Bearer token auth, using a configurable internal user_id
- [x] T045 [US2] Create services/recurring-service/Dockerfile following backend pattern (python:3.13-slim, uv, EXPOSE 8002, CMD uvicorn main:app --host 0.0.0.0 --port 8002)
- [x] T046 [US2] Build recurring service Docker image in minikube docker env: `docker build -t recurring-service:v1 services/recurring-service/`
- [x] T047 [US2] Deploy recurring service via `helm upgrade` and test: complete a daily recurring task, verify new task created with +1 day due date within 5 seconds

**CHECKPOINT 5**: Completing a daily/weekly/monthly recurring task auto-creates next instance. Non-recurring tasks ignored. Duplicate events handled idempotently.

---

## Phase 6: User Story 3 - Task Reminders Before Due Date (Priority: P2)

**Goal**: When a task has a due date, the notification service logs a reminder 1 hour before the deadline.

**Independent Test**: Create a task with a due date 2 minutes in the future, check notification service pod logs for reminder output.

### Implementation for User Story 3

- [x] T048 [P] [US3] Create services/notification-service/pyproject.toml with dependencies: fastapi, uvicorn, httpx
- [x] T049 [US3] Create services/notification-service/main.py with FastAPI app: `/health` endpoint returning `{"status": "healthy", "service": "notification-service"}`, and `/reminders` POST handler that receives CloudEvents-wrapped reminder events
- [x] T050 [US3] Implement reminder processing in services/notification-service/main.py: extract ReminderEvent from CloudEvents `data` field, compare `remind_at` with current time, if remind_at <= now log immediately, if remind_at > now store in-memory for periodic check
- [x] T051 [US3] Implement task-completion check in services/notification-service/main.py: before logging reminder, call backend via Dapr service invocation (`GET http://localhost:3500/v1.0/invoke/backend/method/api/tasks/{task_id}`) to check if task is already completed, skip if completed
- [x] T052 [US3] Implement structured console logging for reminders: output `"REMINDER: Task '[title]' is due at [due_at] for user [user_id]"` using Python logging with JSON format
- [x] T053 [US3] Create services/notification-service/Dockerfile following backend pattern (python:3.13-slim, uv, EXPOSE 8001, CMD uvicorn main:app --host 0.0.0.0 --port 8001)
- [x] T054 [US3] Build notification service Docker image in minikube docker env: `docker build -t notification-service:v1 services/notification-service/`
- [x] T055 [US3] Deploy notification service via `helm upgrade` and test: create task with near-future due date, check pod logs for reminder output via `kubectl logs -l app.kubernetes.io/component=notification-service`

**CHECKPOINT 6**: Notification service logs reminders for tasks approaching due dates. Completed tasks skipped.

---

## Phase 7: User Story 4 - Audit Trail for All Task Operations (Priority: P3)

**Goal**: All task mutation events are persisted to an `audit_log` table for accountability and debugging.

**Independent Test**: Perform create, update, complete, delete operations, then query `audit_log` table and verify all 4 operations recorded with correct event types.

### Implementation for User Story 4

- [x] T056 [P] [US4] Create services/audit-service/pyproject.toml with dependencies: fastapi, uvicorn, psycopg[binary], sqlmodel
- [x] T057 [US4] Create services/audit-service/main.py with FastAPI app: `/health` endpoint, database connection setup using `DATABASE_URL` env var, and `/task-events` POST handler that receives CloudEvents-wrapped task events
- [x] T058 [US4] Create AuditRecord SQLModel in services/audit-service/main.py (or separate models.py): table `audit_log` with columns id (serial PK), event_type (varchar 50), task_id (int), user_id (varchar 100), timestamp (timestamptz), data (JSONB), created_at (timestamptz default now)
- [x] T059 [US4] Implement audit persistence in services/audit-service/main.py: on receiving any task event, extract event_type, task_id, user_id, timestamp from CloudEvents data, persist to audit_log table, return 200 SUCCESS
- [x] T060 [US4] Add startup table creation in services/audit-service/main.py: on app startup, execute CREATE TABLE IF NOT EXISTS for audit_log with all indexes (task_id, user_id, event_type, timestamp) per data-model.md
- [x] T061 [US4] Create services/audit-service/Dockerfile following backend pattern (python:3.13-slim, uv, EXPOSE 8003, CMD uvicorn main:app --host 0.0.0.0 --port 8003)
- [x] T062 [US4] Build audit service Docker image in minikube docker env: `docker build -t audit-service:v1 services/audit-service/`
- [x] T063 [US4] Deploy audit service via `helm upgrade` and test: perform CRUD operations, query audit_log table to verify all events recorded

**CHECKPOINT 7**: Audit service persists all task events. Query audit_log confirms records for create, update, complete, delete.

---

## Phase 8: Integration Testing & Polish

**Purpose**: End-to-end verification of all event flows and cross-cutting concerns.

- [x] T064 Full Helm deployment ✅ All pods 2/2 confirmed: run `helm upgrade taskflow helm-chart/ -f helm-chart/values-local.yaml --set secrets...` and verify all pods show 2/2 containers via `kubectl get pods`
- [x] T065 Test task creation event flow: create task via curl with due date, verify event in `task-events` topic AND reminder in `reminders` topic via rpk consume
- [x] T066 Test recurring task flow: create daily recurring task, complete it, verify new task auto-created with +1 day due date within 5 seconds
- [x] T067 Test weekly and monthly recurrence: complete weekly task (verify +7 days), complete monthly task (verify +1 month)
- [x] T068 Test notification service: create task with near-future due date, verify reminder log in notification service pod logs
- [x] T069 Test audit trail: perform create, update, complete, delete operations, query audit_log table for all 4 event types
- [x] T070 Test MCP chatbot events: create and complete tasks via chatbot, verify events published to topics
- [x] T071 Test idempotency: verify completing same recurring task twice does not create duplicate successor
- [x] T072 Regression check: verify existing functionality (task CRUD, filters, sort, search, tags, chatbot) still works with no regressions after event publishing added
- [x] T073 Test fire-and-forget resilience: stop Redpanda pod, create a task, verify task creation succeeds (event lost but no error), check backend logs for warning

**CHECKPOINT 8**: All integration tests pass. No regressions. System fully operational.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 for Dapr/Redpanda running
- **Phase 3 (US5 - Infrastructure)**: Depends on Phase 2 for event schemas/publisher
- **Phase 4 (US1 - Event Publishing)**: Depends on Phase 2 for publisher module, Phase 1 for Dapr/Redpanda
- **Phase 5 (US2 - Recurring)**: Depends on Phase 4 (needs task.completed events published) and Phase 3 (needs Helm templates)
- **Phase 6 (US3 - Notifications)**: Depends on Phase 4 (needs reminder events published) and Phase 3 (needs Helm templates)
- **Phase 7 (US4 - Audit)**: Depends on Phase 4 (needs task events published) and Phase 3 (needs Helm templates)
- **Phase 8 (Integration)**: Depends on all previous phases

### User Story Dependencies

```text
Phase 1 (Setup) ──→ Phase 2 (Foundational) ──→ Phase 3 (US5: Helm/K8s)
                                               │
                                               ├──→ Phase 4 (US1: Backend Events)
                                               │         │
                                               │         ├──→ Phase 5 (US2: Recurring)  [P]
                                               │         ├──→ Phase 6 (US3: Notifications) [P]
                                               │         └──→ Phase 7 (US4: Audit)  [P]
                                               │                   │
                                               │                   v
                                               └──────────→ Phase 8 (Integration)
```

### Within Each User Story

- Schema/model tasks before service implementation
- Service implementation before Docker build
- Docker build before deploy and test
- Deploy before integration testing

### Parallel Opportunities

- **Phase 1**: T002 and T003 (Redpanda manifests) can run in parallel; T006-T009 (Dapr component/subscription YAMLs) can run in parallel
- **Phase 2**: T012 and T013 (event schemas and __init__) can run in parallel
- **Phase 3**: T019-T027 (all Helm templates for new services) can run in parallel
- **Phase 4**: T029-T032 (route event publishing) are sequential (same file); T033-T036 (MCP event publishing) are sequential (same file); but routes and MCP batches can run in parallel
- **Phase 5-7**: US2, US3, US4 can all run in parallel after Phase 4 is complete (different services, different directories)

---

## Parallel Example: Consumer Services (After Phase 4)

```bash
# These three user stories can be implemented simultaneously:
# Developer A: Recurring Service (US2)
Task: T039-T047 in services/recurring-service/

# Developer B: Notification Service (US3)
Task: T048-T055 in services/notification-service/

# Developer C: Audit Service (US4)
Task: T056-T063 in services/audit-service/
```

---

## Implementation Strategy

### MVP First (US5 + US1 Only)

1. Complete Phase 1: Setup (Dapr + Redpanda on Minikube)
2. Complete Phase 2: Foundational (event schemas, publisher, model change)
3. Complete Phase 3: US5 (Helm templates for all services)
4. Complete Phase 4: US1 (backend event publishing)
5. **STOP and VALIDATE**: Verify events appear in Kafka topics
6. This MVP proves the event-driven architecture works end-to-end

### Incremental Delivery

1. Setup + Foundational → Infrastructure ready
2. Add US5 + US1 → Events flowing into Kafka (MVP!)
3. Add US2 → Recurring tasks auto-create → Test independently
4. Add US3 → Reminders logging → Test independently
5. Add US4 → Audit trail → Test independently
6. Integration testing → Full system verified

---

## Summary

| Metric | Count |
|--------|-------|
| Total tasks | 73 |
| Phase 1 (Setup) | 10 |
| Phase 2 (Foundational) | 6 |
| Phase 3 (US5 - Infrastructure) | 12 |
| Phase 4 (US1 - Event Publishing) | 10 |
| Phase 5 (US2 - Recurring) | 9 |
| Phase 6 (US3 - Notifications) | 8 |
| Phase 7 (US4 - Audit) | 8 |
| Phase 8 (Integration) | 10 |
| Parallel opportunities | T002/T003, T006-T009, T012/T013, T019-T027, T039/T048/T056 (cross-story) |
| MVP scope | Phases 1-4 (US5 + US1): 38 tasks |

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- All services use Python 3.13 + FastAPI + uvicorn to match existing backend
- Event publishing is fire-and-forget: failures log warnings, don't block operations
- Dapr HTTP API used for all pub/sub and service invocation (no SDK)
- Each consumer service is standalone (~100 LOC) with its own Dockerfile
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
