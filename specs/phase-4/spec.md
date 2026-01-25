# Phase IV - Local Kubernetes Deployment with Minikube

## Overview

Phase IV containerizes the application and deploys it to a local Kubernetes cluster using Minikube and Helm.

## Goals

1. Containerize frontend and backend applications
2. Create Helm chart for Kubernetes deployment
3. Deploy to local Minikube cluster
4. Verify application functionality in Kubernetes environment

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Minikube                              │
│  ┌─────────────────┐     ┌─────────────────┐                │
│  │    Frontend     │────▶│    Backend      │                │
│  │   (NodePort)    │     │   (ClusterIP)   │                │
│  │   Port: 30080   │     │   Port: 8000    │                │
│  └─────────────────┘     └─────────────────┘                │
│           │                      │                           │
│           │                      ▼                           │
│           │              ┌───────────────┐                  │
│           │              │ Neon Postgres │                  │
│           │              │  (External)   │                  │
│           │              └───────────────┘                  │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
      http://$(minikube ip):30080
```

## Components

### Docker Images

| Image | Base | Size |
|-------|------|------|
| modern-taskflow-frontend | node:20-alpine | 208MB |
| modern-taskflow-backend | python:3.13-slim | 276MB |

### Kubernetes Resources

| Resource | Name | Purpose |
|----------|------|---------|
| Deployment | taskflow-frontend | Frontend pods |
| Deployment | taskflow-backend | Backend pods |
| Service | taskflow-frontend | NodePort access |
| Service | taskflow-backend | Internal ClusterIP |
| ConfigMap | taskflow-config | Non-sensitive config |
| Secret | taskflow-secrets | Credentials |

## Prerequisites

- Docker Desktop
- Minikube
- Helm 3.x
- kubectl

## Deployment

### Quick Start (Windows)

```powershell
# Set environment variables
$env:DATABASE_URL = "postgresql://..."
$env:BETTER_AUTH_SECRET = "your-secret"
$env:OPENAI_API_KEY = "sk-..."

# Run deployment script
.\scripts\deploy-minikube.ps1
```

### Quick Start (Linux/macOS)

```bash
# Set environment variables
export DATABASE_URL="postgresql://..."
export BETTER_AUTH_SECRET="your-secret"
export OPENAI_API_KEY="sk-..."

# Run deployment script
chmod +x ./scripts/deploy-minikube.sh
./scripts/deploy-minikube.sh
```

### Manual Deployment

```bash
# 1. Start Minikube
minikube start --driver=docker

# 2. Configure Docker to use Minikube
eval $(minikube docker-env)  # Linux/macOS
# or
minikube docker-env --shell powershell | Invoke-Expression  # Windows

# 3. Build images
docker build -t modern-taskflow-backend:latest ./backend
docker build -t modern-taskflow-frontend:latest ./frontend \
    --build-arg DATABASE_URL="..." \
    --build-arg BETTER_AUTH_SECRET="..." \
    --build-arg NEXT_PUBLIC_API_URL="http://backend:8000"

# 4. Deploy with Helm
helm install taskflow ./helm-chart \
    -f ./helm-chart/values-local.yaml \
    --set secrets.databaseUrl="..." \
    --set secrets.betterAuthSecret="..." \
    --set secrets.openaiApiKey="..."

# 5. Access application
minikube service taskflow-frontend
```

## Verification

```bash
# Check pods
kubectl get pods -l app.kubernetes.io/instance=taskflow

# Check services
kubectl get svc -l app.kubernetes.io/instance=taskflow

# View logs
kubectl logs -l app.kubernetes.io/component=frontend -f
kubectl logs -l app.kubernetes.io/component=backend -f

# Port forward (alternative access)
kubectl port-forward svc/taskflow-frontend 3000:3000
```

## Cleanup

```bash
# Remove Helm release
helm uninstall taskflow

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional)
minikube delete
```

## Success Criteria

- [x] Both frontend and backend pods running
- [x] Application accessible via NodePort
- [x] Authentication working
- [x] Todo CRUD operations functional
- [x] AI chat feature operational
