# Quickstart: Phase 5B - Event-Driven Architecture

**Date**: 2026-02-08
**Feature**: 002-event-driven-kafka-dapr

## Prerequisites

- Docker Desktop running
- Minikube installed and started (`minikube start --memory=6144 --cpus=4`)
- Helm 3 installed
- Dapr CLI installed (`winget install Dapr.CLI` or `choco install dapr-cli`)
- kubectl configured to Minikube context

## Step-by-Step Setup

### 1. Start Minikube (if not running)

```bash
minikube start --memory=6144 --cpus=4 --driver=docker
```

### 2. Install Dapr on Minikube

```bash
dapr init -k
# Verify:
dapr status -k
# All components should show "Running"
```

### 3. Deploy Redpanda (Kafka)

```bash
kubectl apply -f k8s/redpanda/
# Wait for pod:
kubectl wait --for=condition=ready pod -l app=redpanda --timeout=120s
```

### 4. Create Kafka Topics

```bash
kubectl exec -it redpanda-0 -- rpk topic create task-events --partitions 3
kubectl exec -it redpanda-0 -- rpk topic create reminders --partitions 1
kubectl exec -it redpanda-0 -- rpk topic create task-updates --partitions 3
# Verify:
kubectl exec -it redpanda-0 -- rpk topic list
```

### 5. Deploy Dapr Components

```bash
kubectl apply -f k8s/dapr-components/
# Verify components loaded:
kubectl get components.dapr.io
```

### 6. Deploy Dapr Subscriptions

```bash
kubectl apply -f k8s/subscriptions/
# Verify:
kubectl get subscriptions.dapr.io
```

### 7. Build Service Docker Images (in minikube docker env)

```bash
# Switch to minikube Docker
eval $(minikube docker-env)

# Build backend v4 (with event publishing)
docker build -t modern-taskflow-backend:v4 backend/

# Build notification service
docker build -t notification-service:v1 services/notification-service/

# Build recurring service
docker build -t recurring-service:v1 services/recurring-service/

# Build audit service
docker build -t audit-service:v1 services/audit-service/
```

### 8. Deploy All Services

```bash
helm upgrade taskflow helm-chart/ -f helm-chart/values-local.yaml \
  --set secrets.databaseUrl="<your-database-url>" \
  --set secrets.betterAuthSecret="<your-secret>" \
  --set secrets.openaiApiKey="<your-api-key>"
```

### 9. Verify Deployment

```bash
# Check all pods have 2/2 containers (app + daprd sidecar)
kubectl get pods

# Check Dapr sidecar logs for any errors
kubectl logs <backend-pod> -c daprd | tail -20

# Check Dapr status
dapr status -k
```

### 10. Port-Forward and Test

```bash
# Port-forward backend
kubectl port-forward svc/taskflow-backend 30081:8000 &

# Port-forward frontend
kubectl port-forward svc/taskflow-frontend 30080:3000 &

# Create a task and check events
curl -X POST http://localhost:30081/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Event","priority":"high","due_date":"2026-02-15T12:00:00Z","recurring_pattern":"daily"}'

# Check Kafka for published event
kubectl exec -it redpanda-0 -- rpk topic consume task-events --num 1

# Check notification service logs
kubectl logs -l app.kubernetes.io/component=notification-service -c notification-service

# Check recurring service logs
kubectl logs -l app.kubernetes.io/component=recurring-service -c recurring-service
```

## Verification Checklist

- [ ] `dapr status -k` shows all components Running
- [ ] Redpanda pod is Running (1/1)
- [ ] `rpk topic list` shows 3 topics
- [ ] Backend pod shows 2/2 containers (app + daprd)
- [ ] Creating a task produces event in `task-events` topic
- [ ] Task with due_date produces event in `reminders` topic
- [ ] Completing a recurring task creates next instance
- [ ] Notification service logs reminders
- [ ] Audit service logs all events
- [ ] Existing functionality (CRUD, chatbot) still works

## Troubleshooting

**Dapr sidecar not injecting**: Check `dapr.io/enabled: "true"` annotation on pod template (not deployment)

**Redpanda connection refused**: Verify service name `redpanda.default.svc.cluster.local:9092` in Dapr component

**Events not flowing**: Check Dapr sidecar logs: `kubectl logs <pod> -c daprd`

**Subscription not working**: Verify `scopes` in subscription match the `dapr.io/app-id` annotation
