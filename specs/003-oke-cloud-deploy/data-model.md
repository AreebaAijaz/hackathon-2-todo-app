# Data Model: Oracle Cloud Deployment

**Feature**: 003-oke-cloud-deploy
**Date**: 2026-02-08

## Infrastructure Entities

### OKE Cluster
- **Name**: taskflow-oke
- **Compartment**: hackathon-compartment
- **Region**: us-ashburn-1
- **K8s version**: v1.30
- **Node pool**: pool-1
  - Shape: VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM)
  - Count: 2 nodes
  - Availability domain: auto-distributed
- **VCN**: Auto-created with public/private subnets
- **Endpoint**: Public (API server accessible from internet for kubectl)

### OCIR Registry
- **Server**: iad.ocir.io
- **Namespace**: `<tenancy-namespace>`
- **Repository prefix**: `<tenancy-namespace>/taskflow`
- **Images**:
  | Image | Repository Path | Tag Strategy |
  |-------|----------------|-------------|
  | frontend | `<ns>/taskflow/frontend` | `git-sha` or `latest` |
  | backend | `<ns>/taskflow/backend` | `git-sha` or `latest` |
  | notification-service | `<ns>/taskflow/notification-service` | `git-sha` or `latest` |
  | recurring-service | `<ns>/taskflow/recurring-service` | `git-sha` or `latest` |
  | audit-service | `<ns>/taskflow/audit-service` | `git-sha` or `latest` |

### Redpanda Cloud Cluster
- **Type**: Serverless
- **Region**: us-east-1 (or closest available)
- **Bootstrap server**: `<cluster-id>.any.us-east-1.mpx.prd.cloud.redpanda.com:9092`
- **Auth**: SASL/SCRAM-SHA-256 over TLS
- **Topics**:
  | Topic | Partitions | Retention |
  |-------|-----------|-----------|
  | task-events | default | default |
  | reminders | default | default |
  | task-updates | default | default |

### Kubernetes Secrets
| Secret Name | Keys | Source |
|-------------|------|--------|
| taskflow-secrets | DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY, INTERNAL_SERVICE_USER_ID | Helm --set or kubectl |
| redpanda-credentials | username, password | kubectl create secret |
| ocir-secret | .dockerconfigjson | kubectl create secret docker-registry |

### GitHub Actions Secrets
| Secret Name | Description |
|-------------|------------|
| OCI_CLI_USER | OCI user OCID |
| OCI_CLI_TENANCY | OCI tenancy OCID |
| OCI_CLI_FINGERPRINT | API key fingerprint |
| OCI_CLI_KEY_CONTENT | PEM private key content |
| OCI_CLI_REGION | us-ashburn-1 |
| OKE_CLUSTER_OCID | OKE cluster OCID |
| OCIR_NAMESPACE | Tenancy namespace for OCIR |
| OCIR_USERNAME | OCIR login username |
| OCIR_TOKEN | OCIR auth token |
| DATABASE_URL | Neon PostgreSQL connection string |
| BETTER_AUTH_SECRET | Auth secret key |
| OPENAI_API_KEY | OpenAI API key |
| INTERNAL_SERVICE_USER_ID | User ID for service-to-service auth |
| REDPANDA_BROKERS | Redpanda Cloud bootstrap server |
| REDPANDA_USERNAME | Redpanda SASL username |
| REDPANDA_PASSWORD | Redpanda SASL password |

## Configuration Changes from Minikube

| Component | Minikube | OKE |
|-----------|----------|-----|
| Frontend service | NodePort:30080 | LoadBalancer |
| Backend service | NodePort:30081 | ClusterIP (internal) |
| Image source | Local (pullPolicy: Never) | OCIR (pullPolicy: Always) |
| Image repos | `modern-taskflow-frontend` | `iad.ocir.io/<ns>/taskflow/frontend` |
| Kafka broker | `redpanda.default.svc.cluster.local:9092` | `<cluster>.cloud.redpanda.com:9092` |
| Kafka auth | None (authRequired: false) | SASL/SCRAM-SHA-256 + TLS |
| Redpanda pod | StatefulSet in cluster | Managed cloud service |
| CORS origins | localhost:30080 | http://<LB-public-IP> |
| NEXT_PUBLIC_API_URL | localhost:30081 | http://<LB-public-IP>/api (via nginx proxy) or http://backend:8000 (internal) |
| imagePullSecrets | None | ocir-secret |
| Resource requests | 100m CPU, 128Mi | 25m CPU, 32-96Mi |
