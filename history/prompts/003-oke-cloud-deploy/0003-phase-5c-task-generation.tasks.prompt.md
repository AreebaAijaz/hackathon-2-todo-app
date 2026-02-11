---
id: 0003
title: Phase 5C Task Generation
stage: tasks
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 003-oke-cloud-deploy
branch: 003-oke-cloud-deploy
user: san
command: /sp.tasks
labels: ["oke", "tasks", "deployment", "cicd", "infrastructure"]
links:
  spec: specs/003-oke-cloud-deploy/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-oke-cloud-deploy/tasks.md
tests:
  - none (task generation phase)
---

## Prompt

/sp.tasks

Phase 1: Oracle Cloud Setup (4 tasks)
1.1 Sign up and create compartment → Compartment ready
1.2 Create VCN with Internet Gateway → Network ready
1.3 Create OKE cluster → Cluster provisioning
1.4 Get kubeconfig and install OCI CLI → kubectl connected
CHECKPOINT 1: OKE ready

Phase 2: OCIR Setup (2 tasks)
2.1 Create auth token and login to OCIR → OCIR authenticated
2.2 Create 4 image repositories → Repos ready
CHECKPOINT 2: Container registry ready

Phase 3: Redpanda Cloud (3 tasks)
3.1 Create serverless cluster → Cluster created
3.2 Create 3 topics → Topics ready
3.3 Get SASL credentials and test → Connection verified
CHECKPOINT 3: Kafka cloud ready

Phase 4: Dapr + Secrets (3 tasks)
4.1 Install Dapr on OKE → Dapr installed
4.2 Update Dapr components for Redpanda Cloud → Components configured
4.3 Create Kubernetes secrets → Secrets created
CHECKPOINT 4: Dapr configured

Phase 5: Build and Push Images (2 tasks)
5.1 Build 4 Docker images → Images built
5.2 Push to OCIR → Images in Oracle registry
CHECKPOINT 5: Images in OCIR

Phase 6: Deploy to OKE (3 tasks)
6.1 Update Helm chart for Oracle Cloud → Chart updated
6.2 helm install taskflow → Deployed to OKE
6.3 Wait for LoadBalancer IP → Public IP assigned
CHECKPOINT 6: Live on Oracle Cloud

Phase 7: GitHub Actions CI/CD (3 tasks)
7.1 Create .github/workflows/deploy-oracle.yml → Workflow created
7.2 Add GitHub secrets for Oracle Cloud → OCI credentials added
7.3 Test git push auto-deploy → CI/CD working
CHECKPOINT 7: CI/CD active

Phase 8: Integration Testing (2 tasks)
8.1 Test all features on public URL → All features work
8.2 Verify event flow to Redpanda Cloud → Events flowing
CHECKPOINT 8: Fully tested

Phase 9: Documentation (1 task)
9.1 Update README with Oracle Cloud info and commit → Phase 5C complete
CHECKPOINT 9: Delivered

## Response snapshot

Generated 43-task breakdown (T001-T043) across 9 sequential phases mapped to 4 user stories:

- **US2 (Infrastructure, P1)**: 20 tasks (T001-T020) — OKE cluster, OCIR, Redpanda Cloud, Dapr + Secrets
- **US1 (Public Access, P1)**: 17 tasks (T021-T031, T035-T039) — build images, deploy, verify
- **US3 (CI/CD, P2)**: 3 tasks (T032-T034) — GitHub Actions workflow
- **US4 (Zero-Cost, P2)**: 1 task (T040) — billing verification
- Documentation: 3 tasks (T041-T043)

Key design decisions:
1. Expanded user's 23-task outline to 43 tasks for LLM-executable specificity
2. Split OCIR imagePullSecrets into 5 parallel tasks (one per deployment template)
3. Split Docker builds into 5 parallel tasks (one per service)
4. Added INTERNAL_SERVICE_USER_ID to Helm secrets template (identified as missing)
5. Task mix: 15 manual (OCI Console), 9 code changes, 11 build/deploy, 6 testing, 3 docs

## Outcome

- ✅ Impact: Complete 43-task breakdown ready for /sp.implement execution
- 🧪 Tests: None (task generation phase)
- 📁 Files: 1 file created (tasks.md)
- 🔁 Next prompts: /sp.implement to begin execution, starting with code changes (T007-T011, T016, T020, T027, T032) while user handles manual OCI tasks
- 🧠 Reflection: Infrastructure deployments have a high manual-to-code ratio; the LLM can prepare all code changes upfront then guide user through manual steps

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Format validation PASS — all 43 tasks have checkbox, ID, story label, file paths
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Execute code change tasks (T007-T011, T016, T020, T027, T032) in parallel before manual tasks
