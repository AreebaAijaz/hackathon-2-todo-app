# Kubernetes Deployment Guide

Deploy Modern TaskFlow to a local Kubernetes cluster using Minikube and Helm.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Helm](https://helm.sh/docs/intro/install/)

### Install on Windows (PowerShell)

```powershell
winget install Docker.DockerDesktop
winget install Kubernetes.minikube
winget install Kubernetes.kubectl
winget install Helm.Helm
```

## Quick Start

### 1. Start Minikube

```bash
minikube start --driver=docker --memory=4096 --cpus=2
```

### 2. Build Images in Minikube

```bash
# Switch to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images
docker build -t modern-taskflow-backend:latest ./backend
docker build -t modern-taskflow-frontend:latest ./frontend
```

### 3. Deploy with Helm

```bash
helm install taskflow ./helm-chart \
  -f ./helm-chart/values-local.yaml \
  --set-string "secrets.databaseUrl=YOUR_DATABASE_URL" \
  --set-string "secrets.betterAuthSecret=YOUR_AUTH_SECRET" \
  --set-string "secrets.openaiApiKey=YOUR_OPENAI_KEY"
```

### 4. Access the Application

```bash
# Get the URL
minikube service taskflow-frontend --url

# Or access directly
echo "http://$(minikube ip):30080"
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Minikube Cluster                      │
│  ┌─────────────────┐         ┌─────────────────┐        │
│  │    Frontend     │         │    Backend      │        │
│  │  (Next.js 16)   │────────▶│   (FastAPI)     │        │
│  │   NodePort      │         │   ClusterIP     │        │
│  │   :30080        │         │   :8000         │        │
│  └─────────────────┘         └────────┬────────┘        │
│                                       │                  │
│  ┌─────────────────┐         ┌────────▼────────┐        │
│  │   ConfigMap     │         │    Secrets      │        │
│  │  (env config)   │         │  (credentials)  │        │
│  └─────────────────┘         └─────────────────┘        │
└─────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                            ┌─────────────────┐
                            │   Neon Database │
                            │  (PostgreSQL)   │
                            └─────────────────┘
```

## Helm Chart Structure

```
helm-chart/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default values
├── values-local.yaml       # Minikube overrides
└── templates/
    ├── _helpers.tpl        # Template helpers
    ├── configmap.yaml      # Environment config
    ├── secrets.yaml        # Sensitive data
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    └── NOTES.txt           # Post-install notes
```

## Commands Reference

### Minikube

| Command | Description |
|---------|-------------|
| `minikube start` | Start cluster |
| `minikube stop` | Stop cluster |
| `minikube delete` | Delete cluster |
| `minikube status` | Check status |
| `minikube ip` | Get cluster IP |
| `minikube ssh` | SSH into node |
| `minikube docker-env` | Configure Docker |
| `minikube service <name>` | Open service in browser |

### Helm

| Command | Description |
|---------|-------------|
| `helm install <name> <chart>` | Install release |
| `helm upgrade <name> <chart>` | Upgrade release |
| `helm uninstall <name>` | Remove release |
| `helm list` | List releases |
| `helm status <name>` | Release status |
| `helm template <name> <chart>` | Render templates |
| `helm lint <chart>` | Validate chart |

### kubectl

| Command | Description |
|---------|-------------|
| `kubectl get pods` | List pods |
| `kubectl get svc` | List services |
| `kubectl logs <pod>` | View logs |
| `kubectl describe pod <pod>` | Pod details |
| `kubectl exec -it <pod> -- sh` | Shell into pod |
| `kubectl port-forward svc/<name> <local>:<remote>` | Port forward |

## Configuration

### values.yaml

```yaml
frontend:
  replicaCount: 1
  image:
    repository: modern-taskflow-frontend
    tag: latest
    pullPolicy: Never  # Use local images
  service:
    type: NodePort
    port: 3000
    nodePort: 30080

backend:
  replicaCount: 1
  image:
    repository: modern-taskflow-backend
    tag: latest
    pullPolicy: Never
  service:
    type: ClusterIP
    port: 8000

secrets:
  databaseUrl: ""      # Required
  betterAuthSecret: "" # Required
  openaiApiKey: ""     # Required
```

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/instance=taskflow

# View pod events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Database connection errors

```bash
# Verify secret is set
kubectl get secret taskflow-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Test from backend pod
kubectl exec <backend-pod> -- curl localhost:8000/health
```

### Service not accessible

```bash
# Check service
kubectl get svc taskflow-frontend

# Use minikube tunnel (alternative)
minikube tunnel
```

### Image pull errors

```bash
# Ensure images are built in Minikube's Docker
eval $(minikube docker-env)
docker images | grep modern-taskflow

# Verify imagePullPolicy is Never
kubectl get deployment taskflow-frontend -o yaml | grep imagePullPolicy
```

## Cleanup

```bash
# Remove Helm release
helm uninstall taskflow

# Stop Minikube
minikube stop

# Delete cluster (full cleanup)
minikube delete

# Remove Docker images
docker rmi modern-taskflow-frontend:latest modern-taskflow-backend:latest
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Neon PostgreSQL connection string | Yes |
| `BETTER_AUTH_SECRET` | JWT signing secret | Yes |
| `OPENAI_API_KEY` | OpenAI API key for chat | Yes |
| `CORS_ORIGINS` | Allowed origins (auto-configured) | No |
| `NODE_ENV` | Node environment | No |

## Resources

- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
