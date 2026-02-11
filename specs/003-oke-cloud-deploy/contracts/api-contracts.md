# API & Infrastructure Contracts: Oracle Cloud Deployment

**Feature**: 003-oke-cloud-deploy
**Date**: 2026-02-09

## Contract 1: GitHub Actions CI/CD Workflow

**File**: `.github/workflows/deploy.yml`

### Trigger
```yaml
on:
  push:
    branches: [master]
  workflow_dispatch:  # Manual trigger
```

### Required Secrets (Repository Settings)
| Secret | Example Value | Description |
|--------|---------------|-------------|
| OCI_CLI_USER | ocid1.user.oc1..aaa... | OCI user OCID |
| OCI_CLI_TENANCY | ocid1.tenancy.oc1..aaa... | OCI tenancy OCID |
| OCI_CLI_FINGERPRINT | aa:bb:cc:dd:... | API key fingerprint |
| OCI_CLI_KEY_CONTENT | -----BEGIN PRIVATE KEY----- ... | PEM private key |
| OCI_CLI_REGION | us-ashburn-1 | OCI region |
| OKE_CLUSTER_OCID | ocid1.cluster.oc1.iad... | OKE cluster OCID |
| OCIR_NAMESPACE | axabc123xyz | Tenancy namespace |
| OCIR_USERNAME | axabc123xyz/user@example.com | OCIR login |
| OCIR_TOKEN | generated-auth-token | OCIR auth token |
| DATABASE_URL | postgresql+psycopg://... | Neon connection string |
| BETTER_AUTH_SECRET | random-secret | Auth secret key |
| OPENAI_API_KEY | sk-... | OpenAI API key |
| INTERNAL_SERVICE_USER_ID | uuid-string | Service auth user ID |
| REDPANDA_BROKERS | cluster.cloud.redpanda.com:9092 | Redpanda bootstrap |
| REDPANDA_USERNAME | sasl-username | Redpanda SASL user |
| REDPANDA_PASSWORD | sasl-password | Redpanda SASL pass |

### Workflow Stages

```
checkout → build-images → push-to-ocir → configure-kubectl → helm-upgrade
```

1. **checkout**: Standard `actions/checkout@v4`
2. **build-images**: Build 5 Docker images, tag with `${{ github.sha }}`
3. **push-to-ocir**: Login via `oracle-actions/login-ocir@v1`, push all images
4. **configure-kubectl**: `oci ce cluster create-kubeconfig --cluster-id $OKE_CLUSTER_OCID`
5. **helm-upgrade**: `helm upgrade --install taskflow ./helm-chart -f helm-chart/values-oke.yaml --set ...`

### Output Contract
- On success: All pods reach Running 2/2 within 10 minutes
- On failure: Previous version remains running (rolling update default)
- GitHub Actions status check visible on commit

---

## Contract 2: Helm Values Overlay (values-oke.yaml)

**File**: `helm-chart/values-oke.yaml`

### Schema
```yaml
# --- Image configuration (OCIR) ---
global:
  imagePullSecrets:
    - name: ocir-secret

frontend:
  image:
    repository: iad.ocir.io/<OCIR_NAMESPACE>/taskflow/frontend
    tag: latest                 # Overridden by CI/CD with git SHA
    pullPolicy: Always
  service:
    type: LoadBalancer          # Exposes public IP
    port: 3000
    # nodePort removed (LoadBalancer assigns automatically)
  resources:
    requests:
      cpu: 25m
      memory: 64Mi
    limits:
      cpu: 250m
      memory: 256Mi
  env:
    NEXT_PUBLIC_API_URL: "http://backend:8000"

backend:
  image:
    repository: iad.ocir.io/<OCIR_NAMESPACE>/taskflow/backend
    tag: latest
    pullPolicy: Always
  service:
    type: ClusterIP             # Internal only
    port: 8000
  resources:
    requests:
      cpu: 50m
      memory: 96Mi
    limits:
      cpu: 250m
      memory: 256Mi
  env:
    CORS_ORIGINS: "http://<LB_PUBLIC_IP>"  # Set during deployment

notificationService:
  image:
    repository: iad.ocir.io/<OCIR_NAMESPACE>/taskflow/notification-service
    tag: latest
    pullPolicy: Always
  resources:
    requests:
      cpu: 25m
      memory: 32Mi
    limits:
      cpu: 125m
      memory: 128Mi

recurringService:
  image:
    repository: iad.ocir.io/<OCIR_NAMESPACE>/taskflow/recurring-service
    tag: latest
    pullPolicy: Always
  resources:
    requests:
      cpu: 25m
      memory: 32Mi
    limits:
      cpu: 125m
      memory: 128Mi

auditService:
  image:
    repository: iad.ocir.io/<OCIR_NAMESPACE>/taskflow/audit-service
    tag: latest
    pullPolicy: Always
  resources:
    requests:
      cpu: 25m
      memory: 32Mi
    limits:
      cpu: 125m
      memory: 128Mi
```

### Invariants
- `imagePullSecrets` must reference `ocir-secret` (created out-of-band)
- `pullPolicy: Always` required for OCIR images
- Frontend service type must be `LoadBalancer` for public access
- Backend service type must be `ClusterIP` (accessed internally via Dapr/cluster DNS)
- Total memory requests: 64+96+32+32+32 = 256Mi (fits within ~1.4GB available)

---

## Contract 3: Dapr kafka-pubsub Component (Cloud)

**File**: `k8s/dapr-components/kafka-pubsub-cloud.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "<REDPANDA_BROKERS>"          # From K8s secret or direct
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: redpanda-credentials
        key: username
    - name: saslPassword
      secretKeyRef:
        name: redpanda-credentials
        key: password
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: initialOffset
      value: "oldest"
    - name: maxMessageBytes
      value: "1048576"
```

### Differences from Local (kafka-pubsub.yaml)
| Field | Local | Cloud |
|-------|-------|-------|
| brokers | redpanda.default.svc.cluster.local:9092 | Redpanda Cloud URL |
| authRequired/authType | false | password |
| disableTls | true | (removed = TLS enabled) |
| saslUsername | (absent) | secretKeyRef → redpanda-credentials |
| saslPassword | (absent) | secretKeyRef → redpanda-credentials |
| saslMechanism | (absent) | SCRAM-SHA-256 |

### Required K8s Secret
```bash
kubectl create secret generic redpanda-credentials \
  --from-literal=username='<SASL_USERNAME>' \
  --from-literal=password='<SASL_PASSWORD>'
```

---

## Contract 4: OCIR Image Pull Secret

```bash
kubectl create secret docker-registry ocir-secret \
  --docker-server=iad.ocir.io \
  --docker-username='<OCIR_NAMESPACE>/<USERNAME>' \
  --docker-password='<AUTH_TOKEN>' \
  --docker-email='<EMAIL>'
```

### Helm Template Change
All deployment templates must include:
```yaml
spec:
  {{- with .Values.global.imagePullSecrets }}
  imagePullSecrets:
    {{- toYaml . | nindent 8 }}
  {{- end }}
  containers:
    ...
```

---

## Contract 5: Frontend CORS and API URL Flow

```
Browser → http://<LB_PUBLIC_IP>:3000 → Frontend (Next.js)
  ↓ API call
Frontend (server-side) → http://backend:8000 → Backend (FastAPI)
  ↓ Events
Backend → Dapr sidecar → Redpanda Cloud (SASL_SSL) → Consumer services
```

### NEXT_PUBLIC_API_URL
- **Server-side rendering (SSR)**: `http://backend:8000` (cluster internal DNS)
- **Client-side (browser)**: Needs public backend URL OR reverse proxy through frontend

**Decision**: Frontend Next.js already proxies `/api/*` requests to the backend via its server-side configuration. The client calls the frontend's own origin, which SSR-proxies to backend. This means `NEXT_PUBLIC_API_URL` = `http://backend:8000` works for both local and cloud.

### CORS_ORIGINS
- Must include the LoadBalancer public IP: `http://<LB_PUBLIC_IP>`
- Set via `--set backend.env.CORS_ORIGINS=http://<IP>` during Helm install
