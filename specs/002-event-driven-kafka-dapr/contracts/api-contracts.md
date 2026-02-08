# API Contracts: Phase 5B - Event-Driven Architecture

**Date**: 2026-02-08
**Feature**: 002-event-driven-kafka-dapr

## Backend Event Publishing (Internal)

No new REST endpoints. Event publishing happens internally after existing route handlers complete.

### Dapr Publish API (Backend -> Dapr Sidecar)

**Publish Task Event**:
```
POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events
Content-Type: application/json

{
  "event_type": "task.created",
  "task_id": 42,
  "task_data": { ... },
  "user_id": "abc123",
  "timestamp": "2026-02-08T10:00:01Z"
}
```
Response: `204 No Content` (success) or `500` (broker unavailable)

**Publish Reminder Event**:
```
POST http://localhost:3500/v1.0/publish/kafka-pubsub/reminders
Content-Type: application/json

{
  "task_id": 42,
  "title": "Buy groceries",
  "due_at": "2026-02-15T12:00:00Z",
  "remind_at": "2026-02-15T11:00:00Z",
  "user_id": "abc123"
}
```
Response: `204 No Content`

---

## Notification Service API

**Base URL**: `http://notification-service:8001`
**Dapr App ID**: `notification-service`

### Health Check

```
GET /health
Response: 200 OK
{
  "status": "healthy",
  "service": "notification-service"
}
```

### Reminder Handler (Called by Dapr)

```
POST /reminders
Content-Type: application/json

{
  "id": "event-uuid",
  "source": "kafka-pubsub",
  "type": "com.dapr.event.sent",
  "specversion": "1.0",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 42,
    "title": "Buy groceries",
    "due_at": "2026-02-15T12:00:00Z",
    "remind_at": "2026-02-15T11:00:00Z",
    "user_id": "abc123"
  }
}
```
Response: `200 OK` with `{"status": "SUCCESS"}` (Dapr requires this to ACK)

---

## Recurring Task Service API

**Base URL**: `http://recurring-service:8002`
**Dapr App ID**: `recurring-service`

### Health Check

```
GET /health
Response: 200 OK
{
  "status": "healthy",
  "service": "recurring-service"
}
```

### Task Event Handler (Called by Dapr)

```
POST /task-events
Content-Type: application/json

{
  "id": "event-uuid",
  "source": "kafka-pubsub",
  "type": "com.dapr.event.sent",
  "specversion": "1.0",
  "datacontenttype": "application/json",
  "data": {
    "event_type": "task.completed",
    "task_id": 42,
    "task_data": {
      "id": 42,
      "title": "Buy groceries",
      "recurring_pattern": "weekly",
      "due_date": "2026-02-08T12:00:00Z",
      "priority": "high",
      "tags": ["shopping"],
      ...
    },
    "user_id": "abc123",
    "timestamp": "2026-02-08T10:00:01Z"
  }
}
```
Response: `200 OK` with `{"status": "SUCCESS"}`

**Behavior**:
- If `event_type != "task.completed"`: return 200 (ignore non-completion events)
- If `task_data.recurring_pattern == "none"`: return 200 (ignore non-recurring)
- Otherwise: call backend API to create next task, return 200

### Recurring Service -> Backend API (Service Invocation via Dapr)

```
POST http://localhost:3500/v1.0/invoke/backend/method/api/tasks
Content-Type: application/json
Authorization: Bearer <service-token or internal auth>

{
  "title": "Buy groceries",
  "description": "Get milk, eggs, bread",
  "priority": "high",
  "tags": ["shopping"],
  "due_date": "2026-02-15T12:00:00Z",
  "recurring_pattern": "weekly"
}
```
Response: `201 Created` with new task object

**Note**: The recurring service needs to authenticate with the backend. Options:
1. Internal service account (preferred) - backend recognizes Dapr service invocation header
2. Pass through user's auth token (complex, token may expire)
3. Add internal API key for service-to-service calls

**Decision**: Add an `X-Internal-Service` header check in the backend. When Dapr invokes service-to-service, it adds `dapr-app-id` header. Backend can trust requests from known Dapr app IDs.

---

## Audit Service API

**Base URL**: `http://audit-service:8003`
**Dapr App ID**: `audit-service`

### Health Check

```
GET /health
Response: 200 OK
{
  "status": "healthy",
  "service": "audit-service"
}
```

### Task Event Handler (Called by Dapr)

```
POST /task-events
Content-Type: application/json

{
  "id": "event-uuid",
  "source": "kafka-pubsub",
  "type": "com.dapr.event.sent",
  "specversion": "1.0",
  "datacontenttype": "application/json",
  "data": {
    "event_type": "task.created",
    "task_id": 42,
    "task_data": { ... },
    "user_id": "abc123",
    "timestamp": "2026-02-08T10:00:01Z"
  }
}
```
Response: `200 OK` with `{"status": "SUCCESS"}`

**Behavior**: Persists all events to the `audit_log` table.

---

## Dapr Component Manifests

### kafka-pubsub Component

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda.default.svc.cluster.local:9092"
    - name: authRequired
      value: "false"
    - name: maxMessageBytes
      value: "1048576"
```

### Declarative Subscriptions

**Notification Subscription**:
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: notification-reminders
  namespace: default
spec:
  pubsubname: kafka-pubsub
  topic: reminders
  routes:
    default: /reminders
  scopes:
    - notification-service
```

**Recurring Task Subscription**:
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: recurring-task-events
  namespace: default
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  routes:
    default: /task-events
  scopes:
    - recurring-service
```

**Audit Subscription**:
```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: audit-task-events
  namespace: default
spec:
  pubsubname: kafka-pubsub
  topic: task-events
  routes:
    default: /task-events
  scopes:
    - audit-service
```

---

## Kubernetes Deployment Annotations

All services with Dapr sidecars require these annotations on the pod template:

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "<service-name>"
  dapr.io/app-port: "<app-port>"
  dapr.io/log-level: "info"
```
