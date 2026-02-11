# Research: Oracle Cloud Deployment (OKE + CI/CD)

**Feature**: 003-oke-cloud-deploy
**Date**: 2026-02-08

## R1: OKE Always Free Tier

**Decision**: Use OKE with VM.Standard.E2.1.Micro nodes (Always Free)

**Rationale**: Oracle Cloud Always Free tier includes:
- OKE cluster management: Free (no charge for control plane)
- Compute nodes: Up to 4 Arm-based Ampere A1 cores + 24GB RAM, OR 2x VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM each, AMD)
- Load Balancer: 1 flexible LB, 10 Mbps bandwidth (free)
- OCIR: 500MB free container image storage
- Networking: VCN, subnets, internet gateway all free

**Important note**: VM.Standard.E2.1.Micro has only 1GB RAM per node. With Dapr sidecars (+~128MB each), 5 services may be tight. Resource requests must be minimized. Alternative: Use VM.Standard.A1.Flex (Arm) with 4 OCPUs + 24GB RAM for more headroom, but requires ARM-compatible Docker images (multi-arch builds).

**Alternatives considered**:
- VM.Standard.A1.Flex (Arm): More resources but requires multi-arch Docker builds — added complexity
- GKE Autopilot free tier: Not truly free for sustained workloads
- EKS: No free tier for cluster management

**Resolution**: Start with E2.1.Micro (AMD). If memory is too tight, switch to A1.Flex (Arm) with multi-arch images.

## R2: OCIR Authentication and Image Pull

**Decision**: Use OCIR with docker-credential and imagePullSecrets

**Rationale**:
- OCIR URL format: `<region-key>.ocir.io/<tenancy-namespace>/<repo>/<image>:<tag>`
- Region key for us-ashburn-1: `iad`
- Auth: Username = `<tenancy-namespace>/oracleidentitycloudservice/<email>` (for IDCS) or `<tenancy-namespace>/<username>` (for local users)
- Password: OCI auth token (generated in console)
- imagePullSecret: `kubectl create secret docker-registry ocir-secret --docker-server=iad.ocir.io --docker-username=<ns>/<user> --docker-password=<token>`
- All deployment templates need `imagePullSecrets` added to pod spec

**Alternatives considered**:
- Docker Hub: Has rate limits on free tier; OCIR is co-located and free
- GitHub Container Registry: Possible but adds external dependency

## R3: Redpanda Cloud Serverless + Dapr

**Decision**: Use Redpanda Cloud Serverless with SASL/SCRAM over TLS

**Rationale**:
- Redpanda Cloud Serverless free tier: Limited throughput but sufficient for demo
- Authentication: SASL/SCRAM-SHA-256 over TLS (port 9092 with SASL_SSL)
- Bootstrap server format: `<cluster-id>.any.us-east-1.mpx.prd.cloud.redpanda.com:9092`
- Topics created via Redpanda Cloud console (or rpk CLI)
- Dapr component needs: `authType: password`, `saslUsername`, `saslPassword`, `saslMechanism: SCRAM-SHA-256`

**Dapr kafka-pubsub for Redpanda Cloud**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "<cluster-id>.any.us-east-1.mpx.prd.cloud.redpanda.com:9092"
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

**Alternatives considered**:
- Confluent Cloud: Free tier available but more complex setup
- Self-hosted Redpanda on OKE: Uses node resources, not viable on 1GB RAM nodes
- MSK Serverless: AWS only

## R4: GitHub Actions for OCI/OKE

**Decision**: Use GitHub Actions with OCI CLI action and kubectl

**Rationale**:
- `oracle-actions/login-ocir`: Official action to authenticate with OCIR
- `oracle-actions/run-oci-cli-command`: Run OCI CLI commands
- For kubectl: Export KUBECONFIG from OCI CLI or use `oci ce cluster create-kubeconfig`
- Secrets needed: OCI_CLI_USER, OCI_CLI_TENANCY, OCI_CLI_FINGERPRINT, OCI_CLI_KEY_CONTENT, OCI_CLI_REGION
- Image tagging: Use `${{ github.sha }}` for unique tags

**Workflow structure**:
1. Checkout code
2. Login to OCIR via `oracle-actions/login-ocir`
3. Build and push 5 images (parallel with `docker buildx`)
4. Configure kubectl via `oci ce cluster create-kubeconfig`
5. Helm upgrade with new image tags

**Alternatives considered**:
- OCI DevOps pipelines: More complex, tied to OCI console
- ArgoCD: Overkill for this use case
- Jenkins: Self-hosted, not free

## R5: Helm Chart Changes for OKE

**Decision**: Create `values-oke.yaml` overlay with OCIR image paths and LoadBalancer service type

**Rationale**:
- Keep `values.yaml` (defaults) and `values-local.yaml` (Minikube) unchanged
- New `values-oke.yaml` with:
  - Image repositories pointing to OCIR
  - Service type: LoadBalancer for frontend
  - Resource requests reduced for 1GB RAM nodes
  - `imagePullSecrets` reference
- All deployment templates need `imagePullSecrets` added (conditional)
- kafka-pubsub component needs cloud version (separate YAML or template)
- Secrets managed via `--set` flags in CI/CD (never in values files)

**Alternatives considered**:
- Kustomize overlays: Adds tooling dependency; Helm already supports value overrides
- Separate Helm chart: Duplicates templates unnecessarily

## R6: Resource Constraints on E2.1.Micro

**Decision**: Minimize resource requests to fit 5 services + Dapr on 2x 1GB nodes

**Rationale**:
- 2 nodes × 1GB RAM = 2GB total
- System overhead: ~300MB per node = 600MB reserved
- Available: ~1.4GB for workloads
- Dapr sidecars: ~50-128MB each × 5 = 250-640MB
- Services themselves: Need ~64-256MB each
- **This is extremely tight.** Must set very low resource requests.

**Proposed resource allocation**:
| Service | Request Memory | Limit Memory |
|---------|---------------|-------------|
| frontend | 64Mi | 256Mi |
| backend | 96Mi | 256Mi |
| notification | 32Mi | 128Mi |
| recurring | 32Mi | 128Mi |
| audit | 32Mi | 128Mi |
| Dapr sidecar (each) | ~50Mi (controlled by Dapr) | ~128Mi |

**Risk**: Pods may be OOMKilled under load. This is acceptable for a demo/hackathon deployment.

**Fallback**: If E2.1.Micro is too constrained, switch to A1.Flex (Arm, 4 OCPU + 24GB) which requires multi-arch Docker builds.
