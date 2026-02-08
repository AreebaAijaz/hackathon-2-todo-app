# Feature Specification: Phase 5B - Event-Driven Architecture with Kafka & Dapr

**Feature Branch**: `002-event-driven-kafka-dapr`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Transform todo app into event-driven microservices system using Kafka for messaging and Dapr for infrastructure abstraction on local Minikube"
**Builds On**: Phase 5A (Advanced Task Features) - tasks have priorities, tags, due dates, recurring patterns

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Events Published to Message Broker (Priority: P1)

When a user creates, updates, completes, or deletes a task through either the web interface or the AI chatbot, the system publishes a structured event to a message broker. This is the foundational capability that all other event-driven services depend on.

**Why this priority**: Without event publishing, no downstream services can react to task mutations. This is the core infrastructure that enables the entire event-driven architecture.

**Independent Test**: Create a task via the API or chatbot, then verify the event appears in the message broker topic. Can be validated using broker CLI tools to consume and inspect the published message.

**Acceptance Scenarios**:

1. **Given** a user creates a task with title "Buy groceries", **When** the task is saved to the database, **Then** a `task.created` event is published to the `task-events` topic containing the task ID, full task data, user ID, and timestamp.
2. **Given** a user marks a task as completed, **When** the completion is persisted, **Then** a `task.completed` event is published to the `task-events` topic.
3. **Given** a user updates a task's priority or tags, **When** the update is saved, **Then** a `task.updated` event is published to the `task-events` topic.
4. **Given** a user deletes a task, **When** the deletion occurs, **Then** a `task.deleted` event is published to the `task-events` topic.
5. **Given** the AI chatbot creates a task via natural language, **When** the MCP tool executes, **Then** the same events are published as when using the direct API.
6. **Given** the message broker is temporarily unavailable, **When** a task mutation occurs, **Then** the task operation still succeeds (fire-and-forget), and a warning is logged.

---

### User Story 2 - Recurring Tasks Auto-Create on Completion (Priority: P1)

When a user completes a task that has a recurring pattern (daily, weekly, or monthly), the system automatically creates the next instance of that task with the appropriate future due date. The user sees the new task appear in their task list without manual intervention.

**Why this priority**: Recurring task auto-creation is a core user-facing feature that directly improves the user experience. Phase 5A added the recurring pattern field but completing a recurring task did not create the next instance. This story delivers that missing capability.

**Independent Test**: Create a task with `recurring_pattern: "daily"` and a due date of today, complete it, then verify a new uncompleted task appears with the same title, priority, and tags but with a due date of tomorrow.

**Acceptance Scenarios**:

1. **Given** a task with `recurring_pattern: "daily"` and due date of Feb 8, **When** the user completes the task, **Then** a new uncompleted task is created with the same title, description, priority, and tags, with due date of Feb 9.
2. **Given** a task with `recurring_pattern: "weekly"` and due date of Feb 8 (Saturday), **When** the user completes the task, **Then** a new task is created with due date of Feb 15 (next Saturday).
3. **Given** a task with `recurring_pattern: "monthly"` and due date of Feb 8, **When** the user completes the task, **Then** a new task is created with due date of Mar 8.
4. **Given** a task with `recurring_pattern: "none"`, **When** the user completes it, **Then** no new task is created.
5. **Given** a recurring task with no due date set, **When** the user completes it, **Then** a new task is created with due date calculated from the current date.

---

### User Story 3 - Task Reminders Before Due Date (Priority: P2)

When a user sets a due date on a task, the system schedules a reminder for 1 hour before the deadline. When the reminder time arrives, the system logs the reminder (console output for this phase; email/push notifications are deferred to a future phase).

**Why this priority**: Reminders add value by proactively alerting users about upcoming deadlines, but the system already shows overdue indicators in the UI. This extends the existing capability with proactive notification.

**Independent Test**: Create a task with a due date 2 minutes in the future, wait for the reminder time to pass, then check service logs for the reminder output.

**Acceptance Scenarios**:

1. **Given** a task is created with due date of tomorrow at 2:00 PM, **When** the task is saved, **Then** a reminder event is scheduled for tomorrow at 1:00 PM (1 hour before).
2. **Given** a reminder is scheduled for 1:00 PM, **When** the current time reaches 1:00 PM, **Then** the notification service outputs a console log: "REMINDER: Task '[title]' is due at 2:00 PM for user [user_id]".
3. **Given** a task's due date is updated to a new time, **When** the update is saved, **Then** a new reminder event is published with the updated remind-at time.
4. **Given** a task has no due date, **When** it is created or updated, **Then** no reminder event is published.
5. **Given** a task is completed before the reminder time, **When** the reminder fires, **Then** the notification service checks task status and skips the reminder if already completed.

---

### User Story 4 - Audit Trail for All Task Operations (Priority: P3)

All task mutations (create, update, complete, delete) are logged to a persistent audit trail. This provides a history of all changes for accountability and debugging.

**Why this priority**: Audit logging is valuable for debugging and compliance but does not directly affect the user experience. It is an operational concern that can be added after the core event-driven flows are working.

**Independent Test**: Perform several task operations (create, update, complete, delete), then query the audit log and verify all operations are recorded with correct event types, timestamps, and task data.

**Acceptance Scenarios**:

1. **Given** any task mutation event is published, **When** the audit service receives it, **Then** it stores an audit record with event_type, task_id, user_id, timestamp, and event data.
2. **Given** 10 task operations have been performed, **When** querying the audit log, **Then** all 10 operations appear in chronological order.
3. **Given** the audit service restarts, **When** it reconnects, **Then** it resumes consuming events from where it left off (no lost events).

---

### User Story 5 - Infrastructure Runs on Local Kubernetes (Priority: P1)

The entire event-driven system (message broker, infrastructure runtime, all microservices) runs on the local Minikube cluster. A developer can start the system with a few commands and verify all services are healthy.

**Why this priority**: Without the infrastructure running, no event-driven features can work. This is a prerequisite for all other stories.

**Independent Test**: Run the installation commands, then verify all pods are running, sidecars are healthy, and message broker topics exist.

**Acceptance Scenarios**:

1. **Given** a running Minikube cluster, **When** the infrastructure runtime is installed, **Then** its control plane pods are all healthy.
2. **Given** the infrastructure runtime is installed, **When** the message broker is deployed, **Then** it is accessible on its internal port and topics can be listed.
3. **Given** all infrastructure is deployed, **When** application services are deployed, **Then** each service pod has a running sidecar container alongside the main application container.
4. **Given** all services are deployed, **When** running a status check, **Then** all components report healthy.

---

### Edge Cases

- What happens when the message broker is down when an event is published? The task operation succeeds but the event is lost (fire-and-forget with logging). No user-facing error.
- What happens when the recurring task service receives a completion event for a non-recurring task? It checks the recurring_pattern field and silently ignores non-recurring tasks.
- What happens when the recurring task service fails to create the next task instance? It logs the error. The user can manually create the task. No retry loop to avoid duplicates.
- What happens when a task with monthly recurrence has a due date on the 31st? The next occurrence uses the last day of the next month if that month has fewer days.
- What happens when multiple completion events arrive for the same task (duplicate messages)? The recurring service checks if a successor task already exists before creating a new one (idempotent).
- What happens if the message broker runs out of disk space? The broker will reject new messages. Task operations still succeed. Events are lost until broker recovers.
- What happens if a service sidecar fails to start? The service container also fails health checks. Kubernetes restarts the pod.

## Requirements *(mandatory)*

### Functional Requirements

#### Event Publishing (Backend)
- **FR-001**: System MUST publish a structured event to the `task-events` topic when a task is created, containing event_type, task_id, task_data, user_id, and timestamp.
- **FR-002**: System MUST publish a structured event to the `task-events` topic when a task is updated (any field change).
- **FR-003**: System MUST publish a structured event to the `task-events` topic when a task is completed.
- **FR-004**: System MUST publish a structured event to the `task-events` topic when a task is deleted.
- **FR-005**: System MUST publish a `reminder.scheduled` event to the `reminders` topic when a task with a due date is created or updated, with remind_at set to 1 hour before the due date.
- **FR-006**: System MUST publish events from both REST API routes and MCP tool mutations.
- **FR-007**: Event publishing MUST be fire-and-forget; failures MUST NOT block the primary task operation.
- **FR-008**: System MUST log a warning when event publishing fails.

#### Recurring Task Service
- **FR-009**: Recurring task service MUST consume `task.completed` events from the `task-events` topic.
- **FR-010**: Recurring task service MUST create a new task when a completed task has `recurring_pattern` other than "none".
- **FR-011**: The new recurring task instance MUST copy title, description, priority, tags, and recurring_pattern from the completed task.
- **FR-012**: The new recurring task instance MUST calculate the next due date: daily (+1 day), weekly (+7 days), monthly (+1 calendar month).
- **FR-013**: If the completed task had no due date, the new task's due date MUST be calculated from the current date.
- **FR-014**: Recurring task creation MUST be idempotent; if a successor task already exists for the same parent, no duplicate is created.

#### Notification Service
- **FR-015**: Notification service MUST consume events from the `reminders` topic.
- **FR-016**: Notification service MUST output a console log when a reminder's scheduled time is reached, including task title, due date, and user ID.
- **FR-017**: Notification service MUST check whether the task is already completed before sending a reminder; if completed, skip the reminder silently.

#### Audit Service
- **FR-018**: Audit service MUST consume all events from the `task-events` topic.
- **FR-019**: Audit service MUST persist each event as an audit record with event_type, task_id, user_id, timestamp, and full event data.
- **FR-020**: Audit service MUST provide a health check endpoint.

#### Infrastructure
- **FR-021**: A single-node Kafka-compatible message broker MUST run on Minikube with three topics: `task-events` (3 partitions), `reminders` (1 partition), `task-updates` (3 partitions).
- **FR-022**: An infrastructure abstraction runtime MUST be installed on Minikube providing pub/sub, state management, service invocation, and secrets building blocks.
- **FR-023**: All application services MUST be annotated for sidecar injection with unique app IDs and correct app ports.
- **FR-024**: Pub/sub subscriptions MUST route `reminders` topic to the notification service and `task-events` topic to both the recurring task service and audit service.
- **FR-025**: Each new microservice MUST include a health check endpoint at `/health`.

### Key Entities

- **TaskEvent**: Represents a domain event for task mutations. Attributes: event_type (created/updated/completed/deleted), task_id, task_data (full task snapshot), user_id, timestamp.
- **ReminderEvent**: Represents a scheduled reminder. Attributes: task_id, title, due_at, remind_at, user_id.
- **AuditRecord**: A persisted log entry for a task operation. Attributes: id, event_type, task_id, user_id, timestamp, data (JSON).
- **Pub/Sub Component**: Infrastructure configuration connecting services to the message broker.
- **Subscription**: Routing rule that delivers topic messages to specific service endpoints.

## Scope

### In Scope
- Event publishing from the existing backend (REST routes + MCP tools)
- Redpanda (Kafka-compatible) single-node broker on Minikube
- Dapr runtime on Minikube with pub/sub, state, service invocation, secrets
- Notification service (console logging only)
- Recurring task service (auto-create next task instance)
- Audit service (persist event log)
- Helm chart updates for all new deployments
- Dapr component and subscription manifests

### Out of Scope
- Actual email or push notifications (console log only for now)
- Real-time WebSocket sync to frontend
- Cloud deployment (Minikube only)
- CI/CD pipeline
- Frontend changes (no UI changes in this phase)
- Multi-node or production-grade broker configuration
- Message retry/dead-letter queues (fire-and-forget for now)

## Assumptions

- Minikube is available and running with sufficient resources (4GB+ RAM, 2+ CPUs recommended)
- Docker Desktop is running (required for minikube with Docker driver)
- Helm 3 is installed
- The Dapr CLI is installed locally (for `dapr init -k`)
- The existing backend at v3 (Phase 5A) is the starting point
- Redpanda is chosen over Apache Kafka for lightweight local development (no Zookeeper, single binary)
- Fire-and-forget event publishing is acceptable; eventual consistency is fine for this phase
- Console logging is sufficient for the notification service (email integration is a future phase)
- The recurring task service calls back to the backend API to create tasks (not direct DB access)
- All new microservices use Python 3.13 + FastAPI to match the existing backend stack
- Dapr sidecar handles message serialization/deserialization

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All infrastructure components (broker, runtime, sidecars) are healthy within 5 minutes of deployment commands completing.
- **SC-002**: Creating a task with a due date results in both a `task.created` event and a `reminder.scheduled` event appearing in their respective topics within 2 seconds.
- **SC-003**: Completing a recurring task results in a new task instance appearing in the user's task list within 5 seconds.
- **SC-004**: The new recurring task has the correct next due date (daily: +1 day, weekly: +7 days, monthly: +1 calendar month).
- **SC-005**: 100% of task mutations (create, update, complete, delete) from both REST API and chatbot produce corresponding events.
- **SC-006**: Notification service logs a reminder message for tasks with due dates.
- **SC-007**: Audit service records all task events with no data loss during normal operation.
- **SC-008**: All services (backend, notification, recurring, audit) have running sidecars and pass health checks.
- **SC-009**: The entire system runs on a single Minikube cluster without requiring external cloud services (except the existing Neon database).
- **SC-010**: Existing functionality (task CRUD, chatbot, priority, tags, due dates) continues to work with no regressions after event publishing is added.
