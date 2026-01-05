# Implementation Plan: Local Kubernetes Deployment

**Branch**: `004-local-k8s-deployment` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-local-k8s-deployment/spec.md`

**Note**: This template is filled in by `/sp.plan` command. See `.specify/templates/commands/plan.md` for execution workflow.

## Summary

Containerize Phase III todo chatbot (frontend: Next.js, backend: FastAPI) and deploy to local Kubernetes cluster using Minikube with Helm chart package management. Implementation follows Docker containerization, Kubernetes manifest generation, Helm chart packaging, and AI DevOps tool integration for developer efficiency.

## Technical Context

**Language/Version**: Dockerfile, Helm 3.15+, kubectl 1.29+, Minikube 1.32+

**Primary Dependencies**:
- Docker (container runtime)
- Helm (package manager)
- Minikube (local Kubernetes)
- kubectl-ai (AI-assisted kubectl, optional)
- Kagent (AI cluster analysis, optional)
- Docker AI Agent / Gordon (AI-assisted Docker, optional, Docker Desktop 4.53+)

**Storage**: External Neon PostgreSQL database (no local DB)

**Testing**: kubectl commands, Docker local testing, Helm chart validation

**Target Platform**: Local Kubernetes (Minikube) - foundation for Phase V cloud deployment

**Project Type**: Deployment orchestration - packaging existing application for Kubernetes

**Performance Goals**: Successful Minikube deployment with <5 minute deployment time, <30 second container startup

**Constraints**:
- Single-node Minikube environment (CPU: 4 cores, Memory: 8GB minimum)
- No cloud deployment (Phase V scope)
- Production-hardening out of scope
- Monitoring stack out of scope

**Scale/Scope**:
- Deploy frontend and backend containers
- Create Kubernetes manifests and Helm chart
- Provide deployment documentation
- Demonstrate Minikube operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Compliance**:
- [PASS] Spec-driven development approach followed
- [PASS] Technology stack aligned with constitution (Phase IV: Docker, Minikube, Helm)
- [PASS] Container orchestration principles applied
- [PASS] AI-first architecture considered (DevOps tools integration)
- [PASS] Reusable intelligence approach (Docker/K8s patterns for Phase V)
- [PASS] Testing-first approach (deployment verification)

**Gates determined**: All gates passed. No constitution violations.

## Project Structure

### Documentation (this feature)

```text
specs/004-local-k8s-deployment/
├── spec.md              # This file (/sp.plan command output)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

**Monorepo pattern adopted** - Phase IV artifacts in dedicated directory for clear separation from Phase III source code.

**directories captured**:
- Phase IV: `Phase-IV-Local-K8s-Deployment/` - container and K8s artifacts
- Phase III: `Phase-III-AI-Chatbot/` - unchanged source code
- Specs: `specs/004-local-k8s-deployment/` - spec and plan documentation

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | No violations identified | All requirements align with established patterns |

## Design Decisions

### 1. Container Strategy

**Decision**: Multi-stage Docker builds for frontend, single-stage for backend

**Rationale**: Frontend requires Node.js build step for optimization; backend Python app can be single-stage

**Alternatives Considered**:
- Single-stage for both (simplest, but frontend image would be larger)
- BuildKit approach (modern but requires rethinking entire build pipeline)

**Technical Impact**:
- Frontend: Two-stage build (dependencies, then app)
- Backend: Single-stage build
- Both use Alpine Linux base for smaller images

### 2. Kubernetes Resource Strategy

**Decision**: Separate Deployments and Services for frontend/backend, ConfigMap for config, Secret for credentials

**Rationale**: Separation of concerns - configuration separate from application code, secrets properly isolated

**Alternatives Considered**:
- All resources in one deployment (simpler but violates separation)
- Environment variables only (simpler but less secure)

**Technical Impact**:
- Frontend Deployment: 2 replicas, ClusterIP service
- Backend Deployment: 2 replicas, ClusterIP service (for internal communication)
- ConfigMap: Application configuration
- Secret: JWT and OpenAI API keys

### 3. Minikube Networking Strategy

**Decision**: NodePort service type for frontend, ClusterIP for backend

**Rationale**: Minikube's LoadBalancer has limitations; NodePort is standard for local development

**Alternatives Considered**:
- LoadBalancer type (requires tunnel, may not work on all systems)
- Port-forwarding (manual, not persistent)

**Technical Impact**:
- Frontend: NodePort 30000, accessible via minikube service list
- Backend: ClusterIP, internal communication only
- No external Ingress (out of scope per spec)

### 4. Helm Chart Structure

**Decision**: Standard Helm chart structure with values.yaml for configuration overrides

**Rationale**: Helm standard patterns, values files support multiple environments

**Alternatives Considered**:
- Inline all manifests (simpler but harder to maintain)
- Multiple charts per service (over-complication)

**Technical Impact**:
- Chart name: todo-chatbot
- Version: 0.1.0
- Templates use Helm template functions
- Values file provides all configurable parameters

### 5. AI DevOps Tools Strategy

**Decision**: Document kubectl-ai and Kagent as optional enhancements, provide standard kubectl fallback commands

**Rationale**: AI tools may not be available in all regions/tiers; fallback ensures core functionality works everywhere

**Alternatives Considered**:
- Require AI tools (excludes users without access)
- Skip AI tool integration (loses productivity benefits)

**Technical Impact**:
- Primary: Standard kubectl and Docker commands
- Enhanced: kubectl-ai natural language commands, Kagent health analysis
- Docker AI (Gordon): Documented as optional enhancement

### 6. Health Check Strategy

**Decision**: Liveness and readiness probes on HTTP endpoints

**Rationale**: Kubernetes requires probes for pod lifecycle management

**Alternatives Considered**:
- No probes (pods may not restart if stuck)
- TCP probes (simpler but less expressive)

**Technical Impact**:
- Frontend: HTTP GET /healthz or root path, initialDelaySeconds: 5, periodSeconds: 10
- Backend: HTTP GET /health, initialDelaySeconds: 5, periodSeconds: 10
- Failure threshold: 3 consecutive failures

### 7. Image Registry Strategy

**Decision**: Use Minikube's built-in registry for local deployment

**Rationale**: No need for external registry in local environment

**Alternatives Considered**:
- Docker Hub (requires internet, authentication)
- Public registry (unnecessary complexity)

**Technical Impact**:
- Images load directly with no network pull
- Tagging: local-dev for Minikube testing

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Development Machine                                        │
│  ┌──────────────────────┐                                      │
│  │  Phase IV Source    │                                      │
│  │  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  │  Frontend Pods (2)   │     │ Backend Pods (2)  │ │
│  │  │  NodePort: 30000    │     │ ClusterIP       │ │
│  │  └──────────────────────┐     └──────────────────┐ │
│  │  │ ConfigMap (config)  │     │ Secret (JWT/API) │ │
│  │  └──────────────────────┘     └──────────────────┘ │
│                                                                  │
│  ┌──────────────────────┐                                      │
│  │  External Neon PostgreSQL Database                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Phase-IV-Local-K8s-Deployment/images/frontend/

**Component**: Frontend Container

**Files to create**:
- `Dockerfile` - Multi-stage build configuration
- `.dockerignore` - Exclude unnecessary files from build context

**Dockerfile specification**:
- Stage 1 (dependencies): FROM node:20-alpine as base, copy package files, run npm ci
- Stage 2 (build): Copy dependencies, run npm run build
- Final stage: FROM node:20-alpine, copy build output, expose port 3000, non-root user, health check

**Health check**: HTTP endpoint at root path (/healthz)

**Configuration**:
- Build arguments for API URL and domain configuration
- Environment for node production mode

---

### Phase-IV-Local-K8s-Deployment/images/backend/

**Component**: Backend Container

**Files to create**:
- `Dockerfile` - Single-stage build configuration
- `.dockerignore` - Exclude unnecessary files from build context

**Dockerfile specification**:
- Base: Python 3.13-slim Alpine image
- Install dependencies: COPY requirements.txt, RUN pip install
- Copy source: COPY . /app
- Expose port: 8000
- Non-root user: USER appuser
- Health check: HTTP GET /health endpoint

**Configuration**:
- Environment variables for database URL and OpenAI API key
- Working directory: /app

---

### Phase-IV-Local-K8s-Deployment/k8s/

**Component**: Kubernetes Manifests

**Files to create**:
- `frontend-deployment.yaml` - Frontend Deployment (2 replicas)
- `backend-deployment.yaml` - Backend Deployment (2 replicas)
- `frontend-service.yaml` - Frontend Service (NodePort 30000)
- `backend-service.yaml` - Backend Service (ClusterIP)
- `configmap.yaml` - Application configuration (Neon DB URL, etc.)
- `secret.yaml` - Sensitive data (JWT secrets, API keys, database credentials)

**Kubernetes specifications**:
- API version: apps/v1
- Kind: Deployment for frontend/backend
- Kind: Service for frontend/backend
- Kind: ConfigMap for configuration
- Kind: Secret for credentials
- Labels: app=todo-chatbot, phase=iv
- Probes: livenessProbe and readinessProbe
- Resources: requests (500m CPU, 512Mi memory), limits (1 CPU, 1Gi memory)

---

### Phase-IV-Local-K8s-Deployment/helm/todo-chatbot/

**Component**: Helm Chart

**Files to create**:
- `Chart.yaml` - Helm chart metadata
- `values.yaml` - Default configuration
- `values-local.yaml` - Local Minikube overrides
- `templates/deployment.yaml` - Deployment template
- `templates/service.yaml` - Service template
- `templates/configmap.yaml` - ConfigMap template
- `templates/secret.yaml` - Secret template
- `templates/ingress.yaml` - Ingress template
- `templates/NOTES.txt` - Post-installation instructions
- `docs/MINIKUBE_SETUP.md` - Minikube installation guide
- `docs/DEPLOYMENT.md` - Deployment procedure
- `docs/AI_DEVOPS_TOOLS.md` - AI tools documentation
- `docs/TROUBLESHOOTING.md` - Common issues and solutions

**Helm chart specification**:
- Chart name: todo-chatbot
- Chart version: 0.1.0
- App version: 1.0.0
- Description: Todo Chatbot for local Minikube deployment
- Type: application
- API version: v2 (Kubernetes 1.16+)
- Values file provides all configurable parameters
- Templates use Helm template functions
- Values file supports overrides for all critical configuration
- Chart must support installation to arbitrary namespaces
- Chart must support upgrades and rollbacks without data loss

**Values parameters**:
- Frontend image, tag, replicas, resources
- Backend image, tag, replicas, resources
- ConfigMap values (database URL, OpenAI settings)
- Secret values (JWT secret, API keys)
- Service settings (NodePort, ClusterIP)
- Ingress configuration (enabled/disabled)

---

### docs/ Directory

**Component**: Documentation

**Files to create**:
- `MINIKUBE_SETUP.md` - Minikube installation and configuration
- `DEPLOYMENT.md` - Step-by-step deployment guide
- `AI_DEVOPS_TOOLS.md` - kubectl-ai, Kagent, Docker AI documentation
- `TROUBLESHOOTING.md` - Common deployment issues and solutions

**Documentation coverage**:
- Minikube prerequisites and installation for macOS/Linux/Windows
- Helm chart installation and configuration
- kubectl-ai setup and usage examples
- Kagent setup and health analysis examples
- Docker AI (Gordon) activation and usage
- Common deployment errors and resolutions
- Log retrieval and debugging techniques

## Implementation Approach

### Phase 0: Research (Skipped)

No research phase required - all technologies are well-established:
- Docker: Industry standard for containerization
- Helm: Industry standard for Kubernetes package management
- Minikube: Official local Kubernetes distribution
- kubectl-ai/kubectl/Kagent: Documented tools with standard patterns

### Phase 1: Data Model & Contracts

**Entity Definition**:
- FrontendContainerImage: Containerized Next.js frontend, includes build artifacts, serves on port 3000
- BackendContainerImage: Containerized FastAPI backend, includes Python runtime, serves on port 8000
- KubernetesDeployment: Defines desired state for containerized applications, includes replica count, resource specs, probes
- KubernetesService: Network access point, NodePort for frontend, ClusterIP for backend
- HelmChart: Package of K8s manifests and configuration, version-controlled
- ConfigMap: Non-sensitive configuration (environment variables, feature flags)
- Secret: Sensitive data (API keys, database credentials), encrypted at rest
- Ingress: External traffic routing (optional, documented but out of scope)

**Validation Rules**:
- Frontend image: <500MB optimized, health endpoint defined
- Backend image: <600MB, non-root, health endpoint /health
- Deployments: Liveness/readiness probes, rolling updates, resource limits defined
- Services: Proper port configuration, labels for discovery
- Helm chart: Standard structure, values file overrides supported

### Phase 1: Quick Start Guide

**Purpose**: Enable developers to understand and deploy to system quickly

**Contents**:
- Prerequisites check script
- Single-command Minikube startup
- Single-command Helm chart installation
- Service access verification steps
- Common deployment verification commands

**Implementation Notes**:
- Copy all commands from documentation to ensure reproducibility
- Include timeout/success indicators in commands
- Document expected outputs at each step
- Provide rollback procedure (helm rollback)

## Deployment Flow

```
1. Prerequisites Check
   ├─ Docker installed and running
   ├─ Minikube installed or follow setup guide
   └─ Helm installed

2. Build Container Images
   ├─ Build frontend Docker image
   └─ Build backend Docker image

3. Load Images to Minikube
   └─ Minikube image load (or tag and load)

4. Create Kubernetes Resources
   ├─ Install Helm chart
   │   ├─ Creates ConfigMap (configuration)
   │   ├─ Creates Secret (credentials)
   │   ├─ Creates Deployment (frontend + backend)
   │   └─ Creates Services (NodePort + ClusterIP)

5. Verify Deployment
   ├─ Check pod status (kubectl get pods)
   ├─ Check service status (kubectl get svc)
   ├─ Verify health endpoints (curl/kubectl port-forward)
   └─ Test application functionality

6. Access Application
   └─ Open browser/app with Minikube service URL or port-forward
```

## Configuration Management

### Environment Variables

| Variable | Source | Description | Secret |
|-----------|----------|-------------|--------|
| DATABASE_URL | ConfigMap | Neon PostgreSQL connection string | No |
| OPENAI_API_KEY | Secret | OpenAI API key for chatbot | Yes |
| JWT_SECRET | Secret | JWT signing/verification secret | Yes |
| LOG_LEVEL | ConfigMap | Application logging level | No |
| NODE_ENV | ConfigMap | production/development flag | No |

### Configuration Override Pattern

**values-local.yaml** for Minikube-specific overrides:
```yaml
replicaCount: 2
resources:
  requests:
    cpu: "500m"
    memory: "512Mi"
  limits:
    cpu: "1"
    memory: "1Gi"
image:
  pullPolicy: Never
  tag: "local-dev"
```

## Quality Assurance

### Code Quality

- [ ] Dockerfiles follow multi-stage best practices
- [ ] All images use non-root user
- [ ] Health check endpoints defined for both services
- [ ] Kubernetes manifests include liveness and readiness probes
- [ ] Resource limits are specified (requests and limits)
- [ ] Secrets used for all sensitive data
- [ ] Labels applied to all Kubernetes resources
- [ ] Helm chart follows standard directory structure

### Documentation Quality

- [ ] All commands are copy-pasteable
- [ ] Prerequisites are clearly documented
- [ ] Troubleshooting guide included
- [ ] AI tools documentation included
- [ ] Deployment steps include verification commands

### Deployment Quality

- [ ] Application accessible after deployment
- [ ] All pods reach ready state
- [ ] Health checks pass
- [ ] No critical errors in logs
- [ ] Configuration values work as expected
- [ ] Kubernetes resource manifests are valid
- [ ] Helm chart lint passes
- [ ] Documentation provides clear step-by-step instructions
- [ ] Deployment can be repeated from scratch (clean Minikube) with 100% success rate
- [ ] Rollback to previous Helm chart version executes successfully with no data loss
