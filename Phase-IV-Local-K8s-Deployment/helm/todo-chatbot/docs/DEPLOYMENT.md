# Deployment Guide

<!--
[Task]: T043
[From]: specs/004-local-k8s-deployment/spec.md §US2, §US3, plan.md
-->

Complete step-by-step guide for deploying the Todo Chatbot application to local Kubernetes using Minikube.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Building Docker Images](#building-docker-images)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Helm Deployment](#helm-deployment)
- [Verification](#verification)
- [Accessing the Application](#accessing-the-application)
- [Updating the Deployment](#updating-the-deployment)
- [Cleanup](#cleanup)

---

## Prerequisites

Before deploying, ensure you have:

1. **Minikube running**: See [MINIKUBE_SETUP.md](./MINIKUBE_SETUP.md)
2. **Docker configured for Minikube**: `eval $(minikube docker-env)`
3. **kubectl connected**: `kubectl cluster-info`
4. **Helm installed**: `helm version`

### Verify Environment

```bash
# Check Minikube is running
minikube status

# Ensure Docker uses Minikube
eval $(minikube docker-env)
docker info | grep -i name

# Verify kubectl context
kubectl config current-context
# Should output: minikube
```

---

## Quick Start

For those familiar with the deployment process:

```bash
# 1. Configure Docker for Minikube
eval $(minikube docker-env)

# 2. Build images
docker build -t todo-chatbot-frontend:local -f Phase-IV-Local-K8s-Deployment/images/frontend/Dockerfile Phase-III-AI-Chatbot/frontend
docker build -t todo-chatbot-backend:local -f Phase-IV-Local-K8s-Deployment/images/backend/Dockerfile Phase-III-AI-Chatbot/backend

# 3. Deploy with Helm
helm install todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml \
  --set secrets.OPENAI_API_KEY="your-api-key"

# 4. Access application
minikube service todo-chatbot-frontend --url
```

---

## Building Docker Images

### Step 1: Configure Docker Environment

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify
docker info | grep -i name
# Output should include: minikube
```

### Step 2: Build Frontend Image

```bash
# Navigate to project root
cd /path/to/02-evolution-of-todo

# Build frontend image
docker build \
  -t todo-chatbot-frontend:local \
  -f Phase-IV-Local-K8s-Deployment/images/frontend/Dockerfile \
  Phase-III-AI-Chatbot/frontend

# Verify image
docker images | grep todo-chatbot-frontend
```

### Step 3: Build Backend Image

```bash
# Build backend image
docker build \
  -t todo-chatbot-backend:local \
  -f Phase-IV-Local-K8s-Deployment/images/backend/Dockerfile \
  Phase-III-AI-Chatbot/backend

# Verify image
docker images | grep todo-chatbot-backend
```

### Verify Images

```bash
# List todo-chatbot images
docker images | grep todo-chatbot

# Expected output:
# todo-chatbot-frontend   local   xxxxx   xx seconds ago   xxx MB
# todo-chatbot-backend    local   xxxxx   xx seconds ago   xxx MB
```

---

## Kubernetes Deployment

Deploy using raw Kubernetes manifests (without Helm).

### Step 1: Apply ConfigMap and Secret

```bash
# Create ConfigMap
kubectl apply -f Phase-IV-Local-K8s-Deployment/k8s/configmap.yaml

# Create Secret (update values first!)
kubectl apply -f Phase-IV-Local-K8s-Deployment/k8s/secret.yaml

# Verify
kubectl get configmaps,secrets | grep todo-chatbot
```

### Step 2: Deploy Backend

```bash
# Deploy backend
kubectl apply -f Phase-IV-Local-K8s-Deployment/k8s/backend-deployment.yaml
kubectl apply -f Phase-IV-Local-K8s-Deployment/k8s/backend-service.yaml

# Wait for ready
kubectl wait --for=condition=available deployment/todo-chatbot-backend --timeout=120s
```

### Step 3: Deploy Frontend

```bash
# Deploy frontend
kubectl apply -f Phase-IV-Local-K8s-Deployment/k8s/frontend-deployment.yaml
kubectl apply -f Phase-IV-Local-K8s-Deployment/k8s/frontend-service.yaml

# Wait for ready
kubectl wait --for=condition=available deployment/todo-chatbot-frontend --timeout=120s
```

### Step 4: Verify Deployment

```bash
# Check all resources
kubectl get all -l app=todo-chatbot
```

---

## Helm Deployment

Deploy using Helm charts (recommended).

### Step 1: Review Values

```bash
# View default values
cat Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values.yaml

# View local overrides
cat Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml
```

### Step 2: Install Chart

```bash
# Basic installation
helm install todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml

# With OpenAI API key
helm install todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml \
  --set secrets.OPENAI_API_KEY="sk-your-api-key"

# With custom namespace
helm install todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml \
  --namespace todo-chatbot --create-namespace
```

### Step 3: View Installation Notes

The installation will display post-install notes with access instructions.

```bash
# View notes again
helm get notes todo-chatbot
```

### Step 4: Verify Installation

```bash
# Check release status
helm status todo-chatbot

# List releases
helm list

# View deployed values
helm get values todo-chatbot
```

---

## Verification

### Check Pod Status

```bash
# List pods
kubectl get pods -l app=todo-chatbot

# Expected output:
# NAME                                      READY   STATUS    RESTARTS   AGE
# todo-chatbot-frontend-xxxxx-xxxxx         1/1     Running   0          1m
# todo-chatbot-backend-xxxxx-xxxxx          1/1     Running   0          1m

# Watch pods
kubectl get pods -l app=todo-chatbot -w
```

### Check Services

```bash
# List services
kubectl get svc -l app=todo-chatbot

# Expected output:
# NAME                      TYPE        CLUSTER-IP      PORT(S)
# todo-chatbot-frontend     NodePort    10.x.x.x        3000:30080/TCP
# todo-chatbot-backend      ClusterIP   10.x.x.x        8000/TCP
```

### Check Logs

```bash
# Frontend logs
kubectl logs -l app=todo-chatbot,component=frontend -f

# Backend logs
kubectl logs -l app=todo-chatbot,component=backend -f
```

### Health Checks

```bash
# Port forward to frontend
kubectl port-forward svc/todo-chatbot-frontend 3000:3000 &

# Check frontend health
curl http://localhost:3000/api/healthz
# Expected: {"status":"healthy",...}

# Port forward to backend
kubectl port-forward svc/todo-chatbot-backend 8000:8000 &

# Check backend health
curl http://localhost:8000/api/health
# Expected: {"status":"healthy",...}
```

---

## Accessing the Application

### Method 1: Minikube Service (Recommended)

```bash
# Get URL and open browser
minikube service todo-chatbot-frontend

# Get URL only
minikube service todo-chatbot-frontend --url
```

### Method 2: NodePort Direct Access

```bash
# Get Minikube IP
minikube ip

# Access via NodePort
# http://<minikube-ip>:30080
```

### Method 3: Port Forwarding

```bash
# Forward frontend port
kubectl port-forward svc/todo-chatbot-frontend 3000:3000

# Access at http://localhost:3000
```

### Method 4: Minikube Tunnel (LoadBalancer)

```bash
# Start tunnel (requires sudo)
minikube tunnel

# Services of type LoadBalancer will get external IPs
kubectl get svc
```

---

## Updating the Deployment

### Update Values

```bash
# Update with new values
helm upgrade todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml \
  --set secrets.OPENAI_API_KEY="new-api-key"
```

### Update Images

```bash
# Rebuild images
docker build -t todo-chatbot-frontend:local ...
docker build -t todo-chatbot-backend:local ...

# Restart deployments to pick up new images
kubectl rollout restart deployment/todo-chatbot-frontend
kubectl rollout restart deployment/todo-chatbot-backend

# Or with different tag
helm upgrade todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  --set frontend.image.tag=v2 \
  --set backend.image.tag=v2
```

### Rollback

```bash
# View history
helm history todo-chatbot

# Rollback to previous release
helm rollback todo-chatbot

# Rollback to specific revision
helm rollback todo-chatbot 1
```

---

## Cleanup

### Remove Helm Release

```bash
# Uninstall release
helm uninstall todo-chatbot

# Verify removal
kubectl get all -l app=todo-chatbot
```

### Remove Kubernetes Resources

```bash
# Delete all resources
kubectl delete -f Phase-IV-Local-K8s-Deployment/k8s/
```

### Remove Images

```bash
# Remove images from Minikube
eval $(minikube docker-env)
docker rmi todo-chatbot-frontend:local
docker rmi todo-chatbot-backend:local
```

### Stop Minikube

```bash
# Stop cluster
minikube stop

# Delete cluster
minikube delete
```

---

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API URL for frontend | http://todo-chatbot-backend:8000 |
| DATABASE_HOST | PostgreSQL host | host.minikube.internal |
| DATABASE_PORT | PostgreSQL port | 5432 |
| DATABASE_NAME | Database name | todo_chatbot |
| OPENAI_API_KEY | OpenAI API key | (required) |
| JWT_SECRET | JWT signing secret | (required for production) |

### Resource Limits

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| Frontend | 50m | 300m | 64Mi | 256Mi |
| Backend | 50m | 300m | 64Mi | 256Mi |

---

## Next Steps

- [Troubleshooting Guide](./TROUBLESHOOTING.md)
- [AI DevOps Tools](./AI_DEVOPS_TOOLS.md)
