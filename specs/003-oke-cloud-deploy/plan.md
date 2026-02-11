# Implementation Plan: Oracle Cloud Deployment (OKE + CI/CD)

**Branch**: `003-oke-cloud-deploy` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/003-oke-cloud-deploy/spec.md`

## Summary

Deploy the full TaskFlow stack (5 services + Dapr + event-driven pipeline) to Oracle Cloud Kubernetes Engine (OKE) using Always Free tier resources. Replace local Redpanda with Redpanda Cloud Serverless (SASL_SSL). Add GitHub Actions CI/CD for automated build → push to OCIR → deploy to OKE workflow. The deployment must be publicly accessible via OCI Load Balancer at $0.00 cost.

## Technical Context

**Language/Version**: YAML (Helm/K8s manifests), Dockerfile (multi-stage), GitHub Actions YAML
**Primary Dependencies**: OKE (K8s v1.30), Dapr, Helm 3, OCI CLI, `oracle-actions/*` GitHub Actions
**Storage**: Neon PostgreSQL (external, unchanged), Redpanda Cloud Serverless (new)
**Testing**: Manual integration tests via kubectl/curl, GitHub Actions status checks
**Target Platform**: Oracle Cloud Infrastructure — OKE (Always Free), OCIR, OCI Load Balancer
**Project Type**: Infrastructure/DevOps — Helm chart modifications + CI/CD pipeline
**Performance Goals**: All pods Running 2/2 within 5 minutes; CI/CD pipeline < 10 minutes
**Constraints**: 2x VM.Standard.E2.1.Micro nodes (1 OCPU, 1GB RAM each); total ~1.4GB usable
**Scale/Scope**: 5 services, 5 Dapr sidecars, 1 Helm chart, 1 GitHub Actions workflow

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is template-only (no project-specific principles defined yet). No violations possible. Proceeding with standard best practices:

- [x] **Smallest viable change**: Only infrastructure/deployment files modified; no application logic changes
- [x] **No hardcoded secrets**: All credentials via K8s secrets and GitHub secrets
- [x] **Testable**: Each phase has explicit verification steps
- [x] **Reversible**: Can revert to Minikube deployment at any time (values.yaml unchanged)

## Project Structure

### Documentation (this feature)

```text
specs/003-oke-cloud-deploy/
├── plan.md                    # This file
├── spec.md                    # Feature specification
├── research.md                # Phase 0: Research findings (R1-R6)
├── data-model.md              # Infrastructure entities and config diff
├── quickstart.md              # Step-by-step deployment guide
├── contracts/
│   └── api-contracts.md       # CI/CD, Helm, Dapr, OCIR contracts
├── checklists/
│   └── requirements.md        # Quality checklist
└── tasks.md                   # Task breakdown (created by /sp.tasks)
```

### Source Code (new/modified files)

```text
helm-chart/
├── values.yaml                # Unchanged (Minikube defaults)
├── values-oke.yaml            # NEW: OKE overlay (OCIR images, LB, resources)
└── templates/
    ├── frontend-deployment.yaml   # MODIFIED: add imagePullSecrets
    ├── backend-deployment.yaml    # MODIFIED: add imagePullSecrets
    ├── notification-deployment.yaml # MODIFIED: add imagePullSecrets
    ├── recurring-deployment.yaml    # MODIFIED: add imagePullSecrets
    ├── audit-deployment.yaml        # MODIFIED: add imagePullSecrets
    └── secrets.yaml               # MODIFIED: add INTERNAL_SERVICE_USER_ID

k8s/
└── dapr-components/
    ├── kafka-pubsub.yaml          # Unchanged (local Redpanda)
    └── kafka-pubsub-cloud.yaml    # NEW: Redpanda Cloud with SASL_SSL

.github/
└── workflows/
    └── deploy.yml                 # NEW: CI/CD pipeline

frontend/Dockerfile               # Verify multi-stage build works for OCIR
backend/Dockerfile                 # Verify multi-stage build works for OCIR
services/*/Dockerfile              # Verify multi-stage build works for OCIR
```

**Structure Decision**: Infrastructure-only changes. No new application code. Helm chart overlay pattern (`values-oke.yaml`) keeps local and cloud configs separate. Dapr cloud component is a separate file to avoid breaking local dev.

## Implementation Plan

### Phase 1: Oracle Cloud Setup (Manual — Prerequisites)

**Goal**: OKE cluster running with 2 nodes in Ready state.

**Steps** (manual, documented in quickstart.md):
1. Verify OCI account and `hackathon-compartment` exist
2. Create OKE cluster `taskflow-oke` via OCI Console (Quick Create)
   - K8s v1.30, public endpoint, VM.Standard.E2.1.Micro, 2 nodes
3. Download kubeconfig: `oci ce cluster create-kubeconfig --cluster-id <OCID>`
4. Verify: `kubectl get nodes` → 2 nodes Ready

**Verification**: `kubectl get nodes` shows 2 nodes, both `Ready`
**Outputs**: KUBECONFIG file, OKE_CLUSTER_OCID noted

---

### Phase 2: OCIR Setup (Manual + Code)

**Goal**: OCIR accessible, imagePullSecrets working, Helm templates updated.

**Steps**:
1. Generate OCI auth token (OCI Console → User → Auth Tokens)
2. Create OCIR repositories (5 repos under `taskflow/`)
3. Create `ocir-secret` K8s secret:
   ```bash
   kubectl create secret docker-registry ocir-secret \
     --docker-server=iad.ocir.io \
     --docker-username='<NS>/<USER>' \
     --docker-password='<TOKEN>'
   ```
4. **Code change**: Add `imagePullSecrets` to all 5 deployment templates
   - Conditional on `.Values.global.imagePullSecrets` to avoid breaking Minikube
5. **Code change**: Add `global.imagePullSecrets` to `values-oke.yaml`

**Verification**: `kubectl get secret ocir-secret` exists; `docker login iad.ocir.io` succeeds
**Files modified**: `helm-chart/templates/*-deployment.yaml` (5 files), `helm-chart/values-oke.yaml` (new)

---

### Phase 3: Redpanda Cloud Setup (Manual + Code)

**Goal**: Redpanda Cloud cluster provisioned, topics created, Dapr component YAML ready.

**Steps**:
1. Create Redpanda Cloud Serverless cluster (manual via console)
2. Create 3 topics: `task-events`, `reminders`, `task-updates`
3. Create SASL API key and save credentials
4. Create `redpanda-credentials` K8s secret
5. **Code change**: Create `k8s/dapr-components/kafka-pubsub-cloud.yaml` with SASL_SSL config
   - Reference `redpanda-credentials` secret via `secretKeyRef`

**Verification**: rpk CLI can connect to Redpanda Cloud and list topics
**Files created**: `k8s/dapr-components/kafka-pubsub-cloud.yaml`

---

### Phase 4: Dapr + Secrets on OKE

**Goal**: Dapr installed on OKE, cloud kafka-pubsub component deployed, application secrets created.

**Steps**:
1. Install Dapr on OKE: `dapr init -k`
2. Verify: `dapr status -k` → all components healthy
3. Apply cloud Dapr component: `kubectl apply -f k8s/dapr-components/kafka-pubsub-cloud.yaml`
4. Create `taskflow-secrets` K8s secret with DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY, INTERNAL_SERVICE_USER_ID
5. **Code change**: Ensure Helm secrets template includes INTERNAL_SERVICE_USER_ID

**Verification**: `dapr status -k` shows healthy; `kubectl get components` shows kafka-pubsub
**Files modified**: `helm-chart/templates/secrets.yaml` (if INTERNAL_SERVICE_USER_ID missing)

---

### Phase 5: Build + Push Images to OCIR

**Goal**: All 5 Docker images built and pushed to OCIR.

**Steps**:
1. Login to OCIR: `docker login iad.ocir.io`
2. Build each image from its Dockerfile:
   - `frontend/Dockerfile` → `iad.ocir.io/<NS>/taskflow/frontend:latest`
   - `backend/Dockerfile` → `iad.ocir.io/<NS>/taskflow/backend:latest`
   - `services/notification-service/Dockerfile` → notification-service
   - `services/recurring-service/Dockerfile` → recurring-service
   - `services/audit-service/Dockerfile` → audit-service
3. Push all images to OCIR
4. Verify: `docker pull iad.ocir.io/<NS>/taskflow/frontend:latest` succeeds

**Verification**: All 5 images visible in OCI Console → OCIR; pull succeeds from OKE nodes
**Dependencies**: Phase 2 (OCIR secret), Phase 1 (cluster running)

---

### Phase 6: Deploy to OKE with Helm

**Goal**: All 5 services running on OKE with 2/2 containers, frontend accessible via LoadBalancer.

**Steps**:
1. **Code change**: Create `values-oke.yaml` with full OKE configuration:
   - OCIR image repositories and `pullPolicy: Always`
   - `global.imagePullSecrets: [ocir-secret]`
   - Frontend service type: `LoadBalancer`
   - Backend service type: `ClusterIP`
   - Reduced resource requests (25-50m CPU, 32-96Mi memory)
2. Deploy: `helm upgrade --install taskflow ./helm-chart -f helm-chart/values-oke.yaml --set ...`
3. Wait for pods: `kubectl get pods -w` → all 2/2 Running
4. Get LoadBalancer IP: `kubectl get svc` → EXTERNAL-IP
5. Update CORS_ORIGINS with LB IP if needed

**Verification**:
- `kubectl get pods` → all 5 pods Running 2/2
- `curl http://<LB_IP>:3000` → frontend HTML
- Create a task via API and verify event flow

**Files created**: `helm-chart/values-oke.yaml`
**Files modified**: All 5 deployment templates (imagePullSecrets)

---

### Phase 7: GitHub Actions CI/CD

**Goal**: Automated pipeline that builds, pushes, and deploys on push to master.

**Steps**:
1. **Code change**: Create `.github/workflows/deploy.yml`:
   - Trigger: push to master + workflow_dispatch
   - Job: build-and-deploy
   - Steps: checkout → login OCIR → build 5 images → push → configure kubectl → helm upgrade
2. Add all 16 secrets to GitHub repository settings (manual)
3. Test: push a minor change to master, verify pipeline succeeds
4. Verify: updated version is live within 10 minutes

**Verification**: GitHub Actions shows green check; updated code is live
**Files created**: `.github/workflows/deploy.yml`

---

### Phase 8: Integration Testing

**Goal**: All acceptance scenarios from spec verified on OKE.

**Tests**:
1. Frontend loads at `http://<LB_IP>:3000` — login page visible
2. Sign in → create task with priority, due date, tag → appears in list
3. Create daily recurring task → complete it → successor auto-created within 10s
4. Check audit logs: `kubectl exec` into audit-service pod and query audit_log table
5. Check notification logs: `kubectl logs -l app.kubernetes.io/component=notification-service`
6. Verify CRUD, filters, search work (regression check)
7. Check OCI billing dashboard → $0.00

**Verification**: All 7 tests pass
**Dependencies**: Phase 6 (deployment running)

---

### Phase 9: Documentation

**Goal**: All deployment knowledge captured for future reference.

**Steps**:
1. Update quickstart.md with actual values (cluster OCID, namespace, etc.)
2. Update CLAUDE.md if any new learnings
3. Commit all changes and create PR

**Files modified**: `quickstart.md`, `CLAUDE.md`

## Dependency Chain

```
Phase 1 (OKE Cluster)
  → Phase 2 (OCIR + imagePullSecrets)
    → Phase 3 (Redpanda Cloud)
      → Phase 4 (Dapr + Secrets)
        → Phase 5 (Build + Push Images)
          → Phase 6 (Deploy to OKE)
            → Phase 7 (GitHub Actions CI/CD)
              → Phase 8 (Integration Testing)
                → Phase 9 (Documentation)
```

All phases are sequential. Each depends on the previous phase's outputs.

## Risk Analysis

1. **Memory pressure on E2.1.Micro nodes**: 5 services + 5 Dapr sidecars on 2x 1GB RAM is extremely tight. *Mitigation*: Minimize resource requests (32-96Mi). *Fallback*: Switch to VM.Standard.A1.Flex (Arm, 24GB RAM) with multi-arch Docker builds.

2. **OCIR image pull failures**: Auth token expiry or misconfigured imagePullSecret. *Mitigation*: Test pull manually before Helm deploy. Auth tokens have a 30-day expiry — regenerate and update secret.

3. **Redpanda Cloud connectivity from OKE**: Firewall or DNS issues between OCI and Redpanda Cloud. *Mitigation*: Test with rpk CLI from a pod first. Redpanda Cloud uses public endpoints, should work.

## Complexity Tracking

No constitution violations. This phase adds only infrastructure/deployment files with no application logic changes.
