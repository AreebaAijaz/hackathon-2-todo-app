# Research: Phase 5B - Event-Driven Architecture with Kafka & Dapr

**Date**: 2026-02-08
**Feature**: 002-event-driven-kafka-dapr

## TD-1: Dapr Installation on Minikube

**Decision**: Use Dapr CLI 1.16.x with `dapr init -k` for Kubernetes mode installation.

**Rationale**: Dapr CLI is already installed locally (v1.16.5). The `-k` flag initializes Dapr on the current Kubernetes context (Minikube). This installs the Dapr control plane (operator, sidecar injector, placement, sentry) into the `dapr-system` namespace.

**Alternatives considered**:
- Helm chart installation (`helm install dapr dapr/dapr`) - More control but unnecessary for local dev
- Manual YAML manifests - Too verbose, Dapr CLI handles this

**Key findings**:
- `dapr init -k` requires an active kubectl context pointing to Minikube
- Dapr system pods: `dapr-operator`, `dapr-sidecar-injector`, `dapr-placement-server`, `dapr-sentry`
- Sidecar injection uses annotations: `dapr.io/enabled: "true"`, `dapr.io/app-id`, `dapr.io/app-port`
- Minimum Minikube resources: 4GB memory, 2 CPUs (for Dapr + Redpanda + services)

## TD-2: Redpanda Deployment on Minikube

**Decision**: Deploy Redpanda as a single-node StatefulSet using minimal YAML manifests (no Helm chart for simplicity).

**Rationale**: Redpanda is Kafka-compatible but requires no Zookeeper, making it ideal for lightweight local development. A single-node deployment is sufficient. Using raw YAML keeps the setup transparent and avoids Helm chart complexity for a single-pod broker.

**Alternatives considered**:
- Apache Kafka with Zookeeper - Heavier, requires 2+ pods, more memory
- Redpanda Helm chart (`helm install redpanda redpanda/redpanda`) - Overkill for single-node, complex values
- Strimzi Kafka operator - Excessive for local dev

**Key findings**:
- Redpanda image: `docker.redpanda.com/redpandadata/redpanda:latest`
- Single-node config: `--overprovisioned --smp 1 --memory 512M --reserve-memory 0M --node-id 0 --check=false`
- Exposes port 9092 (Kafka API), 8081 (Schema Registry), 8082 (Pandaproxy)
- Topics created via: `rpk topic create task-events --brokers localhost:9092`
- Use `rpk` CLI (built into Redpanda container) for topic management

## TD-3: Dapr Pub/Sub Component for Kafka

**Decision**: Use Dapr's `pubsub.kafka` component type pointing to the Redpanda service.

**Rationale**: Dapr abstracts the Kafka protocol. Applications publish via Dapr HTTP API (`POST localhost:3500/v1.0/publish/kafka-pubsub/{topic}`) and subscribe via endpoint annotations. This decouples application code from Kafka client libraries.

**Alternatives considered**:
- Direct Kafka client (aiokafka, confluent-kafka-python) - Tighter coupling, more code, no Dapr benefits
- Dapr `pubsub.redis` - Simpler but doesn't meet Kafka requirement

**Key findings**:
- Component type: `pubsub.kafka` version `v1`
- Required metadata: `brokers` (e.g., `redpanda.default.svc.cluster.local:9092`)
- Optional: `consumerGroup`, `authRequired`, `maxMessageBytes`
- Dapr automatically handles serialization (CloudEvents envelope)
- Each consuming service needs its own consumer group for independent consumption

## TD-4: Dapr Python Integration Approach

**Decision**: Use raw Dapr HTTP API (localhost:3500) for publishing, and standard FastAPI route handlers for subscriptions. No Dapr Python SDK.

**Rationale**: The Dapr HTTP API is simpler and requires zero additional dependencies. Publishing is a single `httpx.post()` call. For subscriptions, Dapr calls a standard HTTP endpoint on the app - any FastAPI route works. The Dapr Python SDK adds complexity without meaningful benefit for our use case.

**Alternatives considered**:
- `dapr-ext-fastapi` SDK - Adds dependency, learning curve, limited docs for latest versions
- `dapr` Python SDK - More abstraction than needed for pub/sub
- Direct Kafka client - No Dapr benefits

**Key findings**:
- Publishing: `POST http://localhost:3500/v1.0/publish/{pubsub-name}/{topic}` with JSON body
- Subscribing: App exposes `GET /dapr/subscribe` returning subscription config, OR use declarative subscriptions (YAML)
- Declarative subscriptions (YAML) are preferred - no app code needed for routing
- `httpx` (already a backend dependency) is sufficient for Dapr HTTP calls
- Fire-and-forget: wrap publish in try/except, log warnings on failure

## TD-5: Subscription Model

**Decision**: Use declarative subscriptions (Kubernetes CRD `Subscription` resources) rather than programmatic subscriptions.

**Rationale**: Declarative subscriptions are defined as YAML and applied to Kubernetes. This separates routing configuration from application code. Services only need to expose the endpoint that receives messages. The routing logic is in infrastructure, not code.

**Alternatives considered**:
- Programmatic subscriptions (`GET /dapr/subscribe` endpoint) - Mixes routing with app code
- Dapr SDK subscription decorators - Requires SDK dependency

**Key findings**:
- Subscription CRD: `apiVersion: dapr.io/v2alpha1`, `kind: Subscription`
- Specifies: `pubsubname`, `topic`, `routes.default` (endpoint path), `scopes` (which app-id receives)
- Each service's Dapr sidecar only delivers messages matching its app-id scope
- Multiple services can subscribe to the same topic with different scopes

## TD-6: Idempotent Recurring Task Creation

**Decision**: Use a `parent_task_id` field on the new task to track lineage. Before creating a new recurring instance, check if one already exists for the completed task's ID.

**Rationale**: Kafka guarantees at-least-once delivery. Duplicate `task.completed` events could arrive. By checking for an existing child task, the recurring service ensures idempotency without complex deduplication infrastructure.

**Alternatives considered**:
- Kafka exactly-once semantics - Complex, overkill for this use case
- Redis-based deduplication cache - Extra infrastructure
- Database unique constraint on (parent_task_id) - Could work but parent_task_id might not be unique across re-completions

**Implementation approach**:
- Add optional `parent_task_id` field to task model (nullable, not exposed in API)
- Recurring service queries: "Does a task exist with parent_task_id = completed_task_id AND completed = false?"
- If yes, skip creation (idempotent)
- If no, create new task with parent_task_id set

## TD-7: Backend Event Publishing Architecture

**Decision**: Create an `events/publisher.py` module with a `publish_event()` helper function. Call it from route handlers and MCP tools after successful DB mutations.

**Rationale**: Centralizing event publishing in a single module ensures consistent event schema and error handling. Fire-and-forget with logging keeps the primary operation unblocked.

**Key findings**:
- Use `httpx.AsyncClient` for non-blocking HTTP calls to Dapr sidecar
- Dapr sidecar address: `http://localhost:3500` (default)
- In Kubernetes, sidecar is injected automatically; in local dev, need `dapr run` or skip publishing
- Backend should gracefully handle missing Dapr sidecar (local dev without Dapr)
- Environment variable `DAPR_HTTP_PORT` (default 3500) or `DAPR_ENABLED=true/false` flag

## TD-8: New Service Project Structure

**Decision**: Create `services/notification-service/` and `services/recurring-service/` as minimal Python projects with `main.py`, `Dockerfile`, and `pyproject.toml`.

**Rationale**: Each service is a standalone FastAPI application with minimal dependencies. They share no code with the backend. Keeping them in a `services/` directory at repo root separates them from the main backend.

**Key findings**:
- Each service needs: FastAPI, uvicorn, httpx (for Dapr/backend API calls)
- Dockerfile: Multi-stage build matching backend pattern (python:3.13-slim)
- Health endpoint at `/health` for K8s probes
- Dapr subscription endpoint receives CloudEvents-wrapped messages
- Message body is in `data` field of CloudEvent JSON
