# Minikube Setup Guide

<!--
[Task]: T042
[From]: specs/004-local-k8s-deployment/spec.md §US2, plan.md §DD-007
-->

This guide covers setting up Minikube for local Kubernetes development of the Todo Chatbot application.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Starting Minikube](#starting-minikube)
- [Configuring Docker Environment](#configuring-docker-environment)
- [Enabling Addons](#enabling-addons)
- [Verification](#verification)
- [Common Operations](#common-operations)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **CPU**: 2+ cores
- **Memory**: 4GB+ available RAM (8GB+ recommended)
- **Disk**: 20GB+ free space
- **OS**: macOS, Linux, or Windows with WSL2

### Required Software

- Docker Desktop or Docker Engine
- kubectl CLI
- Helm 3.x

### Verify Prerequisites

```bash
# Check Docker
docker --version
# Expected: Docker version 24.x.x or higher

# Check kubectl
kubectl version --client
# Expected: Client Version: v1.28.x or higher

# Check Helm
helm version
# Expected: version.BuildInfo{Version:"v3.x.x"...}
```

---

## Installation

### macOS (Homebrew)

```bash
brew install minikube

# Verify installation
minikube version
```

### macOS (Direct Download)

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-darwin-arm64
sudo install minikube-darwin-arm64 /usr/local/bin/minikube
```

### Linux (Direct Download)

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### Windows (PowerShell as Admin)

```powershell
winget install Kubernetes.minikube
```

---

## Starting Minikube

### Basic Start

```bash
# Start with default settings
minikube start

# Start with specific resources
minikube start --cpus=4 --memory=8192
```

### Recommended Configuration for Todo Chatbot

```bash
# Start with Docker driver (recommended)
minikube start \
  --driver=docker \
  --cpus=4 \
  --memory=8192 \
  --disk-size=30g \
  --kubernetes-version=v1.28.0

# Verify cluster is running
minikube status
```

### Expected Output

```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

---

## Configuring Docker Environment

To build images directly in Minikube's Docker daemon (avoiding image push/pull):

### Set Docker Environment

```bash
# Point shell to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify Docker is using Minikube
docker info | grep -i name
# Should show: minikube
```

### Persist Across Sessions

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# Auto-configure Minikube Docker env if Minikube is running
if minikube status &>/dev/null; then
  eval $(minikube docker-env)
fi
```

### Reset to Host Docker

```bash
# Unset Minikube Docker environment
eval $(minikube docker-env -u)
```

---

## Enabling Addons

### Required Addons

```bash
# Enable ingress controller
minikube addons enable ingress

# Enable metrics server (for kubectl top)
minikube addons enable metrics-server

# Enable dashboard (optional but useful)
minikube addons enable dashboard
```

### List Available Addons

```bash
minikube addons list
```

### Verify Addons

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check metrics server
kubectl get pods -n kube-system | grep metrics
```

---

## Verification

### Verify Cluster Access

```bash
# Check nodes
kubectl get nodes
# Expected: minikube   Ready    control-plane   ...

# Check system pods
kubectl get pods -n kube-system
# All pods should be Running

# Check cluster info
kubectl cluster-info
```

### Test Deployment

```bash
# Deploy test application
kubectl create deployment hello-minikube --image=kicbase/echo-server:1.0

# Expose service
kubectl expose deployment hello-minikube --type=NodePort --port=8080

# Access service
minikube service hello-minikube --url

# Cleanup
kubectl delete deployment hello-minikube
kubectl delete service hello-minikube
```

---

## Common Operations

### Starting and Stopping

```bash
# Start cluster
minikube start

# Stop cluster (preserves state)
minikube stop

# Pause cluster (lower resource usage)
minikube pause

# Unpause cluster
minikube unpause
```

### Accessing Services

```bash
# Get service URL
minikube service <service-name> --url

# Open service in browser
minikube service <service-name>

# Create tunnel for LoadBalancer services
minikube tunnel
```

### Dashboard

```bash
# Open Kubernetes dashboard
minikube dashboard

# Get dashboard URL without opening browser
minikube dashboard --url
```

### SSH Access

```bash
# SSH into Minikube VM
minikube ssh

# Run command in Minikube
minikube ssh -- docker images
```

### Logs

```bash
# View Minikube logs
minikube logs

# Follow logs
minikube logs -f
```

### Cleanup

```bash
# Delete cluster
minikube delete

# Delete all clusters
minikube delete --all

# Purge Minikube completely
minikube delete --purge
```

---

## Troubleshooting

### Minikube Won't Start

**Problem**: `minikube start` fails

**Solutions**:

```bash
# Clean start
minikube delete
minikube start --driver=docker

# Check Docker is running
docker info

# Try different driver
minikube start --driver=virtualbox
```

### Insufficient Resources

**Problem**: Pods stuck in Pending state

**Solution**:

```bash
# Increase resources
minikube stop
minikube config set cpus 4
minikube config set memory 8192
minikube start
```

### kubectl Can't Connect

**Problem**: `kubectl` commands fail with connection errors

**Solutions**:

```bash
# Update kubeconfig
minikube update-context

# Verify context
kubectl config current-context
# Should be: minikube

# Check Minikube status
minikube status
```

### Docker Images Not Found

**Problem**: `ImagePullBackOff` errors

**Solutions**:

```bash
# Ensure using Minikube's Docker
eval $(minikube docker-env)

# Rebuild images
docker build -t <image-name>:local ...

# Use imagePullPolicy: Never in deployments
```

### Ingress Not Working

**Problem**: Ingress resources not routing traffic

**Solutions**:

```bash
# Verify ingress addon
minikube addons enable ingress

# Check ingress controller pods
kubectl get pods -n ingress-nginx

# Get Minikube IP
minikube ip

# Add to /etc/hosts
echo "$(minikube ip) todo-chatbot.local" | sudo tee -a /etc/hosts
```

### Port Already in Use

**Problem**: NodePort conflicts

**Solutions**:

```bash
# Find process using port
lsof -i :30080

# Kill process or use different NodePort
# Update service to use different port
```

---

## Resource Configuration Reference

### Recommended Settings

| Setting | Development | Production-like |
|---------|-------------|-----------------|
| CPUs | 2 | 4+ |
| Memory | 4096 MB | 8192+ MB |
| Disk | 20 GB | 40+ GB |
| Driver | docker | docker |

### Configuration Commands

```bash
# View current config
minikube config view

# Set defaults
minikube config set cpus 4
minikube config set memory 8192
minikube config set driver docker
```

---

## Next Steps

After setting up Minikube:

1. [Build Docker images](./DEPLOYMENT.md#building-docker-images)
2. [Deploy with Helm](./DEPLOYMENT.md#helm-deployment)
3. [Verify deployment](./DEPLOYMENT.md#verification)
