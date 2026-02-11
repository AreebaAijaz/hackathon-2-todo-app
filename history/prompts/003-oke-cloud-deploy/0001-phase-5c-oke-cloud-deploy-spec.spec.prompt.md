---
id: 0001
title: Phase 5C OKE Cloud Deploy Spec
stage: spec
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 003-oke-cloud-deploy
branch: 003-oke-cloud-deploy
user: san
command: /sp.specify
labels: ["oracle-cloud", "oke", "cicd", "github-actions", "ocir", "redpanda-cloud"]
links:
  spec: specs/003-oke-cloud-deploy/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-oke-cloud-deploy/spec.md
  - specs/003-oke-cloud-deploy/checklists/requirements.md
  - CLAUDE.md
tests:
  - null
---

## Prompt

/sp.specify Phase 5C - Oracle Cloud Deployment (OKE + CI/CD). Goal: Deploy Phase 5B to Oracle Cloud Kubernetes Engine (OKE) with public access and GitHub Actions CI/CD. Infrastructure: OKE cluster (2 nodes, 4 OCPUs, 24GB RAM total - always free), OCIR (free), Redpanda Cloud Serverless (free tier), Neon (existing), OCI Load Balancer (free tier). Changes from Minikube: Cluster → OKE, Services → LoadBalancer, Registry → OCIR, Kafka → Redpanda Cloud, Deployment → GitHub Actions. OKE specs: hackathon-compartment, taskflow-oke, v1.30, VM.Standard.E2.1.Micro x2. GitHub Actions: push to main triggers build → push OCIR → deploy OKE. Success: all pods running, public IP, zero charges.

## Response snapshot

Created feature branch `003-oke-cloud-deploy` and wrote comprehensive spec with:
- 4 user stories: Public Internet Access (P1), Cloud Infrastructure (P1), CI/CD Automation (P2), Zero-Cost Deployment (P2)
- 13 functional requirements covering OKE deployment, OCIR registry, Redpanda Cloud SASL_SSL, GitHub Actions CI/CD, secrets management
- 6 measurable success criteria
- 6 edge cases (node failure, broker unavailable, image pull failure, bandwidth, secrets misconfiguration, DB unreachable)
- Quality checklist: all items pass, no clarifications needed
- Updated CLAUDE.md with new active technologies

## Outcome

- Impact: Complete deployment spec ready for planning
- Tests: N/A (spec phase)
- Files: spec.md, checklists/requirements.md, CLAUDE.md
- Next prompts: /sp.plan to create implementation plan, /sp.tasks to generate task breakdown
- Reflection: User input was exceptionally detailed — no clarification markers needed. Corrected audit-service oversight (5 images not 4).

## Evaluation notes (flywheel)

- Failure modes observed: None — user provided comprehensive infrastructure details
- Graders run and results (PASS/FAIL): Quality checklist PASS (all items)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
