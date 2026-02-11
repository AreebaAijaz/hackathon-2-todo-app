---
id: 0002
title: Phase 5C Implementation Plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-opus-4-6
feature: 003-oke-cloud-deploy
branch: 003-oke-cloud-deploy
user: san
command: /sp.plan
labels: ["oke", "deployment", "helm", "cicd", "infrastructure", "plan"]
links:
  spec: specs/003-oke-cloud-deploy/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-oke-cloud-deploy/plan.md
  - specs/003-oke-cloud-deploy/research.md
  - specs/003-oke-cloud-deploy/data-model.md
  - specs/003-oke-cloud-deploy/quickstart.md
  - specs/003-oke-cloud-deploy/contracts/api-contracts.md
  - CLAUDE.md
tests:
  - none (planning phase)
---

## Prompt

/sp.plan

Phase 1: Oracle Cloud Setup → Phase 2: OCIR Setup → Phase 3: Redpanda Cloud → Phase 4: Dapr + Secrets → Phase 5: Build + Push Images → Phase 6: Deploy to OKE → Phase 7: GitHub Actions → Phase 8: Testing → Phase 9: Documentation

Dependencies: Phase 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 (sequential)

## Response snapshot

Created full implementation plan for deploying TaskFlow to Oracle Cloud OKE with 9 sequential phases. Key deliverables:

1. **research.md** — 6 research decisions (R1-R6): OKE Always Free tier constraints (VM.Standard.E2.1.Micro, 1GB RAM per node), OCIR authentication with imagePullSecrets, Redpanda Cloud Serverless SASL/SCRAM-SHA-256 over TLS, GitHub Actions with oracle-actions, Helm values overlay strategy, resource constraints analysis (256Mi total workload requests to fit in ~1.4GB available).

2. **data-model.md** — Infrastructure entities (OKE cluster, OCIR registry, Redpanda Cloud, K8s secrets, GitHub Actions secrets) with full Minikube-to-OKE configuration diff table.

3. **contracts/api-contracts.md** — 5 contracts: GitHub Actions CI/CD workflow (16 required secrets, 5-stage pipeline), Helm values-oke.yaml schema, Dapr kafka-pubsub-cloud.yaml with SASL_SSL, OCIR imagePullSecret setup, Frontend CORS/API URL flow.

4. **quickstart.md** — 9-step deployment guide with commands and troubleshooting table.

5. **plan.md** — 9-phase implementation plan with verification steps, file change lists, dependency chain, and 3 risk mitigations.

Key architecture decisions: Helm overlay pattern (values-oke.yaml) keeps Minikube unchanged; separate Dapr cloud component (kafka-pubsub-cloud.yaml) to avoid breaking local dev; frontend proxies API calls via SSR so NEXT_PUBLIC_API_URL stays `http://backend:8000` for both environments; conditional imagePullSecrets in Helm templates.

## Outcome

- ✅ Impact: Complete plan for 9-phase cloud deployment created with all artifacts
- 🧪 Tests: None (planning phase — tests will come from /sp.tasks)
- 📁 Files: 6 files created/modified (plan.md, research.md, data-model.md, quickstart.md, api-contracts.md, CLAUDE.md)
- 🔁 Next prompts: /sp.tasks to generate task breakdown, then /sp.implement to begin execution
- 🧠 Reflection: Research agents provided useful scaffolding but lacked live web access; Dapr kafka component config for SASL_SSL confirmed from prior project experience

## Evaluation notes (flywheel)

- Failure modes observed: Research agents couldn't fetch live docs (no web access in subagent), but training data sufficed for OCI and Dapr configs
- Graders run and results (PASS/FAIL): N/A (planning)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run /sp.tasks to generate actionable task list from plan
