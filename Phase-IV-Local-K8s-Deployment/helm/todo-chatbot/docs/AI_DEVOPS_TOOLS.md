# AI-Assisted DevOps Tools Guide

<!--
[Task]: T034, T035, T036, T037, T038, T039, T040, T041
[From]: specs/004-local-k8s-deployment/spec.md §US4, §US5, plan.md §DD-005
-->

This guide documents AI-powered DevOps tools that enhance the Kubernetes deployment workflow for the Todo Chatbot application. All tools provide natural language interfaces with fallback to standard CLI commands.

## Table of Contents

- [Overview](#overview)
- [kubectl-ai](#kubectl-ai)
- [Kagent](#kagent)
- [Docker AI Agent (Gordon)](#docker-ai-agent-gordon)
- [CLI Fallback Commands](#cli-fallback-commands)
- [Troubleshooting](#troubleshooting)

---

## Overview

| Tool | Purpose | Installation Status | Fallback |
|------|---------|---------------------|----------|
| kubectl-ai | Natural language Kubernetes operations | Optional | kubectl |
| Kagent | AI-powered Kubernetes agent | Optional | kubectl + helm |
| Gordon | Docker AI assistant | Optional (Docker Desktop) | docker CLI |

**Note**: These tools are **optional enhancements**. All deployments can be completed using standard CLI commands.

---

## kubectl-ai

kubectl-ai is a kubectl plugin that uses OpenAI GPT to generate and execute Kubernetes manifests from natural language descriptions.

### Installation

```bash
# Using krew (kubectl plugin manager)
kubectl krew install ai

# Or using Homebrew (macOS)
brew install kubectl-ai

# Verify installation
kubectl ai --version
```

### Configuration

```bash
# Set OpenAI API key
export OPENAI_API_KEY="your-openai-api-key"

# Optional: Set default model
export KUBECTL_AI_MODEL="gpt-4"
```

### Usage Examples

#### Deployment Operations

```bash
# Natural Language: Deploy the todo chatbot frontend
kubectl ai "create a deployment for todo-chatbot-frontend with image todo-chatbot-frontend:local, 1 replica, port 3000"

# Natural Language: Scale the backend
kubectl ai "scale the todo-chatbot-backend deployment to 3 replicas"

# Natural Language: Check pod status
kubectl ai "show me all pods in the todo-chatbot application with their status"
```

#### Service Operations

```bash
# Natural Language: Create a NodePort service
kubectl ai "create a NodePort service for todo-chatbot-frontend on port 30080"

# Natural Language: Get service endpoints
kubectl ai "list all services and their endpoints for the todo-chatbot app"
```

#### Debugging Operations

```bash
# Natural Language: Debug failing pods
kubectl ai "why is the todo-chatbot-backend pod failing?"

# Natural Language: Get recent logs
kubectl ai "show me the last 100 lines of logs from the frontend pod"

# Natural Language: Describe resources
kubectl ai "describe the todo-chatbot-frontend deployment and show any issues"
```

### CLI Fallback

If kubectl-ai is not available, use standard kubectl commands:

```bash
# Instead of: kubectl ai "create deployment..."
kubectl apply -f k8s/frontend-deployment.yaml

# Instead of: kubectl ai "scale deployment..."
kubectl scale deployment todo-chatbot-backend --replicas=3

# Instead of: kubectl ai "show pods..."
kubectl get pods -l app=todo-chatbot -o wide

# Instead of: kubectl ai "show logs..."
kubectl logs -l app=todo-chatbot,component=frontend --tail=100
```

---

## Kagent

Kagent is an AI-powered Kubernetes management agent that provides intelligent cluster operations and recommendations.

### Installation

```bash
# Install via pip
pip install kagent

# Or via Homebrew
brew install kagent

# Verify installation
kagent --version
```

### Configuration

```bash
# Configure Kagent with your cluster
kagent init

# Set AI provider
export KAGENT_AI_PROVIDER="openai"
export OPENAI_API_KEY="your-openai-api-key"
```

### Usage Examples

#### Intelligent Deployment

```bash
# Deploy with AI optimization suggestions
kagent deploy ./helm/todo-chatbot --suggest-optimizations

# Auto-fix deployment issues
kagent fix deployment todo-chatbot-backend

# Get AI-powered recommendations
kagent recommend --namespace default
```

#### Resource Analysis

```bash
# Analyze resource usage
kagent analyze resources --app todo-chatbot

# Get scaling recommendations
kagent recommend scaling --deployment todo-chatbot-frontend

# Security audit
kagent audit security --namespace default
```

#### Troubleshooting

```bash
# AI-assisted debugging
kagent debug pod todo-chatbot-backend-xxxx

# Root cause analysis
kagent analyze failure --deployment todo-chatbot-backend

# Generate fix suggestions
kagent suggest fix --issue "CrashLoopBackOff"
```

### CLI Fallback

If Kagent is not available, use standard kubectl and helm commands:

```bash
# Instead of: kagent deploy...
helm install todo-chatbot ./helm/todo-chatbot -f values-local.yaml

# Instead of: kagent analyze resources...
kubectl top pods -l app=todo-chatbot
kubectl describe nodes

# Instead of: kagent debug pod...
kubectl describe pod <pod-name>
kubectl logs <pod-name> --previous

# Instead of: kagent audit security...
kubectl auth can-i --list
kubectl get networkpolicies
```

---

## Docker AI Agent (Gordon)

Gordon is Docker's AI assistant integrated into Docker Desktop that helps with container operations using natural language.

### Activation Requirements

1. **Docker Desktop 4.30+** with AI features enabled
2. **Docker subscription** (Pro, Team, or Business)
3. **AI features toggle** enabled in Docker Desktop settings

### Enabling Gordon

1. Open Docker Desktop
2. Go to **Settings** → **Features in development**
3. Enable **Docker AI (Gordon)**
4. Restart Docker Desktop

### Usage Examples

#### Container Operations

```bash
# Natural Language: Build the frontend image
docker ai "build the frontend image from Phase-III-AI-Chatbot/frontend with tag local"

# Natural Language: Run a container
docker ai "run the todo-chatbot-frontend image on port 3000"

# Natural Language: List containers
docker ai "show all running containers related to todo-chatbot"
```

#### Image Management

```bash
# Natural Language: Optimize Dockerfile
docker ai "analyze my frontend Dockerfile and suggest optimizations"

# Natural Language: Check image size
docker ai "show the size breakdown of todo-chatbot-frontend:local image"

# Natural Language: Security scan
docker ai "scan todo-chatbot-backend:local for vulnerabilities"
```

#### Troubleshooting

```bash
# Natural Language: Debug container crash
docker ai "why did the todo-chatbot-backend container exit?"

# Natural Language: Inspect networking
docker ai "show network configuration for todo-chatbot containers"

# Natural Language: Resource usage
docker ai "show CPU and memory usage for all todo-chatbot containers"
```

### CLI Fallback

If Gordon is not available, use standard Docker commands:

```bash
# Instead of: docker ai "build..."
docker build -t todo-chatbot-frontend:local -f Phase-IV-Local-K8s-Deployment/images/frontend/Dockerfile Phase-III-AI-Chatbot/frontend

# Instead of: docker ai "run..."
docker run -d -p 3000:3000 --name frontend todo-chatbot-frontend:local

# Instead of: docker ai "show containers..."
docker ps -a --filter "name=todo-chatbot"

# Instead of: docker ai "scan for vulnerabilities..."
docker scout cves todo-chatbot-backend:local

# Instead of: docker ai "show resource usage..."
docker stats --no-stream
```

---

## CLI Fallback Commands

Complete reference for standard CLI commands when AI tools are unavailable.

### Building Images

```bash
# Build frontend image
eval $(minikube docker-env)
docker build -t todo-chatbot-frontend:local \
  -f Phase-IV-Local-K8s-Deployment/images/frontend/Dockerfile \
  Phase-III-AI-Chatbot/frontend

# Build backend image
docker build -t todo-chatbot-backend:local \
  -f Phase-IV-Local-K8s-Deployment/images/backend/Dockerfile \
  Phase-III-AI-Chatbot/backend
```

### Deploying with Kubernetes

```bash
# Apply all manifests
kubectl apply -f Phase-IV-Local-K8s-Deployment/k8s/

# Or deploy individually
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/backend-service.yaml
```

### Deploying with Helm

```bash
# Install
helm install todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml

# Upgrade
helm upgrade todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml

# Uninstall
helm uninstall todo-chatbot
```

### Verification Commands

```bash
# Check pods
kubectl get pods -l app=todo-chatbot -w

# Check services
kubectl get svc -l app=todo-chatbot

# Check deployments
kubectl get deployments -l app=todo-chatbot

# View logs
kubectl logs -l app=todo-chatbot,component=frontend -f
kubectl logs -l app=todo-chatbot,component=backend -f

# Port forward
kubectl port-forward svc/todo-chatbot-frontend 3000:3000

# Access via Minikube
minikube service todo-chatbot-frontend --url
```

### Debugging Commands

```bash
# Describe pod
kubectl describe pod <pod-name>

# Get events
kubectl get events --sort-by='.lastTimestamp'

# Execute into container
kubectl exec -it <pod-name> -- /bin/sh

# Check resource usage
kubectl top pods -l app=todo-chatbot

# Check container logs
kubectl logs <pod-name> --previous
```

---

## Troubleshooting

### Common Issues and Solutions

#### kubectl-ai Not Generating Correct Manifests

**Problem**: kubectl-ai generates manifests that don't match requirements.

**Solution**:
1. Be more specific in your natural language prompt
2. Review generated manifest before applying: `kubectl ai "..." --dry-run`
3. Fall back to manual kubectl commands

#### Kagent Connection Issues

**Problem**: Kagent can't connect to the cluster.

**Solution**:
```bash
# Verify kubeconfig
kubectl config current-context

# Reinitialize Kagent
kagent init --reset

# Check cluster connectivity
kubectl cluster-info
```

#### Gordon Not Available

**Problem**: Docker AI features are not showing.

**Solution**:
1. Ensure Docker Desktop version 4.30+
2. Check subscription level (Pro/Team/Business required)
3. Enable AI features in Docker Desktop settings
4. Restart Docker Desktop

#### API Key Issues

**Problem**: AI tools fail with authentication errors.

**Solution**:
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Re-export if needed
export OPENAI_API_KEY="sk-..."

# Add to shell profile for persistence
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
```

### When to Use AI Tools vs CLI

| Scenario | Recommended Tool |
|----------|-----------------|
| Quick queries (pod status, logs) | kubectl-ai |
| Complex deployments | Helm CLI |
| Troubleshooting failures | Kagent or kubectl describe |
| Image building | Docker CLI |
| Image optimization | Gordon |
| Production deployments | Standard CLI (kubectl, helm) |

### Best Practices

1. **Always review AI-generated commands** before execution
2. **Use `--dry-run` flags** when available
3. **Keep fallback commands handy** for production environments
4. **Don't rely solely on AI tools** for critical operations
5. **Document custom prompts** that work well for your team

---

## Additional Resources

- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [Kagent Documentation](https://kagent.dev/docs)
- [Docker AI Assistant](https://docs.docker.com/desktop/ai/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
