# Data Model: Local Kubernetes Deployment

**Feature**: Phase IV - Local Kubernetes Deployment
**Date**: 2026-01-05

## Entity Definitions

### 1. FrontendContainerImage

**Description**: Containerized version of the Next.js chatbot frontend from Phase III, ready for Kubernetes deployment.

**Attributes**:
- `imageTag`: Version identifier (e.g., local-dev, 1.0.0)
- `imageName`: Docker image name (e.g., todo-chatbot-frontend)
- `port`: Application port (3000)
- `healthEndpoint`: HTTP path for health checks (/)
- `baseImage`: Base Docker image (node:20-alpine)
- `buildStrategy`: Multi-stage build (dependencies, build, runtime)
- `nonRootUser`: Security flag - container runs as non-root user
- `optimizedSize`: Target size <500MB

**Relationships**:
- Source: `Phase-III-AI-Chatbot/frontend/` directory
- Deployed via: Frontend Kubernetes Deployment
- Accessed via: Frontend Service (NodePort)
- Configuration: ConfigMap (URL, logging level)
- Secrets: None (frontend doesn't handle secrets)

**Validation Rules**:
- Image tag must match semantic versioning (MAJOR.MINOR.PATCH)
- Health endpoint must return HTTP 200 when healthy
- Container must run as non-root user (UID > 100)
- Final image size must be <500MB after build optimization
- Port 3000 must be exposed in Dockerfile

**State Transitions**:
- Built → (Docker build completed)
- Loaded → (Image loaded to Minikube registry)
- Deployed → (Pod running in Kubernetes)
- Ready → (Readiness probe passing)
- Failed → (Pod restarted after probe failure)

---

### 2. BackendContainerImage

**Description**: Containerized version of the FastAPI chatbot backend from Phase III, ready for Kubernetes deployment.

**Attributes**:
- `imageTag`: Version identifier (e.g., local-dev, 1.0.0)
- `imageName`: Docker image name (e.g., todo-chatbot-backend)
- `port`: Application port (8000)
- `healthEndpoint`: HTTP path for health checks (/health)
- `baseImage`: Base Docker image (python:3.13-slim-alpine)
- `buildStrategy`: Single-stage build (Python application)
- `nonRootUser`: Security flag - container runs as non-root user
- `optimizedSize`: Target size <600MB

**Relationships**:
- Source: `Phase-III-AI-Chatbot/backend/` directory
- Deployed via: Backend Kubernetes Deployment
- Accessed via: Backend Service (ClusterIP)
- Configuration: ConfigMap (database URL, logging level, OpenAI settings)
- Secrets: JWT_SECRET, OPENAI_API_KEY, DATABASE_CREDENTIALS

**Validation Rules**:
- Image tag must match semantic versioning (MAJOR.MINOR.PATCH)
- Health endpoint /health must return HTTP 200 when healthy
- Container must run as non-root user (UID > 100, e.g., 1000)
- Final image size must be <600MB after build optimization
- Port 8000 must be exposed in Dockerfile
- All secrets must be injected as environment variables, not in image
- Working directory must be /app

**State Transitions**:
- Built → (Docker build completed)
- Loaded → (Image loaded to Minikube registry)
- Deployed → (Pod running in Kubernetes)
- Ready → (Readiness probe passing)
- Failed → (Pod restarted after probe failure)

---

### 3. KubernetesDeployment

**Description**: Defines desired state for containerized applications in Kubernetes, includes replica count, pod template, update strategy, and resource specifications.

**Attributes**:
- `name`: Deployment name (todo-chatbot-frontend, todo-chatbot-backend)
- `namespace`: Kubernetes namespace (default: todo-chatbot)
- `replicas`: Number of pod replicas (default: 2 for each service)
- `strategy`: Update strategy (RollingUpdate with maxUnavailable=1)
- `labels`: Key-value pairs for service discovery (app, component, version)
- `annotations`: Metadata for additional configuration
- `selector`: Label selector for pod management
- `imagePullPolicy`: Image pull policy (Never for Minikube local registry)

**Relationships**:
- Manages: Pods (frontend and backend)
- Creates: ReplicaSets for each deployment
- Uses: ContainerImage (frontend or backend)
- Uses: ConfigMap for configuration injection
- Uses: Secret for credential injection

**Validation Rules**:
- Replica count must be >=1 (minimum HA)
- Strategy must be RollingUpdate (zero-downtime)
- maxUnavailable must be <= 1 (maintain availability)
- Resource requests must be specified
- Resource limits must be specified
- Labels must include app and component selectors
- Selector must match pod template labels

**State Transitions**:
- Created → (Deployment resource created)
- Progressing → (Rolling update in progress)
- Ready → (All pods ready and serving traffic)
- Failed → (Deployment failure, requires troubleshooting)

---

### 4. KubernetesService

**Description**: Provides network access to deployed applications, enables service discovery, and handles load balancing across pods.

**Attributes**:
- `name`: Service name (todo-chatbot-frontend, todo-chatbot-backend)
- `namespace`: Kubernetes namespace (default: todo-chatbot)
- `type`: Service type (NodePort for frontend, ClusterIP for backend)
- `selector`: Label selector to route traffic to pods
- `ports`: Port mapping (containerPort, servicePort, nodePort)
- `sessionAffinity`: Session affinity (None for stateless services)

**Relationships**:
- Routes traffic to: Pods managed by Deployment
- Labels match: Deployment pod template labels
- Frontend Service: NodePort for external Minikube access
- Backend Service: ClusterIP for internal communication

**Validation Rules**:
- Selector must match Deployment pod labels
- Port mapping must be correct (servicePort exposes containerPort)
- NodePort must be in valid range (30000-32767)
- ClusterIP service must have no nodePort or externalIP
- Service must be created after Deployment (dependency order)

**State Transitions**:
- Created → (Service resource created)
- Pending → (Service waiting for endpoints)
- Ready → (Endpoints ready, traffic can flow)
- Terminating → (Service being deleted)

---

### 5. HelmChart

**Description**: Package containing all Kubernetes manifests, templates, and configuration values needed to deploy the complete application using Helm.

**Attributes**:
- `name`: Chart name (todo-chatbot)
- `version`: Chart version following semantic versioning (0.1.0)
- `appVersion`: Application version (1.0.0)
- `description`: Chart description
- `type`: Chart type (application)
- `apiVersion`: Helm API version (v2)
- `kubeVersion`: Kubernetes version constraint (^1.16.0-0)
- `dependencies`: Chart dependencies (none for this chart)

**Relationships**:
- Contains: Templates for all Kubernetes resources
- Uses: values.yaml for default configuration
- Supports: values-local.yaml for Minikube overrides
- Generates: Kubernetes Deployment, Service, ConfigMap, Secret resources

**Validation Rules**:
- Chart version must follow semantic versioning
- Chart name must match directory name
- App version must match application version
- templates/ directory must contain .yaml files
- Chart must pass `helm lint`
- Chart must support `helm install` and `helm upgrade`
- Chart must support `helm rollback` for version changes

**State Transitions**:
- Created → (Chart initialized with helm create)
- Installed → (Release created in cluster)
- Upgraded → (Release updated in cluster)
- Rolledback → (Release reverted to previous version)
- Uninstalled → (Release removed from cluster)

---

### 6. ConfigMap

**Description**: Stores non-sensitive configuration data (environment variables, feature flags) that can be mounted into containers as environment variables or files.

**Attributes**:
- `name`: ConfigMap name (todo-chatbot-config)
- `namespace`: Kubernetes namespace (default: todo-chatbot)
- `data`: Key-value configuration pairs

**Configuration Data**:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `FRONTEND_API_URL`: Backend API URL for frontend
- `LOG_LEVEL`: Application logging level (INFO, DEBUG, ERROR)
- `NODE_ENV`: Node environment (production/development)

**Relationships**:
- Used by: Frontend Deployment (NODE_ENV, FRONTEND_API_URL, LOG_LEVEL)
- Used by: Backend Deployment (DATABASE_URL, LOG_LEVEL)
- Mounted as: Environment variables in containers

**Validation Rules**:
- Database URL must be valid connection string
- API URLs must be valid HTTP/HTTPS URLs
- Log level must be valid (DEBUG, INFO, WARNING, ERROR)
- ConfigMap must be created before Deployments (dependency)
- No sensitive data (API keys, passwords) allowed in ConfigMap

---

### 7. Secret

**Description**: Stores sensitive data (API keys, database credentials, JWT secrets) encrypted at rest and mounted into containers.

**Attributes**:
- `name`: Secret name (todo-chatbot-secrets)
- `namespace`: Kubernetes namespace (default: todo-chatbot)
- `type`: Secret type (Opaque for generic secrets)
- `data`: Base64-encoded secret values

**Secret Data**:
- `JWT_SECRET`: JWT signing/verification secret
- `OPENAI_API_KEY`: OpenAI API key for chatbot
- `DATABASE_PASSWORD`: Database password (if using password auth)

**Relationships**:
- Used by: Backend Deployment (JWT_SECRET, OPENAI_API_KEY)
- Mounted as: Environment variables in containers
- Must not be: Committed to version control

**Validation Rules**:
- All secret values must be Base64-encoded
- Secret must be created before Deployments (dependency)
- Secrets must not be in ConfigMap
- Secret values must not be empty
- Secret must use type: Opaque (generic)

---

### 8. Ingress

**Description**: Defines routing rules for external traffic to reach services within the cluster (optional, documented but out of scope for Phase IV local deployment).

**Attributes**:
- `name`: Ingress name (todo-chatbot-ingress)
- `namespace`: Kubernetes namespace (default: todo-chatbot)
- `rules`: Routing rules array
- `tls`: TLS configuration

**Ingress Rules**:
- `host`: Hostname for routing
- `paths`: Path routing array
- `backend`: Target service name and port

**Relationships**:
- Routes to: Frontend Service
- Uses: Service selector for backend routing
- Documented for: Phase V cloud deployment

**Validation Rules**:
- Ingress class must be available in cluster
- Service must exist before Ingress creation
- TLS certificate required for HTTPS (out of scope for Phase IV)

---

## Data Flow

```
Phase III Source Code
         │
         ├── Frontend (Next.js)
         │       └─> Docker build ──> FrontendContainerImage
         │
         └── Backend (FastAPI)
                 └─> Docker build ──> BackendContainerImage
                                            │
                                            ├─> Minikube registry load
                                            │
                                            └─> Kubernetes Deployment
                                                   │
                                                   ├─> Pods (frontend x2)
                                                   │       └─> Service (NodePort)
                                                   │
                                                   └─> Pods (backend x2)
                                                           └─> Service (ClusterIP)
                                                                   │
                                                   ConfigMap ◄────────┴
                                                   Secret  ◄────────┴
```

## Configuration Schema

### Helm Values Structure

```yaml
# Global settings
global:
  namespace: todo-chatbot
  domain: localhost

# Frontend configuration
frontend:
  image:
    repository: todo-chatbot-frontend
    tag: local-dev
    pullPolicy: Never
  replicas: 2
  service:
    type: NodePort
    port: 30000
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1
      memory: 1Gi
  env:
    NODE_ENV: production
    FRONTEND_API_URL: http://todo-chatbot-backend:8000
    LOG_LEVEL: INFO

# Backend configuration
backend:
  image:
    repository: todo-chatbot-backend
    tag: local-dev
    pullPolicy: Never
  replicas: 2
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 1
      memory: 1Gi
  env:
    DATABASE_URL: postgresql://user:pass@host:5432/db
    LOG_LEVEL: INFO

# External services
external:
  neon:
    enabled: true
  openai:
    enabled: true
```

## Validation Summary

| Entity | Validation Rules | State Transitions |
|--------|------------------|------------------|
| FrontendContainerImage | Tag versioning, <500MB, non-root, health endpoint | Built → Loaded → Deployed → Ready/Failed |
| BackendContainerImage | Tag versioning, <600MB, non-root, health endpoint, secrets | Built → Loaded → Deployed → Ready/Failed |
| KubernetesDeployment | Replicas, rolling update, resources, labels | Created → Progressing → Ready/Failed |
| KubernetesService | Selector match, port mapping, type | Created → Pending → Ready → Terminating |
| HelmChart | Semantic versioning, helm lint, install/upgrade/rollback | Created → Installed → Upgraded → Rolledback → Uninstalled |
| ConfigMap | Valid URLs, no secrets, dependency order | Created |
| Secret | Base64 encoded, dependency order, no empty values | Created |
| Ingress | Available ingress class, service exists | Created |
