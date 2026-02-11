---
id: 0002
title: Phase 5B Implementation Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 002-event-driven-kafka-dapr
branch: 002-event-driven-kafka-dapr
user: san
command: /sp.plan
labels: ["event-driven", "kafka", "dapr", "microservices", "plan", "architecture"]
links:
  spec: specs/002-event-driven-kafka-dapr/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-event-driven-kafka-dapr/research.md
  - specs/002-event-driven-kafka-dapr/data-model.md
  - specs/002-event-driven-kafka-dapr/contracts/api-contracts.md
  - specs/002-event-driven-kafka-dapr/quickstart.md
  - specs/002-event-driven-kafka-dapr/plan.md
tests:
  - null
---

## Prompt

/sp.plan

Phase 1: Dapr Installation - Install Dapr on Minikube cluster
Phase 2: Kafka Setup - Deploy Redpanda (Kafka-compatible) message broker
Phase 3: Dapr Components - Configure pub/sub component and subscriptions
Phase 4: Backend Event Publishing - Add event publishing to task mutations
Phase 5: Notification Service - Build reminder notification consumer
Phase 6: Recurring Task Service - Build recurring task auto-creation consumer
Phase 7: Dapr Subscriptions - Configure declarative subscriptions
Phase 8: Integration Testing - End-to-end verification of all event flows

## Response snapshot

Generated comprehensive implementation plan with 7 phases (consolidated from 8 suggested phases), 5 supporting documents, and full architecture specification:

**Research (research.md)**: 8 technology decisions covering Dapr installation (CLI init -k), Redpanda deployment (single-node StatefulSet), Dapr pub/sub component (pubsub.kafka), Python integration (raw HTTP API over SDK), subscription model (declarative CRDs), idempotency (parent_task_id), event publishing architecture (centralized module), and service project structure (standalone under services/).

**Data Model (data-model.md)**: New `parent_task_id` column on tasks table for recurring lineage, new `audit_log` table (event_type, task_id, user_id, timestamp, data JSONB), Pydantic event schemas (TaskEvent, ReminderEvent, TaskEventData).

**API Contracts (contracts/api-contracts.md)**: Dapr publish API endpoints for task-events and reminders topics, 3 service APIs (notification:8001, recurring:8002, audit:8003), Dapr component YAML (kafka-pubsub), 3 declarative subscription YAMLs, deployment annotations.

**Quickstart (quickstart.md)**: 10-step setup guide from minikube start through verification, with troubleshooting tips.

**Plan (plan.md)**: 7 implementation phases - Infrastructure Setup, Backend Event Publishing, Recurring Task Service, Notification Service, Audit Service, Helm Chart Integration, Integration Testing. Each phase has clear tasks and checkpoints.

## Outcome

- ✅ Impact: Complete architectural plan for transforming todo app into event-driven microservices
- 🧪 Tests: Manual integration testing defined in Phase 7 (6 test scenarios)
- 📁 Files: 5 new spec documents created (research.md, data-model.md, api-contracts.md, quickstart.md, plan.md)
- 🔁 Next prompts: /sp.tasks to generate task breakdown, then /sp.implement for execution
- 🧠 Reflection: Consolidated user's 8 phases into 7 logical phases. Chose Dapr HTTP API over Python SDK for simplicity. Fire-and-forget publishing keeps backend non-blocking.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generation completed successfully
- Graders run and results (PASS/FAIL): Constitution check PASS (all gates pass)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
