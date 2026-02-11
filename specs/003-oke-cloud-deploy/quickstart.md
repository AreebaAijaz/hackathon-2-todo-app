# Quickstart: Deploy TaskFlow to Oracle Cloud (OKE)

**Feature**: 003-oke-cloud-deploy
**Date**: 2026-02-11
**Status**: DEPLOYED

## Live Deployment

| Component | URL |
|-----------|-----|
| Frontend | http://80.225.211.34:3000 |
| Backend API | http://80.225.232.189:8000 |
| Backend Docs | http://80.225.232.189:8000/docs |

## Infrastructure

| Resource | Value |
|----------|-------|
| OKE Cluster OCID | `ocid1.cluster.oc1.ap-mumbai-1.aaaaaaaaqqdgmmbvs4jmitnonpqjouz6sgonmvkdrtc24djkrch5z3qlit3a` |
| Region | `ap-mumbai-1` (Mumbai) |
| OCIR Registry | `bom.ocir.io` |
| OCIR Namespace | `bmchaanonuwz` |
| Nodes | 3x (K8s v1.34.2) |
| Dapr | v1.16.8 |
| Redpanda Cloud | `d65n25bt489913vpgoj0.any.us-east-1.mpx.prd.cloud.redpanda.com:9092` |

## Prerequisites

- Oracle Cloud account with Always Free tier (compartment: `hackathon-compartment`)
- OCI CLI installed and configured (`oci setup config`)
- kubectl installed
- Helm 3 installed
- Docker Desktop (for building images)
- GitHub repository with Actions enabled

## Step 1: Provision OKE Cluster (Manual — OCI Console)

1. Navigate to **Developer Services → Kubernetes Clusters (OKE)**
2. Create cluster:
   - Name: `taskflow-oke`
   - Compartment: `hackathon-compartment`
   - Kubernetes version: v1.30+
   - Quick Create → **Basic** cluster → Public endpoint
3. Wait for cluster status: **Active** (~10 min)
4. Download kubeconfig:
   ```bash
   oci ce cluster create-kubeconfig \
     --cluster-id ocid1.cluster.oc1.ap-mumbai-1.aaaaaaaaqqdgmmbvs4jmitnonpqjouz6sgonmvkdrtc24djkrch5z3qlit3a \
     --file $HOME/.kube/config \
     --region ap-mumbai-1 \
     --token-version 2.0.0
   ```
5. Verify: `kubectl get nodes` → 3 nodes in Ready state

## Step 2: Provision Redpanda Cloud (Manual — Redpanda Console)

1. Sign up at https://cloud.redpanda.com
2. Create a **Serverless** cluster (free tier)
3. Note the **bootstrap server URL**
4. Create topics: `task-events`, `reminders`, `task-updates` (auto-created on first publish)
5. Create a SASL user (Security → Users) with full ACL access

## Step 3: Create Kubernetes Secrets

```bash
# OCIR image pull secret
kubectl create secret docker-registry ocir-secret \
  --docker-server=bom.ocir.io \
  --docker-username='bmchaanonuwz/<your-email>' \
  --docker-password='<AUTH_TOKEN>'

# Redpanda credentials
kubectl create secret generic redpanda-credentials \
  --from-literal=username='<SASL_USERNAME>' \
  --from-literal=password='<SASL_PASSWORD>'
```

## Step 4: Install Dapr on OKE

```bash
dapr init -k
dapr status -k  # Verify all components healthy
```

## Step 5: Deploy Dapr Component (Cloud Kafka)

```bash
kubectl apply -f k8s/dapr-components/kafka-pubsub-cloud.yaml
```

**IMPORTANT**: The `saslMechanism` must be `SHA-256` (not `SCRAM-SHA-256`) for Dapr's Kafka component.

## Step 6: Build and Push Images to OCIR

```bash
# Login to OCIR (Mumbai region = bom)
docker login bom.ocir.io -u 'bmchaanonuwz/<your-email>' -p '<AUTH_TOKEN>'

# Build and push each image
for svc in frontend backend; do
  docker build -t bom.ocir.io/bmchaanonuwz/taskflow/${svc}:latest ./${svc}/
  docker push bom.ocir.io/bmchaanonuwz/taskflow/${svc}:latest
done

for svc in notification-service recurring-service audit-service; do
  docker build -t bom.ocir.io/bmchaanonuwz/taskflow/${svc}:latest ./services/${svc}/
  docker push bom.ocir.io/bmchaanonuwz/taskflow/${svc}:latest
done
```

Note: Frontend needs `--build-arg NEXT_PUBLIC_API_URL=http://<BACKEND_LB_IP>:8000` for the API URL.

## Step 7: Deploy with Helm

```bash
helm upgrade --install taskflow ./helm-chart \
  -f helm-chart/values-oke.yaml \
  --set-string secrets.databaseUrl='<NEON_URL>' \
  --set-string secrets.betterAuthSecret='<SECRET>' \
  --set-string secrets.openaiApiKey='<KEY>' \
  --set-string secrets.internalServiceUserId='<UUID>' \
  --set backend.env.CORS_ORIGINS='http://<FRONTEND_LB_IP>:3000'
```

## Step 8: Get Public IP

```bash
kubectl get svc -l app.kubernetes.io/instance=taskflow
# Wait for EXTERNAL-IP to appear (may take 2-5 minutes)
```

Open `http://<EXTERNAL-IP>:3000` in your browser.

## Step 9: Configure GitHub Actions (CI/CD)

14 secrets required in GitHub repository settings:
- OCI: `OCI_CLI_USER`, `OCI_CLI_TENANCY`, `OCI_CLI_FINGERPRINT`, `OCI_CLI_KEY_CONTENT`, `OCI_CLI_REGION`
- OCIR: `OCIR_NAMESPACE`, `OCIR_USERNAME`, `OCIR_TOKEN`
- OKE: `OKE_CLUSTER_OCID`
- App: `DATABASE_URL`, `BETTER_AUTH_SECRET`, `OPENAI_API_KEY`, `INTERNAL_SERVICE_USER_ID`
- Frontend: `NEXT_PUBLIC_API_URL`, `CORS_ORIGINS`

Push to `master` branch to trigger the workflow.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Pods stuck in `ImagePullBackOff` | OCIR auth failed | Verify `ocir-secret` and image paths |
| Pods 1/2 (no Dapr sidecar) | Dapr not installed | Run `dapr init -k` |
| Dapr sidecar CrashLoopBackOff | Kafka auth failed — wrong saslMechanism | Use `SHA-256` not `SCRAM-SHA-256` in Dapr component |
| Backend CrashLoopBackOff | DATABASE_URL wrong | Check `taskflow-secrets` secret |
| Events not flowing | Redpanda auth failed | Check `redpanda-credentials` secret |
| No EXTERNAL-IP | LB provisioning | Wait 5 min; check OCI LB console |
| OOMKilled pods | Node memory full | Reduce resource limits in values-oke.yaml |
| Windows OCI CLI install fails | Long path not enabled | Enable `LongPathsEnabled` in Windows registry |
| OCI API key paste fails | Key format issue | Use "Generate API key pair" in OCI Console instead |
