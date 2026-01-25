#!/bin/bash
# Deploy Modern TaskFlow to Minikube
# Usage: ./scripts/deploy-minikube.sh

set -e

echo "🚀 Modern TaskFlow - Minikube Deployment"
echo "========================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v minikube &> /dev/null; then
    echo "❌ minikube is not installed. Please install it first."
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ helm is not installed. Please install it first."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ docker is not installed. Please install it first."
    exit 1
fi

echo "✅ All prerequisites found"

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "📦 Starting Minikube..."
    minikube start --driver=docker
fi

echo "✅ Minikube is running"

# Configure docker to use minikube's docker daemon
echo "🔧 Configuring Docker to use Minikube's daemon..."
eval $(minikube docker-env)

# Build Docker images
echo "🏗️  Building Docker images..."

echo "   Building backend image..."
docker build -t modern-taskflow-backend:latest ./backend

echo "   Building frontend image..."
docker build -t modern-taskflow-frontend:latest ./frontend \
    --build-arg DATABASE_URL="${DATABASE_URL}" \
    --build-arg BETTER_AUTH_SECRET="${BETTER_AUTH_SECRET}" \
    --build-arg NEXT_PUBLIC_API_URL="http://backend:8000"

echo "✅ Docker images built"

# Check if secrets are set
if [ -z "$DATABASE_URL" ] || [ -z "$BETTER_AUTH_SECRET" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  Warning: Environment variables not set!"
    echo "   Please set the following before deploying:"
    echo "   - DATABASE_URL"
    echo "   - BETTER_AUTH_SECRET"
    echo "   - OPENAI_API_KEY"
    echo ""
    echo "   Example:"
    echo "   export DATABASE_URL='postgresql://...'"
    echo "   export BETTER_AUTH_SECRET='your-secret'"
    echo "   export OPENAI_API_KEY='sk-...'"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Deploy with Helm
echo "📦 Deploying with Helm..."

# Check if release exists
if helm status taskflow &> /dev/null; then
    echo "   Upgrading existing release..."
    helm upgrade taskflow ./helm-chart \
        -f ./helm-chart/values-local.yaml \
        --set secrets.databaseUrl="${DATABASE_URL}" \
        --set secrets.betterAuthSecret="${BETTER_AUTH_SECRET}" \
        --set secrets.openaiApiKey="${OPENAI_API_KEY}"
else
    echo "   Installing new release..."
    helm install taskflow ./helm-chart \
        -f ./helm-chart/values-local.yaml \
        --set secrets.databaseUrl="${DATABASE_URL}" \
        --set secrets.betterAuthSecret="${BETTER_AUTH_SECRET}" \
        --set secrets.openaiApiKey="${OPENAI_API_KEY}"
fi

echo "✅ Helm deployment complete"

# Wait for pods to be ready
echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=taskflow --timeout=120s

# Get access URL
echo ""
echo "========================================="
echo "🎉 Deployment Complete!"
echo "========================================="
echo ""
MINIKUBE_IP=$(minikube ip)
echo "🌐 Access the application at:"
echo "   http://${MINIKUBE_IP}:30080"
echo ""
echo "   Or run: minikube service taskflow-frontend"
echo ""
echo "📊 Check pod status:"
echo "   kubectl get pods -l app.kubernetes.io/instance=taskflow"
echo ""
echo "📜 View logs:"
echo "   kubectl logs -l app.kubernetes.io/component=frontend -f"
echo "   kubectl logs -l app.kubernetes.io/component=backend -f"
echo ""
