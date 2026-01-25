# Deploy Modern TaskFlow to Minikube (Windows PowerShell)
# Usage: .\scripts\deploy-minikube.ps1

$ErrorActionPreference = "Stop"

Write-Host "🚀 Modern TaskFlow - Minikube Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check prerequisites
Write-Host "📋 Checking prerequisites..." -ForegroundColor Yellow

$commands = @("minikube", "helm", "docker")
foreach ($cmd in $commands) {
    if (!(Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "❌ $cmd is not installed. Please install it first." -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ All prerequisites found" -ForegroundColor Green

# Check if minikube is running
$minikubeStatus = minikube status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 Starting Minikube..." -ForegroundColor Yellow
    minikube start --driver=docker
}
Write-Host "✅ Minikube is running" -ForegroundColor Green

# Configure docker to use minikube's docker daemon
Write-Host "🔧 Configuring Docker to use Minikube's daemon..." -ForegroundColor Yellow
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build Docker images
Write-Host "🏗️  Building Docker images..." -ForegroundColor Yellow

Write-Host "   Building backend image..." -ForegroundColor Gray
docker build -t modern-taskflow-backend:latest ./backend

Write-Host "   Building frontend image..." -ForegroundColor Gray
$buildArgs = @(
    "--build-arg", "DATABASE_URL=$env:DATABASE_URL",
    "--build-arg", "BETTER_AUTH_SECRET=$env:BETTER_AUTH_SECRET",
    "--build-arg", "NEXT_PUBLIC_API_URL=http://backend:8000"
)
docker build -t modern-taskflow-frontend:latest ./frontend @buildArgs

Write-Host "✅ Docker images built" -ForegroundColor Green

# Check if secrets are set
if ([string]::IsNullOrEmpty($env:DATABASE_URL) -or
    [string]::IsNullOrEmpty($env:BETTER_AUTH_SECRET) -or
    [string]::IsNullOrEmpty($env:OPENAI_API_KEY)) {

    Write-Host ""
    Write-Host "⚠️  Warning: Environment variables not set!" -ForegroundColor Yellow
    Write-Host "   Please set the following before deploying:"
    Write-Host "   - DATABASE_URL"
    Write-Host "   - BETTER_AUTH_SECRET"
    Write-Host "   - OPENAI_API_KEY"
    Write-Host ""
    Write-Host "   Example (PowerShell):"
    Write-Host '   $env:DATABASE_URL = "postgresql://..."'
    Write-Host '   $env:BETTER_AUTH_SECRET = "your-secret"'
    Write-Host '   $env:OPENAI_API_KEY = "sk-..."'
    Write-Host ""

    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Deploy with Helm
Write-Host "📦 Deploying with Helm..." -ForegroundColor Yellow

$helmStatus = helm status taskflow 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   Upgrading existing release..." -ForegroundColor Gray
    helm upgrade taskflow ./helm-chart `
        -f ./helm-chart/values-local.yaml `
        --set "secrets.databaseUrl=$env:DATABASE_URL" `
        --set "secrets.betterAuthSecret=$env:BETTER_AUTH_SECRET" `
        --set "secrets.openaiApiKey=$env:OPENAI_API_KEY"
} else {
    Write-Host "   Installing new release..." -ForegroundColor Gray
    helm install taskflow ./helm-chart `
        -f ./helm-chart/values-local.yaml `
        --set "secrets.databaseUrl=$env:DATABASE_URL" `
        --set "secrets.betterAuthSecret=$env:BETTER_AUTH_SECRET" `
        --set "secrets.openaiApiKey=$env:OPENAI_API_KEY"
}

Write-Host "✅ Helm deployment complete" -ForegroundColor Green

# Wait for pods to be ready
Write-Host "⏳ Waiting for pods to be ready..." -ForegroundColor Yellow
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=taskflow --timeout=120s

# Get access URL
$minikubeIp = minikube ip

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Access the application at:" -ForegroundColor Yellow
Write-Host "   http://${minikubeIp}:30080"
Write-Host ""
Write-Host "   Or run: minikube service taskflow-frontend"
Write-Host ""
Write-Host "📊 Check pod status:" -ForegroundColor Yellow
Write-Host "   kubectl get pods -l app.kubernetes.io/instance=taskflow"
Write-Host ""
Write-Host "📜 View logs:" -ForegroundColor Yellow
Write-Host "   kubectl logs -l app.kubernetes.io/component=frontend -f"
Write-Host "   kubectl logs -l app.kubernetes.io/component=backend -f"
Write-Host ""
