# Tasks: Oracle Cloud Deployment (OKE + CI/CD)

**Input**: Design documents from `specs/003-oke-cloud-deploy/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not requested. Integration verification is included as manual checkpoint tasks.

**Organization**: Tasks follow the user's 9-phase sequential deployment pipeline. User stories are mapped:
- **US2** (Infrastructure, P1): Phases 1–4 — provisioning OKE, OCIR, Redpanda Cloud, Dapr + Secrets
- **US1** (Public Access, P1): Phases 5–6 — build images, deploy, expose via LoadBalancer
- **US3** (CI/CD, P2): Phase 7 — GitHub Actions workflow
- **US4** (Zero-Cost, P2): Verified as part of Phase 8 integration testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Exact file paths included where code changes are needed

---

## Phase 1: Oracle Cloud Setup (US2 — Infrastructure)

**Goal**: OKE cluster running with 2 healthy nodes, kubectl connected

**Independent Test**: `kubectl get nodes` shows 2 nodes in Ready state

- [x] T001 [US2] Verify OCI account access and `hackathon-compartment` compartment exists in OCI Console
- [x] T002 [US2] Create OKE cluster `taskflow-oke` via OCI Console Quick Create — K8s v1.30, public endpoint, VM.Standard.E2.1.Micro shape, 2 nodes in `hackathon-compartment`
- [x] T003 [US2] Install OCI CLI and configure with `oci setup config` — set region to ap-mumbai-1
- [x] T004 [US2] Download kubeconfig via `oci ce cluster create-kubeconfig --cluster-id <CLUSTER_OCID> --region ap-mumbai-1 --token-version 2.0.0` and verify `kubectl get nodes` shows 3 Ready nodes

**CHECKPOINT 1**: OKE cluster ready — `kubectl get nodes` returns 2 nodes in Ready state

---

## Phase 2: OCIR Setup (US2 — Infrastructure)

**Goal**: Container registry authenticated, image pull secret created, Helm templates updated with imagePullSecrets

**Independent Test**: `kubectl get secret ocir-secret` exists; `docker login iad.ocir.io` succeeds

- [x] T005 [US2] Generate OCI auth token via OCI CLI and login to OCIR
- [x] T006 [US2] Create `ocir-secret` Kubernetes secret in OKE cluster
- [x] T007 [P] [US2] Add conditional imagePullSecrets to `helm-chart/templates/frontend-deployment.yaml` — add `{{- with .Values.global.imagePullSecrets }}imagePullSecrets: {{- toYaml . | nindent 8 }}{{- end }}` in pod spec before `containers:`
- [x] T008 [P] [US2] Add conditional imagePullSecrets to `helm-chart/templates/backend-deployment.yaml` — same pattern as T007
- [x] T009 [P] [US2] Add conditional imagePullSecrets to `helm-chart/templates/notification-deployment.yaml` — same pattern as T007
- [x] T010 [P] [US2] Add conditional imagePullSecrets to `helm-chart/templates/recurring-deployment.yaml` — same pattern as T007
- [x] T011 [P] [US2] Add conditional imagePullSecrets to `helm-chart/templates/audit-deployment.yaml` — same pattern as T007

**CHECKPOINT 2**: Container registry ready — OCIR secret exists, all 5 deployment templates have imagePullSecrets

---

## Phase 3: Redpanda Cloud (US2 — Infrastructure)

**Goal**: Redpanda Cloud Serverless cluster provisioned with 3 topics and SASL credentials verified

**Independent Test**: rpk CLI or Redpanda Cloud console confirms topics `task-events`, `reminders`, `task-updates` exist and credentials work

- [x] T012 [US2] Create Redpanda Cloud Serverless cluster at cloud.redpanda.com — note bootstrap server URL
- [x] T013 [US2] Create 3 topics in Redpanda Cloud console: `task-events`, `reminders`, `task-updates`
- [x] T014 [US2] Create SASL API key in Redpanda Cloud (Security → API Keys) — save username and password; test connection with rpk CLI or Redpanda Cloud console

**CHECKPOINT 3**: Kafka cloud ready — 3 topics exist, SASL credentials verified

---

## Phase 4: Dapr + Secrets (US2 — Infrastructure)

**Goal**: Dapr installed on OKE, cloud kafka-pubsub component deployed with SASL_SSL, application secrets created

**Independent Test**: `dapr status -k` shows healthy; `kubectl get components` shows kafka-pubsub; `kubectl get secret taskflow-secrets` exists

- [x] T015 [US2] Install Dapr on OKE via `dapr init -k` and verify with `dapr status -k` — all components must show healthy
- [x] T016 [US2] Create `k8s/dapr-components/kafka-pubsub-cloud.yaml` with Redpanda Cloud SASL_SSL configuration — brokers from T012, secretKeyRef to `redpanda-credentials` for saslUsername/saslPassword, saslMechanism: SCRAM-SHA-256, authType: password (see contracts/api-contracts.md Contract 3)
- [x] T017 [US2] Create `redpanda-credentials` K8s secret via `kubectl create secret generic redpanda-credentials --from-literal=username='<SASL_USER>' --from-literal=password='<SASL_PASS>'`
- [x] T018 [US2] Apply cloud Dapr component: `kubectl apply -f k8s/dapr-components/kafka-pubsub-cloud.yaml`
- [x] T019 [US2] Create `taskflow-secrets` K8s secret via `kubectl create secret generic taskflow-secrets --from-literal=DATABASE_URL='<NEON_URL>' --from-literal=BETTER_AUTH_SECRET='<SECRET>' --from-literal=OPENAI_API_KEY='<KEY>' --from-literal=INTERNAL_SERVICE_USER_ID='<UUID>'`
- [x] T020 [US2] Add INTERNAL_SERVICE_USER_ID to `helm-chart/templates/secrets.yaml` — add line `INTERNAL_SERVICE_USER_ID: {{ .Values.secrets.internalServiceUserId | b64enc | quote }}` and add `internalServiceUserId: ""` default to `helm-chart/values.yaml` under secrets

**CHECKPOINT 4**: Dapr + Secrets configured — Dapr healthy, kafka-pubsub component deployed, all K8s secrets created

---

## Phase 5: Build and Push Images (US1 — Public Access)

**Goal**: All 5 Docker images built and pushed to OCIR

**Independent Test**: `docker pull iad.ocir.io/<NS>/taskflow/<service>:latest` succeeds for all 5 services

- [x] T021 [P] [US1] Build frontend image: `docker build -t iad.ocir.io/<NS>/taskflow/frontend:latest ./frontend/`
- [x] T022 [P] [US1] Build backend image: `docker build -t iad.ocir.io/<NS>/taskflow/backend:latest ./backend/`
- [x] T023 [P] [US1] Build notification-service image: `docker build -t iad.ocir.io/<NS>/taskflow/notification-service:latest ./services/notification-service/`
- [x] T024 [P] [US1] Build recurring-service image: `docker build -t iad.ocir.io/<NS>/taskflow/recurring-service:latest ./services/recurring-service/`
- [x] T025 [P] [US1] Build audit-service image: `docker build -t iad.ocir.io/<NS>/taskflow/audit-service:latest ./services/audit-service/`
- [x] T026 [US1] Push all 5 images to OCIR via `docker push iad.ocir.io/<NS>/taskflow/<service>:latest` — verify images visible in OCI Console → OCIR

**CHECKPOINT 5**: Images in OCIR — all 5 images pushed and pullable

---

## Phase 6: Deploy to OKE (US1 — Public Access)

**Goal**: All 5 services running on OKE with 2/2 containers (Dapr sidecar), frontend accessible via LoadBalancer public IP

**Independent Test**: `kubectl get pods` shows all 5 pods Running 2/2; `curl http://<LB_IP>:3000` returns frontend HTML

- [x] T027 [US1] Create `helm-chart/values-oke.yaml` with OKE overlay — OCIR image repos, pullPolicy: Always, global.imagePullSecrets: [ocir-secret], frontend service type LoadBalancer, backend service type ClusterIP, reduced resources per R6 (see contracts/api-contracts.md Contract 2 for full schema)
- [x] T028 [US1] Deploy to OKE via `helm upgrade --install taskflow ./helm-chart -f helm-chart/values-oke.yaml --set secrets.databaseUrl='<URL>' --set secrets.betterAuthSecret='<SECRET>' --set secrets.openaiApiKey='<KEY>' --set secrets.internalServiceUserId='<UUID>' --set backend.env.CORS_ORIGINS='http://<LB_IP>'`
- [x] T029 [US1] Wait for all pods to reach Running 2/2 state: `kubectl get pods -w` — should complete within 5 minutes (SC-001); troubleshoot ImagePullBackOff (ocir-secret), CrashLoopBackOff (secrets/DB), or OOMKilled (resource limits)
- [x] T030 [US1] Get LoadBalancer public IP via `kubectl get svc -l app.kubernetes.io/component=frontend` — wait for EXTERNAL-IP (2-5 minutes); open `http://<EXTERNAL-IP>:3000` in browser to confirm frontend loads (SC-002)
- [x] T031 [US1] Update CORS_ORIGINS with actual LB IP if needed: `helm upgrade taskflow ./helm-chart -f helm-chart/values-oke.yaml --set backend.env.CORS_ORIGINS='http://<ACTUAL_LB_IP>' --reuse-values`

**CHECKPOINT 6**: Live on Oracle Cloud — all pods 2/2, frontend accessible via public IP

---

## Phase 7: GitHub Actions CI/CD (US3 — Automated Deployment)

**Goal**: Automated pipeline that builds, pushes, and deploys on push to master

**Independent Test**: Push a minor change to master, observe GitHub Actions build/push/deploy, verify updated version is live within 10 minutes (SC-004)

- [x] T032 [US3] Create `.github/workflows/deploy.yml` with CI/CD pipeline — trigger on push to master + workflow_dispatch; steps: checkout, login OCIR via `oracle-actions/login-ocir@v1`, build 5 images tagged with `github.sha`, push to OCIR, configure kubectl via `oci ce cluster create-kubeconfig`, helm upgrade with new image tags (see contracts/api-contracts.md Contract 1 for full workflow spec)
- [x] T033 [US3] Add all 16 GitHub Actions secrets to repository settings (OCI_CLI_USER, OCI_CLI_TENANCY, OCI_CLI_FINGERPRINT, OCI_CLI_KEY_CONTENT, OCI_CLI_REGION, OKE_CLUSTER_OCID, OCIR_NAMESPACE, OCIR_USERNAME, OCIR_TOKEN, DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY, INTERNAL_SERVICE_USER_ID, REDPANDA_BROKERS, REDPANDA_USERNAME, REDPANDA_PASSWORD) — see data-model.md GitHub Actions Secrets table
- [x] T034 [US3] Test CI/CD by pushing a minor change (e.g., update health endpoint version) to master — verify GitHub Actions succeeds, new images appear in OCIR with git SHA tag, pods roll to new version, change is live

**CHECKPOINT 7**: CI/CD active — push to master triggers automated build + deploy

---

## Phase 8: Integration Testing (US1 + US4 — Verification)

**Goal**: All acceptance scenarios verified on OKE deployment

**Independent Test**: End-to-end user journey works; event-driven pipeline flows; $0.00 billing

- [x] T035 [US1] Verify frontend loads at `http://<LB_IP>:3000` — sign in, create a task with priority "high", due date tomorrow, tag "cloud-test" → task appears with correct badges (SC-002, SC-006)
- [x] T036 [US1] Verify recurring task flow — create daily recurring task, complete it, verify successor auto-created with +1 day due date within 10 seconds (SC-003)
- [x] T037 [US1] Verify audit trail — check audit-service logs via `kubectl logs -l app.kubernetes.io/component=audit-service` for event processing; query audit_log table via backend API
- [x] T038 [US1] Verify notification service — check `kubectl logs -l app.kubernetes.io/component=notification-service` for reminder processing on tasks with due dates
- [x] T039 [US1] Regression check — verify CRUD operations, filters, search, tags all work correctly on OKE (SC-006)
- [x] T040 [US4] Verify zero-cost deployment — check OCI billing dashboard shows $0.00 charges; confirm node shapes are VM.Standard.E2.1.Micro (SC-005)

**CHECKPOINT 8**: Fully tested — all features work on OKE, event pipeline flows, $0.00 cost

---

## Phase 9: Documentation & Delivery

**Goal**: All deployment knowledge captured, changes committed

- [x] T041 Update `specs/003-oke-cloud-deploy/quickstart.md` with actual values — cluster OCID, tenancy namespace, Redpanda broker URL, LoadBalancer IP
- [x] T042 Update `CLAUDE.md` with any new learnings from deployment
- [x] T043 Commit all changes and create PR for 003-oke-cloud-deploy branch

**CHECKPOINT 9**: Phase 5C delivered

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (OKE Setup — T001-T004)
  → Phase 2 (OCIR — T005-T011)
    → Phase 3 (Redpanda Cloud — T012-T014)
      → Phase 4 (Dapr + Secrets — T015-T020)
        → Phase 5 (Build Images — T021-T026)
          → Phase 6 (Deploy — T027-T031)
            → Phase 7 (CI/CD — T032-T034)
              → Phase 8 (Testing — T035-T040)
                → Phase 9 (Docs — T041-T043)
```

All phases are sequential. Each depends on the previous phase's outputs.

### User Story Dependencies

- **US2 (Infrastructure, P1)**: Phases 1–4 — must complete first (foundation for everything)
- **US1 (Public Access, P1)**: Phases 5–6 — depends on US2 completion
- **US3 (CI/CD, P2)**: Phase 7 — depends on US1 (needs working deployment to validate)
- **US4 (Zero-Cost, P2)**: Phase 8 — cross-cutting verification, depends on US1+US2

### Parallel Opportunities

**Within Phase 2** (T007-T011): All 5 deployment template edits can run in parallel — different files, same pattern.

**Within Phase 5** (T021-T025): All 5 Docker image builds can run in parallel — independent Dockerfiles.

**Within Phase 8** (T035-T040): Integration tests are independent and can run in parallel after deployment is live.

---

## Parallel Example: Phase 2

```bash
# All 5 imagePullSecrets edits in parallel (different files):
Task T007: "Add imagePullSecrets to helm-chart/templates/frontend-deployment.yaml"
Task T008: "Add imagePullSecrets to helm-chart/templates/backend-deployment.yaml"
Task T009: "Add imagePullSecrets to helm-chart/templates/notification-deployment.yaml"
Task T010: "Add imagePullSecrets to helm-chart/templates/recurring-deployment.yaml"
Task T011: "Add imagePullSecrets to helm-chart/templates/audit-deployment.yaml"
```

## Parallel Example: Phase 5

```bash
# All 5 Docker image builds in parallel:
Task T021: "Build frontend image"
Task T022: "Build backend image"
Task T023: "Build notification-service image"
Task T024: "Build recurring-service image"
Task T025: "Build audit-service image"
```

---

## Implementation Strategy

### MVP First (US2 + US1 — Phases 1–6)

1. Complete Phases 1–4: Infrastructure provisioning (US2)
2. Complete Phases 5–6: Build, push, deploy (US1)
3. **STOP and VALIDATE**: Application accessible via public IP, all features work
4. This is the minimum viable cloud deployment

### Incremental Delivery

1. Phases 1–6 → MVP: App live on OKE with public access
2. Phase 7 → CI/CD: Automated deployment pipeline
3. Phase 8 → Verified: Full integration testing
4. Phase 9 → Delivered: Documentation complete

### Task Mix Summary

| Category | Tasks | Description |
|----------|-------|-------------|
| Manual (OCI Console) | T001-T006, T012-T015, T017-T019 | Infrastructure provisioning, secrets |
| Code Changes | T007-T011, T016, T020, T027, T032 | Helm templates, Dapr component, values overlay, CI/CD workflow |
| Build/Deploy | T021-T026, T028-T031, T034 | Docker builds, Helm deploy, verification |
| Testing | T035-T040 | Integration verification |
| Documentation | T041-T043 | Quickstart update, commit, PR |

---

## Notes

- Many tasks are **manual** (OCI Console operations, kubectl commands) — they cannot be automated by the LLM
- Code change tasks (T007-T011, T016, T020, T027, T032) are the LLM-executable tasks
- The LLM should prepare all code changes first, then guide the user through manual steps
- Secrets must never be committed to source control — use `--set` flags or `kubectl create secret`
- If E2.1.Micro nodes are too memory-constrained, fallback to VM.Standard.A1.Flex (Arm) per research.md R6
