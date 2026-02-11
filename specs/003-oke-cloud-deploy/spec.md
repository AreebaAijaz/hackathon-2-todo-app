# Feature Specification: Oracle Cloud Deployment (OKE + CI/CD)

**Feature Branch**: `003-oke-cloud-deploy`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Phase 5C - Oracle Cloud Deployment (OKE + CI/CD) — Deploy Phase 5B to Oracle Cloud Kubernetes Engine (OKE) with public access and GitHub Actions CI/CD"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Application Accessible on Public Internet (Priority: P1)

A user navigates to the public URL (http://<public-ip>) and can use all TaskFlow features: create tasks with priority/due dates/tags, complete recurring tasks (triggering auto-creation of successors), and interact with the AI chatbot. The experience is identical to the local Minikube deployment but now publicly accessible.

**Why this priority**: Public accessibility is the fundamental goal of cloud deployment. Without it, the deployment has no user-facing value.

**Independent Test**: Open a browser to the LoadBalancer public IP, sign in, create a task with a due date and daily recurrence, complete it, and verify the successor task appears automatically. Check notification and audit service logs to confirm the full event-driven pipeline works end-to-end.

**Acceptance Scenarios**:

1. **Given** the OKE cluster is running with all services deployed, **When** a user navigates to http://<public-ip> in a browser, **Then** the TaskFlow frontend loads and displays the login page.
2. **Given** a user is authenticated, **When** they create a task with priority "high", due date tomorrow, and tag "cloud-test", **Then** the task appears in the list with correct priority badge, due date indicator, and tag pill.
3. **Given** a daily recurring task exists, **When** the user completes it, **Then** a successor task is auto-created with +1 day due date within 10 seconds.
4. **Given** a task with a due date is created, **When** the event pipeline processes it, **Then** the audit service records the event in the audit_log table and the notification service logs the reminder.

---

### User Story 2 - Cloud Infrastructure Provisioned and Healthy (Priority: P1)

The operations team provisions the OKE cluster, OCIR registry, and Redpanda Cloud cluster. All infrastructure components are running, connected, and pass health checks. Dapr is installed on OKE with the kafka-pubsub component pointing to Redpanda Cloud via SASL_SSL.

**Why this priority**: Infrastructure is a prerequisite for US1 (public access). Without a running cluster, nothing else works. Co-prioritized with US1 as a foundation.

**Independent Test**: Run `kubectl get nodes` to see 2 healthy nodes, `kubectl get pods` to see all pods with 2/2 containers (Dapr sidecar), and verify the Dapr kafka-pubsub component connects to Redpanda Cloud by publishing a test event.

**Acceptance Scenarios**:

1. **Given** the OCI compartment and VCN are configured, **When** the OKE cluster is created, **Then** `kubectl get nodes` shows 2 nodes in Ready state.
2. **Given** the OKE cluster is running, **When** Dapr is installed, **Then** `dapr status -k` shows all Dapr components healthy.
3. **Given** Redpanda Cloud serverless cluster is provisioned, **When** the Dapr kafka-pubsub component is deployed with SASL_SSL credentials, **Then** a test event published via Dapr API appears in the Redpanda Cloud topic.
4. **Given** all infrastructure is provisioned, **When** `helm upgrade` deploys the application, **Then** all pods (frontend, backend, recurring-service, notification-service, audit-service) reach Running state with 2/2 containers within 5 minutes.

---

### User Story 3 - Automated Deployment via CI/CD (Priority: P2)

A developer pushes code to the main branch on GitHub. GitHub Actions automatically builds all Docker images, pushes them to OCIR, and deploys the updated application to OKE with zero manual intervention.

**Why this priority**: CI/CD eliminates manual deployment friction and ensures consistent, repeatable deployments. Essential for ongoing development velocity but only valuable after the application is accessible (US1).

**Independent Test**: Make a minor change (e.g., update a health endpoint version string), push to main, and observe GitHub Actions build, push images to OCIR, and roll out the update on OKE. Verify the change is live by checking the health endpoint response.

**Acceptance Scenarios**:

1. **Given** a developer pushes a commit to the main branch, **When** GitHub Actions triggers, **Then** the workflow builds Docker images for frontend, backend, recurring-service, notification-service, and audit-service.
2. **Given** images are built, **When** the push step executes, **Then** all images are tagged and pushed to OCIR at `<region-key>.ocir.io/<tenancy-namespace>/taskflow/<service>:<tag>`.
3. **Given** images are pushed to OCIR, **When** the deploy step executes, **Then** Helm upgrades the release on OKE with the new image tags and all pods roll to the new version.
4. **Given** a deployment completes, **When** a user accesses the application, **Then** the updated version is live within 10 minutes of the push.

---

### User Story 4 - Zero-Cost Cloud Deployment (Priority: P2)

The entire deployment runs within Oracle Cloud's Always Free tier and Redpanda Cloud's free tier, incurring no charges to the account. Resource usage stays within free-tier limits.

**Why this priority**: Cost control is a hard constraint. If the deployment incurs charges, it must be flagged immediately. Important but ranks after functionality.

**Independent Test**: Review the OCI billing dashboard after 24 hours of operation and verify all resources show $0.00 charges. Confirm node shapes are VM.Standard.E2.1.Micro (free tier).

**Acceptance Scenarios**:

1. **Given** the OKE cluster uses VM.Standard.E2.1.Micro nodes, **When** the cluster runs for 24 hours, **Then** the OCI billing dashboard shows no charges.
2. **Given** OCIR is used for image storage, **When** images are pushed and pulled, **Then** no storage charges appear (within free-tier limits).
3. **Given** Redpanda Cloud serverless free tier is used, **When** events are published and consumed, **Then** no Redpanda charges appear.

---

### Edge Cases

- What happens when a node becomes unhealthy? Pods should reschedule to the remaining node (2-node cluster provides basic redundancy).
- What happens when Redpanda Cloud is temporarily unavailable? The fire-and-forget pattern (from Phase 5B) ensures task operations succeed with a warning logged; events are lost but the primary operation is not blocked.
- What happens when OCIR image pull fails during deployment? The deployment should report an error in GitHub Actions and the previous version continues running (Kubernetes rolling update).
- What happens when the OCI Load Balancer free-tier bandwidth is exceeded? Requests may be throttled; the application should still function but with higher latency.
- What happens when GitHub Actions secrets are misconfigured? The CI/CD pipeline fails fast with a clear error message at the authentication step.
- What happens when the Neon database is unreachable from OCI? The backend and audit service health checks fail; pods enter CrashLoopBackOff until connectivity is restored.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST deploy all 5 services (frontend, backend, recurring-service, notification-service, audit-service) to an OKE cluster with Dapr sidecars injected.
- **FR-002**: System MUST expose the frontend via an OCI Load Balancer with a public IP address accessible over HTTP.
- **FR-003**: System MUST connect to the existing Neon PostgreSQL database for both the backend and audit service.
- **FR-004**: System MUST use Redpanda Cloud (serverless) as the Kafka-compatible message broker, replacing the local Redpanda instance.
- **FR-005**: System MUST authenticate to Redpanda Cloud using SASL_SSL with credentials stored as Kubernetes secrets.
- **FR-006**: System MUST store Docker images in OCIR and pull them during deployment using an image pull secret.
- **FR-007**: System MUST provide a GitHub Actions workflow that builds all images, pushes to OCIR, and deploys to OKE on push to the main branch.
- **FR-008**: System MUST pass all Kubernetes health checks (liveness and readiness probes) for every service.
- **FR-009**: System MUST preserve all Phase 5A (advanced task features) and Phase 5B (event-driven microservices) functionality without regression.
- **FR-010**: System MUST use only Oracle Cloud Always Free tier resources (VM.Standard.E2.1.Micro nodes, free Load Balancer, free OCIR).
- **FR-011**: System MUST store sensitive configuration (database URL, API keys, Kafka credentials) as Kubernetes secrets, never in source code or Helm values files.
- **FR-012**: System MUST configure the frontend to use the correct backend URL for API calls in the cloud environment.
- **FR-013**: System MUST install Dapr on the OKE cluster and configure the kafka-pubsub component with Redpanda Cloud connection details (SASL_SSL).

### Key Entities

- **OKE Cluster**: 2-node Kubernetes cluster in Oracle Cloud (compartment: hackathon-compartment, name: taskflow-oke, K8s v1.30, region: us-ashburn-1). Nodes use VM.Standard.E2.1.Micro shape (1 OCPU, 1GB RAM each — Always Free).
- **OCIR Registry**: Container image registry at `<region-key>.ocir.io/<tenancy-namespace>/taskflow/` holding 5 service images (frontend, backend, notification-service, recurring-service, audit-service).
- **Redpanda Cloud Cluster**: Serverless Kafka-compatible broker with 3 topics (task-events, reminders, task-updates) and SASL_SSL authentication.
- **GitHub Actions Workflow**: CI/CD pipeline file (`.github/workflows/deploy.yml`) triggered on push to main, with build, push, and deploy stages.
- **Kubernetes Secrets**: Encrypted configuration for DATABASE_URL, OPENAI_API_KEY, BETTER_AUTH_SECRET, INTERNAL_SERVICE_USER_ID, Redpanda SASL credentials, and OCIR image pull secret.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 5 application services reach Running state with 2/2 containers (Dapr sidecar) on OKE within 5 minutes of deployment.
- **SC-002**: The application is accessible via public IP — a user can load the page, sign in, and create a task within 60 seconds of first visit.
- **SC-003**: End-to-end event flow works on OKE: completing a daily recurring task auto-creates a successor within 10 seconds.
- **SC-004**: A code push to the main branch triggers GitHub Actions and results in a live deployment within 10 minutes.
- **SC-005**: The OCI billing dashboard shows $0.00 charges after 48 hours of continuous operation.
- **SC-006**: All Phase 5A features (priority, due dates, tags, recurring patterns, filters, search) and Phase 5B features (event publishing, recurring auto-creation, notifications, audit trail) work without regression on OKE.

## Assumptions

- The user already has an Oracle Cloud account with Always Free tier access and the `hackathon-compartment` compartment created.
- OCI CLI is configured locally or the user can configure it during implementation.
- The GitHub repository (`AreebaAijaz/hackathon-2-todo-app`) has GitHub Actions enabled and the user can add repository secrets.
- Redpanda Cloud offers a serverless free tier with SASL_SSL authentication (the user will create the cluster manually via the Redpanda Cloud console).
- The Neon PostgreSQL database is externally accessible from OCI (no VPN/peering required).
- Dapr can be installed on OKE via the standard `dapr init -k` method.
- The frontend's NEXT_PUBLIC_API_URL will be updated to point to the backend's public or cluster-internal URL.
- The audit-service image is also deployed to OCIR (5 images total, not 4 as initially stated).

## Constraints

- **Hard constraint**: All OCI resources must stay within Always Free tier — no paid resources.
- **Hard constraint**: No secrets in source code or Helm values files checked into git.
- **Dependency**: Requires Phase 5A+5B branch to be merged to main before CI/CD can deploy the full stack.
- **Dependency**: Redpanda Cloud cluster must be provisioned manually before Dapr component can connect.
- **Dependency**: OCI auth tokens for OCIR must be generated manually and stored as GitHub secrets.

## Non-Goals

- Custom domain name or HTTPS/TLS termination (HTTP-only for this phase).
- Horizontal pod autoscaling or advanced scaling policies.
- Monitoring, alerting, or observability dashboards (Dapr log-level info is sufficient).
- Multi-region or high-availability deployment.
- Database migration from Neon to OCI Autonomous Database.
- Production-grade security hardening (network policies, pod security standards).
