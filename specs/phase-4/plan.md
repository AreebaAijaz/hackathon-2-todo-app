# Phase IV - Local Kubernetes Deployment Plan

## Architecture Overview

```
Docker Containers → Minikube K8s Cluster → Helm Charts → AI DevOps Tools
```

---

## Phase 1: Docker Setup

### Tasks
1. Install Docker Desktop, enable Gordon AI
2. Create frontend Dockerfile with Gordon AI assistance
3. Create backend Dockerfile with Gordon AI assistance
4. Build and test containers locally
5. Optimize image sizes

### Commands
```powershell
# Verify Docker installation
docker --version
docker info

# Build images locally (test)
docker build -t modern-taskflow-frontend:latest ./frontend
docker build -t modern-taskflow-backend:latest ./backend

# Test containers
docker run -d -p 8000:8000 --name backend-test modern-taskflow-backend:latest
docker run -d -p 3000:3000 --name frontend-test modern-taskflow-frontend:latest

# Check image sizes
docker images | grep modern-taskflow
```

### Success Criteria
- [ ] Docker Desktop running with Gordon AI enabled
- [ ] Frontend image builds successfully
- [ ] Backend image builds successfully
- [ ] Containers run without errors
- [ ] Image sizes optimized (frontend ~150MB, backend ~200MB)

---

## Phase 2: Minikube Setup

### Tasks
1. Install Minikube, kubectl, Helm
2. Start Minikube cluster
3. Configure docker-env for Minikube
4. Verify cluster running

### Commands
```powershell
# Install (Windows - using winget)
winget install Kubernetes.minikube
winget install Kubernetes.kubectl
winget install Helm.Helm

# Start Minikube
minikube start --driver=docker --memory=4096 --cpus=2

# Verify cluster
minikube status
kubectl cluster-info
kubectl get nodes

# Configure Docker to use Minikube's daemon
minikube docker-env --shell powershell | Invoke-Expression
```

### Success Criteria
- [ ] Minikube installed and version verified
- [ ] kubectl connected to cluster
- [ ] Helm 3.x installed
- [ ] Cluster status shows "Running"

---

## Phase 3: Helm Chart Creation

### Tasks
1. Use kubectl-ai to generate Helm templates (optional)
2. Create Chart.yaml, values.yaml
3. Build deployment templates (frontend, backend)
4. Build service templates
5. Create ConfigMap and Secrets
6. Test chart locally (helm template)

### Structure
```
helm-chart/
├── Chart.yaml
├── values.yaml
├── values-local.yaml
└── templates/
    ├── _helpers.tpl
    ├── configmap.yaml
    ├── secrets.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    └── NOTES.txt
```

### Commands
```powershell
# Validate chart syntax
helm lint ./helm-chart

# Dry-run to see generated manifests
helm template taskflow ./helm-chart -f ./helm-chart/values-local.yaml

# Check for issues
helm template taskflow ./helm-chart --debug
```

### Success Criteria
- [ ] Chart.yaml with correct metadata
- [ ] values.yaml with all configuration
- [ ] All templates render without errors
- [ ] helm lint passes

---

## Phase 4: Image Build for Minikube

### Tasks
1. Switch to Minikube Docker context
2. Rebuild frontend and backend images
3. Verify images in Minikube registry
4. Tag images correctly

### Commands
```powershell
# Switch to Minikube Docker context
minikube docker-env --shell powershell | Invoke-Expression

# Build images (now inside Minikube)
docker build -t modern-taskflow-backend:latest ./backend

docker build -t modern-taskflow-frontend:latest ./frontend `
    --build-arg DATABASE_URL="$env:DATABASE_URL" `
    --build-arg BETTER_AUTH_SECRET="$env:BETTER_AUTH_SECRET" `
    --build-arg NEXT_PUBLIC_API_URL="http://taskflow-backend:8000"

# Verify images exist in Minikube
docker images | Select-String "modern-taskflow"
```

### Success Criteria
- [ ] Docker context switched to Minikube
- [ ] Both images built inside Minikube
- [ ] Images visible with `docker images`
- [ ] Images tagged as `latest`

---

## Phase 5: Helm Deployment

### Tasks
1. helm install todo-app ./helm-chart
2. kubectl get pods (verify running)
3. kubectl get services (get access URLs)
4. Test connectivity between services

### Commands
```powershell
# Set secrets as environment variables
$env:DATABASE_URL = "postgresql://..."
$env:BETTER_AUTH_SECRET = "..."
$env:OPENAI_API_KEY = "sk-..."

# Install with Helm
helm install taskflow ./helm-chart `
    -f ./helm-chart/values-local.yaml `
    --set secrets.databaseUrl="$env:DATABASE_URL" `
    --set secrets.betterAuthSecret="$env:BETTER_AUTH_SECRET" `
    --set secrets.openaiApiKey="$env:OPENAI_API_KEY"

# Verify deployment
kubectl get pods -l app.kubernetes.io/instance=taskflow
kubectl get svc -l app.kubernetes.io/instance=taskflow
kubectl get configmap,secret -l app.kubernetes.io/instance=taskflow

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=taskflow --timeout=120s
```

### Success Criteria
- [ ] Helm install completes without errors
- [ ] All pods show Running status
- [ ] Services created with correct ports
- [ ] ConfigMap and Secret created

---

## Phase 6: Access & Testing

### Tasks
1. minikube service frontend --url
2. Test chatbot in browser
3. Verify backend API
4. Test database connectivity (Neon)
5. Check logs for errors

### Commands
```powershell
# Get access URL
minikube service taskflow-frontend --url

# Or access directly
$minikubeIp = minikube ip
Write-Host "Access at: http://${minikubeIp}:30080"

# Alternative: port-forward
kubectl port-forward svc/taskflow-frontend 3000:3000

# Check logs
kubectl logs -l app.kubernetes.io/component=frontend -f
kubectl logs -l app.kubernetes.io/component=backend -f

# Test backend health
kubectl exec -it $(kubectl get pod -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}') -- curl localhost:8000/health
```

### Testing Checklist
- [ ] Frontend loads in browser
- [ ] User can sign up/login
- [ ] Todo CRUD operations work
- [ ] AI chat responds correctly
- [ ] No errors in pod logs

---

## Phase 7: AI DevOps Optimization

### Tasks
1. Install kubectl-ai and Kagent
2. kagent "analyze cluster health"
3. Optimize resource limits
4. Test rolling updates (helm upgrade)
5. Verify zero-downtime deployment

### Commands
```powershell
# Install kubectl-ai (optional)
# pip install kubectl-ai

# Analyze with AI tools
# kagent "analyze cluster health"
# kagent "suggest resource optimizations"

# Update deployment (rolling update)
helm upgrade taskflow ./helm-chart `
    -f ./helm-chart/values-local.yaml `
    --set secrets.databaseUrl="$env:DATABASE_URL" `
    --set secrets.betterAuthSecret="$env:BETTER_AUTH_SECRET" `
    --set secrets.openaiApiKey="$env:OPENAI_API_KEY" `
    --set frontend.replicaCount=2

# Watch rolling update
kubectl rollout status deployment/taskflow-frontend

# Verify zero-downtime
kubectl get pods -w
```

### Success Criteria
- [ ] AI tools provide useful insights
- [ ] Resource limits optimized
- [ ] Rolling update completes successfully
- [ ] No downtime during update

---

## Phase 8: Documentation

### Tasks
1. Write README-k8s.md (setup instructions)
2. Document Minikube commands
3. Document Helm commands
4. Commit to GitHub

### Deliverables
- [ ] README-k8s.md with full setup guide
- [ ] Quick reference commands
- [ ] Troubleshooting section
- [ ] All changes committed to GitHub

---

## Dependencies

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8
(Docker)  (Minikube) (Helm)   (Build)   (Deploy)  (Test)   (Optimize) (Docs)
```

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Service Type | NodePort | Minikube limitation (no cloud LB) |
| Database | External (Neon) | No StatefulSet complexity |
| Dockerfile Gen | Gordon AI | Intelligent optimization |
| Helm Gen | kubectl-ai | Faster than manual (optional) |
| Image Pull | Never | Local images in Minikube |

---

## Environment Variables Required

```powershell
$env:DATABASE_URL = "postgresql://user:pass@host/db"
$env:BETTER_AUTH_SECRET = "your-auth-secret"
$env:OPENAI_API_KEY = "sk-your-openai-key"
```

---

## Cleanup Commands

```powershell
# Remove Helm release
helm uninstall taskflow

# Stop Minikube
minikube stop

# Delete cluster entirely
minikube delete

# Clean up Docker images (optional)
docker rmi modern-taskflow-frontend:latest modern-taskflow-backend:latest
```
