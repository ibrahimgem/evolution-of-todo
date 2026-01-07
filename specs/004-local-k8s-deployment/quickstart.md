# Quick Start Guide: Local Kubernetes Deployment

**Feature**: Phase IV - Local Kubernetes Deployment
**Date**: 2026-01-05

## Prerequisites

Before starting, ensure you have the following installed:

- **Docker**: Docker Desktop or Docker CLI (version 24.0+)
- **Minikube**: Local Kubernetes cluster (version 1.32+)
- **Helm**: Kubernetes package manager (version 3.15+)
- **kubectl**: Kubernetes command-line tool (version 1.29+)

### Check Prerequisites

```bash
# Check Docker
docker --version

# Check Minikube
minikube version

# Check Helm
helm version

# Check kubectl
kubectl version --client
```

## Quick Start (5 Minutes)

### Step 1: Start Minikube (30 seconds)

```bash
# Start Minikube with recommended resources
minikube start --cpus=4 --memory=8192 --disk-size=20000

# Enable ingress addon
minikube addons enable ingress
```

**Success indicators**:
- Minikube cluster started
- Kubernetes context is minikube
- Ingress addon enabled

---

### Step 2: Build Container Images (3 minutes)

```bash
# Configure Docker to use Minikube's daemon
eval $(minikube docker-env)

# Build frontend image (from project root)
docker build -t todo-chatbot-frontend:local \
  -f Phase-IV-Local-K8s-Deployment/images/frontend/Dockerfile \
  Phase-III-AI-Chatbot/frontend

# Build backend image
docker build -t todo-chatbot-backend:local \
  -f Phase-IV-Local-K8s-Deployment/images/backend/Dockerfile \
  Phase-III-AI-Chatbot/backend
```

**Success indicators**:
- Frontend image built successfully
- Backend image built successfully
- Both images visible in `docker images`
- Image sizes <500MB (frontend) and <600MB (backend)

---

### Step 3: Verify Images in Minikube (30 seconds)

```bash
# Images are already in Minikube's Docker daemon (via eval)
# Verify images are available
docker images | grep todo-chatbot
```

**Success indicators**:
- Both images visible in docker images output
- Images tagged with `:local`

---

### Step 4: Install Helm Chart (1 minute)

```bash
# Install Helm chart with local values (from project root)
helm install todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml \
  --set secrets.OPENAI_API_KEY="your-openai-api-key"

# Or install in separate namespace
kubectl create namespace todo-chatbot
helm install todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml \
  --namespace todo-chatbot
```

**Success indicators**:
- Release `todo-chatbot` created
- All pods in Running state
- Services created and accessible

---

### Step 5: Verify Deployment (30 seconds)

```bash
# Check pod status
kubectl get pods -n todo-chatbot

# Check service status
kubectl get svc -n todo-chatbot

# Get Minikube service URL
minikube service list -n todo-chatbot
```

**Success indicators**:
- Frontend pods: 2/2 Running
- Backend pods: 2/2 Running
- Frontend service: NodePort accessible
- Backend service: ClusterIP available

---

### Step 6: Access Application (30 seconds)

```bash
# Open application in browser
open $(minikube service todo-chatbot-frontend -n todo-chatbot --url)
```

**Success indicators**:
- Frontend loads in browser
- Can create todo via chat interface
- No errors in browser console

---

## Full Deployment Script

Automate the entire deployment with this script:

```bash
#!/bin/bash
# deploy-local.sh - Full Minikube deployment script

set -e

echo "=== Phase IV Todo Chatbot Minikube Deployment ==="
echo ""

# Step 1: Check prerequisites
echo "[1/6] Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not installed"
    exit 1
fi
if ! command -v minikube &> /dev/null; then
    echo "ERROR: Minikube not installed"
    exit 1
fi
if ! command -v helm &> /dev/null; then
    echo "ERROR: Helm not installed"
    exit 1
fi
echo "✓ Prerequisites OK"
echo ""

# Step 2: Start Minikube
echo "[2/6] Starting Minikube..."
minikube status | grep "Running" || minikube start --cpus=4 --memory=8192 --disk-size=20000
minikube addons enable ingress
echo "✓ Minikube running"
echo ""

# Step 3: Configure Docker and build images
echo "[3/6] Building container images..."
eval $(minikube docker-env)
docker build -t todo-chatbot-frontend:local \
  -f Phase-IV-Local-K8s-Deployment/images/frontend/Dockerfile \
  Phase-III-AI-Chatbot/frontend
docker build -t todo-chatbot-backend:local \
  -f Phase-IV-Local-K8s-Deployment/images/backend/Dockerfile \
  Phase-III-AI-Chatbot/backend
echo "✓ Images built"
echo ""

# Step 4: Verify images
echo "[4/6] Verifying images in Minikube..."
docker images | grep todo-chatbot
echo "✓ Images available"
echo ""

# Step 5: Install Helm chart
echo "[5/6] Installing Helm chart..."
kubectl create namespace todo-chatbot --dry-run=client || true
helm upgrade --install todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
    --namespace todo-chatbot \
    --values ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml
echo "✓ Helm chart installed"
echo ""

# Step 6: Verify deployment
echo "[6/6] Verifying deployment..."
kubectl wait --for=condition=ready pod --timeout=120s -n todo-chatbot -l app=todo-chatbot
kubectl get pods -n todo-chatbot
echo "✓ Deployment verified"
echo ""

# Step 7: Show access URL
echo "=== Access Application ==="
minikube service todo-chatbot-frontend -n todo-chatbot --url
echo ""
echo "Deployment complete!"
```

Save as `deploy-local.sh` and run:

```bash
chmod +x deploy-local.sh
./deploy-local.sh
```

---

## Common Commands

### View Logs

```bash
# Frontend logs
kubectl logs -n todo-chatbot -l app=todo-chatbot -l component=frontend

# Backend logs
kubectl logs -n todo-chatbot -l app=todo-chatbot -l component=backend
```

### Port Forwarding

```bash
# Forward frontend to localhost:3000
kubectl port-forward -n todo-chatbot svc/todo-chatbot-frontend 3000:3000

# Forward backend to localhost:8000
kubectl port-forward -n todo-chatbot svc/todo-chatbot-backend 8000:8000
```

### Cleanup

```bash
# Uninstall Helm chart
helm uninstall todo-chatbot -n todo-chatbot

# Delete namespace
kubectl delete namespace todo-chatbot

# Stop Minikube
minikube stop
```

---

## Troubleshooting

### Minikube won't start

```bash
# Check available resources
minikube start --cpus=2 --memory=4096  # Reduce if resources limited

# Use hyperkit driver on macOS (alternative to docker)
minikube start --driver=hyperkit
```

### Pods stuck in Pending

```bash
# Describe pod for details
kubectl describe pod -n todo-chatbot <pod-name>

# Check node events
kubectl get events -n todo-chatbot --sort-by=.metadata.creationTimestamp
```

### Images not loading

```bash
# Verify image exists
docker images | grep todo-chatbot

# Load image explicitly
minikube image load todo-chatbot-frontend:local-dev --daemon
```

---

## Next Steps

- Review full documentation in `docs/` directory
- Configure values in `values-local.yaml` for your environment
- Explore AI DevOps tools (kubectl-ai, Kagent, Docker AI)
- Prepare for Phase V: Cloud Deployment to DigitalOcean Kubernetes
