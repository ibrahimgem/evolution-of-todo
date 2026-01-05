# Troubleshooting Guide

<!--
[Task]: T045
[From]: specs/004-local-k8s-deployment/spec.md, plan.md
-->

Common issues and solutions when deploying the Todo Chatbot to local Kubernetes.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Pod Issues](#pod-issues)
- [Service Issues](#service-issues)
- [Image Issues](#image-issues)
- [Configuration Issues](#configuration-issues)
- [Database Issues](#database-issues)
- [Network Issues](#network-issues)
- [Helm Issues](#helm-issues)
- [Minikube Issues](#minikube-issues)

---

## Quick Diagnostics

Run these commands first to identify issues:

```bash
# Check overall status
kubectl get all -l app=todo-chatbot

# Check pod events
kubectl describe pods -l app=todo-chatbot

# Check recent events
kubectl get events --sort-by='.lastTimestamp' | head -20

# Check logs
kubectl logs -l app=todo-chatbot --all-containers --tail=50
```

---

## Pod Issues

### Pod Stuck in Pending

**Symptoms**: Pod status shows `Pending`

**Causes & Solutions**:

1. **Insufficient Resources**
   ```bash
   # Check node resources
   kubectl describe nodes | grep -A 5 "Allocated resources"

   # Solution: Increase Minikube resources
   minikube stop
   minikube config set cpus 4
   minikube config set memory 8192
   minikube start
   ```

2. **No Schedulable Nodes**
   ```bash
   # Check node status
   kubectl get nodes

   # Uncordon node if cordoned
   kubectl uncordon minikube
   ```

### Pod in CrashLoopBackOff

**Symptoms**: Pod keeps restarting

**Diagnosis**:
```bash
# Check container logs
kubectl logs <pod-name> --previous

# Describe pod for events
kubectl describe pod <pod-name>
```

**Common Causes**:

1. **Application Error**
   ```bash
   # Check application logs
   kubectl logs <pod-name> -f
   ```

2. **Missing Environment Variables**
   ```bash
   # Verify secrets exist
   kubectl get secrets todo-chatbot-secret -o yaml

   # Check ConfigMap
   kubectl get configmap todo-chatbot-config -o yaml
   ```

3. **Health Check Failing**
   ```bash
   # Exec into container to test health endpoint
   kubectl exec -it <pod-name> -- curl localhost:3000/api/healthz
   ```

### Pod in ImagePullBackOff

**Symptoms**: `ImagePullBackOff` or `ErrImagePull`

**Solutions**:

```bash
# Ensure using Minikube's Docker daemon
eval $(minikube docker-env)

# Rebuild the image
docker build -t todo-chatbot-frontend:local ...

# Verify image exists in Minikube
docker images | grep todo-chatbot

# Ensure imagePullPolicy: Never in deployment
kubectl get deployment todo-chatbot-frontend -o yaml | grep imagePullPolicy
```

### Pod OOMKilled

**Symptoms**: Pod status shows `OOMKilled`

**Solution**:
```bash
# Increase memory limits
helm upgrade todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  --set frontend.resources.limits.memory=512Mi \
  --set backend.resources.limits.memory=512Mi
```

---

## Service Issues

### Service Not Accessible

**Symptoms**: Cannot connect to service URL

**Diagnosis**:
```bash
# Check service exists
kubectl get svc todo-chatbot-frontend

# Check endpoints
kubectl get endpoints todo-chatbot-frontend

# Verify pod labels match selector
kubectl get pods --show-labels | grep todo-chatbot
```

**Solutions**:

1. **No Endpoints**
   ```bash
   # Pods may not be running or labels don't match
   kubectl describe svc todo-chatbot-frontend
   ```

2. **NodePort Not Accessible**
   ```bash
   # Get Minikube IP
   MINIKUBE_IP=$(minikube ip)

   # Test directly
   curl http://$MINIKUBE_IP:30080

   # Or use minikube service
   minikube service todo-chatbot-frontend --url
   ```

### Frontend Cannot Reach Backend

**Symptoms**: API calls fail with network errors

**Diagnosis**:
```bash
# Check backend service DNS
kubectl exec -it <frontend-pod> -- nslookup todo-chatbot-backend

# Test backend connection from frontend
kubectl exec -it <frontend-pod> -- curl http://todo-chatbot-backend:8000/api/health
```

**Solutions**:

1. **DNS Not Resolving**
   ```bash
   # Check CoreDNS pods
   kubectl get pods -n kube-system -l k8s-app=kube-dns
   ```

2. **Wrong Service Name**
   ```bash
   # Verify NEXT_PUBLIC_API_URL
   kubectl get configmap todo-chatbot-config -o yaml
   ```

---

## Image Issues

### Image Not Found

**Symptoms**: `ImagePullBackOff` error

**Solution**:
```bash
# 1. Set Docker to use Minikube
eval $(minikube docker-env)

# 2. Verify you're using Minikube's Docker
docker info | grep -i name

# 3. Build images
docker build -t todo-chatbot-frontend:local -f Phase-IV-Local-K8s-Deployment/images/frontend/Dockerfile Phase-III-AI-Chatbot/frontend

# 4. Verify image exists
docker images | grep todo-chatbot-frontend

# 5. Ensure imagePullPolicy: Never
```

### Old Image Being Used

**Symptoms**: Changes not reflected in deployment

**Solution**:
```bash
# Force restart to pull new image
kubectl rollout restart deployment/todo-chatbot-frontend
kubectl rollout restart deployment/todo-chatbot-backend

# Or delete pods to force recreation
kubectl delete pods -l app=todo-chatbot
```

---

## Configuration Issues

### Missing Secret Values

**Symptoms**: Application fails to start, missing environment variables

**Diagnosis**:
```bash
# Check secret exists
kubectl get secret todo-chatbot-secret

# View secret values (base64 encoded)
kubectl get secret todo-chatbot-secret -o yaml
```

**Solution**:
```bash
# Update secrets via Helm
helm upgrade todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  --set secrets.OPENAI_API_KEY="your-api-key" \
  --set secrets.JWT_SECRET="your-jwt-secret"
```

### Wrong ConfigMap Values

**Symptoms**: Application connects to wrong services

**Diagnosis**:
```bash
# View ConfigMap
kubectl get configmap todo-chatbot-config -o yaml
```

**Solution**:
```bash
# Update ConfigMap via Helm
helm upgrade todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  --set config.DATABASE_HOST="correct-host"
```

---

## Database Issues

### Cannot Connect to Database

**Symptoms**: Backend fails with database connection errors

**Diagnosis**:
```bash
# Check backend logs
kubectl logs -l app=todo-chatbot,component=backend | grep -i database

# Test database connectivity from backend pod
kubectl exec -it <backend-pod> -- python -c "
import os
host = os.environ.get('DATABASE_HOST')
port = os.environ.get('DATABASE_PORT')
print(f'Database: {host}:{port}')
"
```

**Solutions**:

1. **External Database (Recommended for Local)**
   ```bash
   # Ensure database is running on host
   # PostgreSQL should be accessible at host.minikube.internal

   # Verify host.minikube.internal resolves
   kubectl exec -it <backend-pod> -- ping -c 1 host.minikube.internal
   ```

2. **In-Cluster Database**
   ```bash
   # Deploy PostgreSQL in cluster
   helm install postgres bitnami/postgresql

   # Update backend config to use in-cluster PostgreSQL
   ```

---

## Network Issues

### Port Conflicts

**Symptoms**: NodePort already in use

**Diagnosis**:
```bash
# Check what's using the port
lsof -i :30080
```

**Solution**:
```bash
# Use different NodePort
helm upgrade todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  --set frontend.service.nodePort=30081
```

### Minikube Tunnel Issues

**Symptoms**: LoadBalancer services stuck in `<pending>`

**Solution**:
```bash
# Start Minikube tunnel (requires sudo)
minikube tunnel

# Keep tunnel running in separate terminal
```

---

## Helm Issues

### Release Already Exists

**Symptoms**: `Error: cannot re-use a name that is still in use`

**Solution**:
```bash
# Uninstall existing release
helm uninstall todo-chatbot

# Or use upgrade with install flag
helm upgrade --install todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot
```

### Values Not Applied

**Symptoms**: Configuration not taking effect

**Diagnosis**:
```bash
# Check deployed values
helm get values todo-chatbot
```

**Solution**:
```bash
# Ensure values file is specified
helm upgrade todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml
```

### Template Rendering Errors

**Symptoms**: `Error: YAML parse error`

**Diagnosis**:
```bash
# Debug template rendering
helm template todo-chatbot ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot \
  -f ./Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/values-local.yaml

# Or with debug flag
helm install --dry-run --debug todo-chatbot ...
```

---

## Minikube Issues

### Minikube Not Starting

**Symptoms**: `minikube start` fails

**Solutions**:

```bash
# Clean restart
minikube delete
minikube start --driver=docker

# Check Docker is running
docker info

# Try with more resources
minikube start --cpus=4 --memory=8192
```

### Minikube IP Changed

**Symptoms**: Old IP no longer works

**Solution**:
```bash
# Get new IP
minikube ip

# Update any external references (hosts file, etc.)
```

### kubectl Context Wrong

**Symptoms**: Commands apply to wrong cluster

**Solution**:
```bash
# Switch to minikube context
kubectl config use-context minikube

# Verify
kubectl config current-context
```

---

## Debugging Commands Reference

```bash
# Pods
kubectl get pods -l app=todo-chatbot
kubectl describe pod <pod-name>
kubectl logs <pod-name> -f
kubectl logs <pod-name> --previous
kubectl exec -it <pod-name> -- /bin/sh

# Services
kubectl get svc -l app=todo-chatbot
kubectl describe svc <service-name>
kubectl get endpoints

# Deployments
kubectl get deployments -l app=todo-chatbot
kubectl describe deployment <deployment-name>
kubectl rollout status deployment/<deployment-name>

# Events
kubectl get events --sort-by='.lastTimestamp'

# Resources
kubectl top pods
kubectl top nodes

# Helm
helm status todo-chatbot
helm history todo-chatbot
helm get values todo-chatbot
helm get manifest todo-chatbot
```

---

## Getting Help

If issues persist:

1. Check [AI DevOps Tools](./AI_DEVOPS_TOOLS.md) for AI-assisted debugging
2. Review [Minikube Setup](./MINIKUBE_SETUP.md) for configuration
3. Consult [Kubernetes Documentation](https://kubernetes.io/docs/)
4. Check [Helm Documentation](https://helm.sh/docs/)
