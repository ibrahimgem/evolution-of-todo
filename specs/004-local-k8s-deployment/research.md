# Research: Local Kubernetes Deployment

**Feature**: Phase IV - Local Kubernetes Deployment
**Date**: 2026-01-05

## Overview

No external research required - all technologies (Docker, Helm, Minikube, kubectl-ai, Kagent) are well-established industry standards. This document records the decisions and patterns selected for implementation.

## Technology Decisions

### 1. Docker Containerization

**Decision**: Multi-stage Docker build for frontend, single-stage for backend

**Rationale**: Next.js requires build step (npm run build) for optimization; Python/FastAPI app can run directly from source. Multi-stage builds separate build dependencies from runtime image, resulting in smaller final images.

**Alternatives Considered**:
- Single-stage for both: Simplest but final frontend image would include build tools and cache, increasing size by 200-300MB
- BuildKit with inline caching: Modern but requires rethinking entire build pipeline for local development

**Reference**: Docker multi-stage build best practices (https://docs.docker.com/build/building/multi-stage/)

**Implementation Details**:
- Frontend base image: node:20-alpine
- Frontend builder stage: npm ci && npm run build
- Frontend final stage: Copy only build artifacts and node_modules
- Backend base image: python:3.13-slim
- Backend: Single stage, install dependencies, copy source code

---

### 2. Kubernetes Manifests

**Decision**: Standard Kubernetes Deployment and Service manifests, separate Deployments for frontend and backend

**Rationale**: Separation of concerns allows independent scaling and updates. Each service has its own Deployment with replica count.

**Alternatives Considered**:
- Single Deployment with multiple containers: Simpler but couples services together
- DaemonSet: Not appropriate for this workload

**Reference**: Kubernetes Deployment documentation (https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

**Implementation Details**:
- API version: apps/v1
- Replicas: 2 per service (frontend, backend)
- Strategy: RollingUpdate with maxUnavailable=1
- Probes: HTTP liveness and readiness
- Resources: Requests (500m CPU, 512Mi memory), Limits (1 CPU, 1Gi memory)
- Labels: app=todo-chatbot, phase=iv, component=frontend/backend
- Service types: NodePort for frontend (external access), ClusterIP for backend (internal)

---

### 3. Helm Chart Structure

**Decision**: Standard Helm chart structure with Chart.yaml, values.yaml, and templates/ directory

**Rationale**: Helm is the de-facto standard for Kubernetes package management. Values files support multiple environments (local, staging, production).

**Alternatives Considered**:
- Kustomize: Powerful but steeper learning curve
- Inline manifests: Simplest but harder to maintain and version control

**Reference**: Helm best practices (https://helm.sh/docs/topics/chart_best_practices/)

**Implementation Details**:
- Chart name: todo-chatbot
- Chart version: 0.1.0
- API version: v2 (Kubernetes 1.16+)
- Templates use Go template functions for values injection
- values.yaml: Default configuration
- values-local.yaml: Minikube-specific overrides

---

### 4. Minikube Configuration

**Decision**: Use Minikube's built-in registry, NodePort services, and local resource allocation

**Rationale**: Minikube is designed for local development. Using its registry avoids network pulls. NodePort is reliable for local access.

**Alternatives Considered**:
- External registry: Requires network, authentication, unnecessary for local
- LoadBalancer: Requires minikube tunnel, less reliable across platforms
- Port-forwarding: Manual process, not persistent

**Reference**: Minikube documentation (https://minikube.sigs.k8s.io/docs/)

**Implementation Details**:
- Driver: docker (default on macOS)
- Resources: CPUs=4, Memory=8192, Disk=20000MB
- Registry: Built-in minikube registry
- Services: NodePort for frontend (30000-32767 range)

---

### 5. Configuration Management

**Decision**: ConfigMap for non-sensitive config, Secret for sensitive data

**Rationale**: Kubernetes best practice. Separates concerns: ConfigMap for application configuration, Secret for credentials. Allows version control of config without committing secrets.

**Alternatives Considered**:
- Environment variables only: Simplest but no separation, secrets in manifests
- External config systems: Over-complication for local deployment

**Reference**: Kubernetes ConfigMaps and Secrets (https://kubernetes.io/docs/concepts/configuration/secret/)

**Implementation Details**:
- ConfigMap: DATABASE_URL, LOG_LEVEL, NODE_ENV, FRONTEND_API_URL
- Secret: OPENAI_API_KEY, JWT_SECRET
- Mounted as environment variables in containers
- Secret values not committed to Git (use .gitignore and separate-secrets pattern)

---

### 6. AI DevOps Tools

**Decision**: Document kubectl-ai, Kagent, and Docker AI (Gordon) as optional enhancements with fallback to standard CLI commands

**Rationale**: AI tools enhance developer experience but may not be available in all regions/tiers. Primary documentation uses standard commands to ensure core functionality works everywhere.

**Alternatives Considered**:
- Require AI tools: Would exclude users without access
- Skip AI tools: Loses productivity benefits for users with access

**Reference**: Documentation from respective tools (kubectl-ai, Kagent, Gordon)

**Implementation Details**:
- kubectl-ai: Natural language to kubectl command translation
- Kagent: Cluster health analysis and recommendations
- Docker AI (Gordon): Natural language Docker operations
- All tools: Documented with setup and example commands
- Fallback: All primary commands provided in standard kubectl/Docker format

---

## Patterns Selected

### Container Pattern

**Multi-stage build for Node.js applications**:
```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Stage 2: Build
COPY . .
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY package*.json ./
RUN npm ci --only=production
EXPOSE 3000
CMD ["npm", "start"]
```

**Single-stage build for Python applications**:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd -m -u 1000 appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Kubernetes Health Check Pattern

**Liveness Probe**: Detects and restarts unresponsive containers

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

**Readiness Probe**: Prevents traffic to unready containers

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

### Helm Template Pattern

**Deployment template with values injection**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Chart.Name }}-{{ .Values.component }}
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: {{ .Chart.Name }}-config
              key: database-url
```

## Security Considerations

1. **Non-root containers**: All containers run as non-root user for security best practice
2. **Secrets for credentials**: No sensitive data in ConfigMaps or manifests
3. **Minimal base images**: Alpine and slim variants reduce attack surface
4. **Resource limits**: Prevent containers from consuming all node resources
5. **Read-only root filesystem**: Run containers as non-root user with minimal permissions

## Performance Considerations

1. **Image size optimization**: Multi-stage builds exclude build artifacts from final image
2. **Resource requests/limits**: Ensure fair scheduling and prevent resource exhaustion
3. **Probes configuration**: Quick detection of unhealthy pods (10s period)
4. **Rolling updates**: Zero-downtime deployments with maxUnavailable=1

## Known Limitations

1. **Single-node cluster**: Minikube has no multi-node high availability (acceptable for local)
2. **No external Ingress**: NodePort access sufficient for local (Ingress for Phase V)
3. **No monitoring stack**: Basic logging only (Prometheus/Grafana for Phase V)
4. **No service mesh**: Direct service communication (Istio/Linkerd for Phase V)
5. **No CI/CD**: Manual deployment (pipelines for Phase V)

## References

- Docker Documentation: https://docs.docker.com/
- Kubernetes Documentation: https://kubernetes.io/docs/
- Helm Documentation: https://helm.sh/docs/
- Minikube Documentation: https://minikube.sigs.k8s.io/docs/
- kubectl-ai: https://github.com/sozercan/kubernetes-cli-ai
- Kagent: https://kagent.io/
- Docker AI (Gordon): Available in Docker Desktop 4.53+
