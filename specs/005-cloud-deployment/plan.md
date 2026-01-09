# Phase V: Enterprise Cloud Deployment - Architecture Plan

## Document Information
- **Phase**: V
- **Version**: 1.0.0
- **Status**: Draft
- **Created**: 2026-01-08
- **From**: spec.md §US1-US7

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              GITHUB ACTIONS CI/CD                                │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐       │
│  │  Push   │───▶│  Test   │───▶│  Build  │───▶│  Push   │───▶│ Deploy  │       │
│  │  Code   │    │  & Lint │    │  Images │    │  to DO  │    │  Helm   │       │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘       │
└─────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         DIGITALOCEAN CLOUD PLATFORM                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────┐     ┌──────────────────────────────────────────────────┐ │
│  │ DO Container     │     │              DOKS CLUSTER                         │ │
│  │ Registry         │     ├──────────────────────────────────────────────────┤ │
│  │ ┌──────────────┐ │     │                                                  │ │
│  │ │ frontend:tag │ │────▶│  ┌─────────────────────────────────────────────┐│ │
│  │ │ backend:tag  │ │     │  │ INGRESS CONTROLLER + CERT-MANAGER          ││ │
│  │ └──────────────┘ │     │  │ (SSL/TLS, Domain Routing)                  ││ │
│  └──────────────────┘     │  └─────────────────────────────────────────────┘│ │
│                           │                      │                           │ │
│  ┌──────────────────┐     │  ┌───────────────────┴───────────────────────┐  │ │
│  │ DO Load Balancer │◀────│  │                                           │  │ │
│  │ (Public IP)      │     │  │  ┌─────────────┐     ┌─────────────┐     │  │ │
│  └──────────────────┘     │  │  │  FRONTEND   │     │  BACKEND    │     │  │ │
│                           │  │  │  ┌───────┐  │     │  ┌───────┐  │     │  │ │
│  ┌──────────────────┐     │  │  │  │ Next  │  │     │  │FastAPI│  │     │  │ │
│  │ DO Managed       │     │  │  │  │ .js   │  │     │  │ App   │  │     │  │ │
│  │ PostgreSQL       │◀────│──│  │  └───┬───┘  │     │  └───┬───┘  │     │  │ │
│  │ (or Neon)        │     │  │  │  ┌───┴───┐  │     │  ┌───┴───┐  │     │  │ │
│  └──────────────────┘     │  │  │  │ Dapr  │  │     │  │ Dapr  │  │     │  │ │
│                           │  │  │  │Sidecar│  │     │  │Sidecar│  │     │  │ │
│                           │  │  │  └───────┘  │     │  └───┬───┘  │     │  │ │
│                           │  │  └─────────────┘     └──────┼──────┘     │  │ │
│                           │  │                             │            │  │ │
│                           │  │              ┌──────────────▼──────────┐ │  │ │
│                           │  │              │     KAFKA CLUSTER       │ │  │ │
│                           │  │              │  ┌────┐ ┌────┐ ┌────┐  │ │  │ │
│                           │  │              │  │ B0 │ │ B1 │ │ B2 │  │ │  │ │
│                           │  │              │  └────┘ └────┘ └────┘  │ │  │ │
│                           │  │              └─────────────────────────┘ │  │ │
│                           │  │                                          │  │ │
│                           │  │  ┌─────────────────────────────────────┐ │  │ │
│                           │  │  │         MONITORING STACK            │ │  │ │
│                           │  │  │ Prometheus │ Grafana │ Loki │Jaeger │ │  │ │
│                           │  │  └─────────────────────────────────────┘ │  │ │
│                           │  └──────────────────────────────────────────┘  │ │
│                           └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Design

### 2.1 Infrastructure Components (Terraform)

#### DD-001: DOKS Cluster Configuration
```hcl
# Cluster specification
resource "digitalocean_kubernetes_cluster" "todo_chatbot" {
  name    = "todo-chatbot-prod"
  region  = "nyc1"
  version = "1.28.x"

  node_pool {
    name       = "worker-pool"
    size       = "s-2vcpu-4gb"
    auto_scale = true
    min_nodes  = 3
    max_nodes  = 10
  }
}
```

**Decisions:**
- Region: NYC1 (low latency for US users)
- Node size: s-2vcpu-4gb (balanced cost/performance)
- Auto-scaling: 3-10 nodes based on load

#### DD-002: Container Registry
```hcl
resource "digitalocean_container_registry" "todo_chatbot" {
  name                   = "todo-chatbot-registry"
  subscription_tier_slug = "basic"
}
```

#### DD-003: Load Balancer (via Kubernetes Ingress)
- Automatically provisioned by NGINX Ingress Controller
- SSL/TLS via cert-manager with Let's Encrypt

---

### 2.2 Kafka Architecture

#### DD-010: Kafka Deployment (Strimzi Operator)

```yaml
# Kafka cluster specification
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-chatbot-kafka
spec:
  kafka:
    replicas: 3
    listeners:
      - name: plain
        port: 9092
        type: internal
      - name: tls
        port: 9093
        type: internal
        tls: true
    storage:
      type: persistent-claim
      size: 10Gi
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 5Gi
```

#### DD-011: Topic Design

| Topic | Partitions | Retention | Purpose |
|-------|------------|-----------|---------|
| `todo-events` | 6 | 7 days | Task CRUD operations |
| `chat-events` | 6 | 7 days | Conversation events |
| `user-events` | 3 | 30 days | Auth/user events |
| `dlq` | 3 | 30 days | Dead letter queue |

#### DD-012: Event Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Backend    │────▶│    Kafka     │────▶│  Consumers   │
│  (Producer)  │     │   Broker     │     │ (Analytics)  │
└──────────────┘     └──────────────┘     └──────────────┘
      │                    │
      │ Events:            │ Stored:
      │ - TaskCreated      │ - 7 days retention
      │ - TaskUpdated      │ - 6 partitions
      │ - TaskDeleted      │ - Replicated x3
      │ - MessageSent      │
```

---

### 2.3 Dapr Architecture

#### DD-020: Dapr Components

```yaml
# Service Invocation Component
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: service-invocation
spec:
  type: serviceinvocation
  version: v1
---
# Pub/Sub Component (Kafka)
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "todo-chatbot-kafka-kafka-bootstrap:9092"
    - name: authType
      value: "none"
---
# State Store Component (Redis)
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis-master:6379"
```

#### DD-021: Dapr Sidecar Integration

```yaml
# Pod annotation for Dapr sidecar injection
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "backend"
    dapr.io/app-port: "8000"
    dapr.io/enable-api-logging: "true"
```

#### DD-022: Service Communication via Dapr

```
Frontend Pod                          Backend Pod
┌─────────────────┐                  ┌─────────────────┐
│   Next.js App   │                  │   FastAPI App   │
│        │        │                  │        │        │
│   ┌────▼────┐   │    HTTP/gRPC    │   ┌────▼────┐   │
│   │  Dapr   │───┼─────────────────┼──▶│  Dapr   │   │
│   │ Sidecar │   │                  │   │ Sidecar │   │
│   └─────────┘   │                  │   └─────────┘   │
└─────────────────┘                  └─────────────────┘

# Dapr service invocation
curl http://localhost:3500/v1.0/invoke/backend/method/api/tasks
```

---

### 2.4 CI/CD Pipeline Design

#### DD-030: GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to DOKS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Tests
        run: |
          # Frontend tests
          cd Phase-III-AI-Chatbot/frontend && npm test
          # Backend tests
          cd Phase-III-AI-Chatbot/backend && pytest

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build and Push Frontend
        uses: docker/build-push-action@v5
        with:
          context: ./Phase-III-AI-Chatbot/frontend
          push: true
          tags: registry.digitalocean.com/todo-chatbot/frontend:${{ github.sha }}

      - name: Build and Push Backend
        uses: docker/build-push-action@v5
        with:
          context: ./Phase-III-AI-Chatbot/backend
          push: true
          tags: registry.digitalocean.com/todo-chatbot/backend:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to DOKS
        run: |
          helm upgrade --install todo-chatbot ./helm/todo-chatbot \
            --set frontend.image.tag=${{ github.sha }} \
            --set backend.image.tag=${{ github.sha }}
```

#### DD-031: Deployment Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT FLOW                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Push to main ──▶ 2. Run Tests ──▶ 3. Build Images       │
│                           │                  │               │
│                           │ (fail)           │ (success)     │
│                           ▼                  ▼               │
│                      Stop Pipeline     4. Push to Registry   │
│                                              │               │
│                                              ▼               │
│                      6. Health Check ◀── 5. Helm Upgrade     │
│                           │                                  │
│              ┌────────────┴────────────┐                    │
│              │                         │                    │
│              ▼ (healthy)               ▼ (unhealthy)        │
│         7. Complete              8. Auto Rollback            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.5 Monitoring Architecture

#### DD-040: Prometheus Configuration

```yaml
# Prometheus scrape config
scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true

  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-jmx-exporter:9404']
```

#### DD-041: Grafana Dashboards

| Dashboard | Purpose | Key Metrics |
|-----------|---------|-------------|
| Application Overview | System health | Request rate, error rate, latency |
| Kafka Metrics | Event streaming | Messages/sec, lag, partition status |
| Kubernetes | Cluster health | CPU, memory, pod status |
| Dapr | Service mesh | Invocation count, latency, errors |

#### DD-042: Alert Rules

```yaml
groups:
  - name: todo-chatbot-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"

      - alert: PodNotReady
        expr: kube_pod_status_ready{condition="false"} == 1
        for: 5m
        labels:
          severity: warning
```

---

## 3. Directory Structure

```
Phase-V-Cloud-Deployment/
├── terraform/
│   ├── main.tf                 # Main infrastructure
│   ├── variables.tf            # Input variables
│   ├── outputs.tf              # Output values
│   ├── doks.tf                 # DOKS cluster
│   ├── registry.tf             # Container registry
│   └── database.tf             # Managed database (optional)
│
├── kafka/
│   ├── strimzi-operator.yaml   # Strimzi CRDs and operator
│   ├── kafka-cluster.yaml      # Kafka cluster definition
│   ├── topics.yaml             # Topic definitions
│   └── kafka-ui.yaml           # Kafka UI for debugging
│
├── dapr/
│   ├── dapr-install.yaml       # Dapr control plane
│   ├── components/
│   │   ├── pubsub.yaml         # Kafka pub/sub component
│   │   ├── statestore.yaml     # Redis state store
│   │   └── secrets.yaml        # Secrets component
│   └── config.yaml             # Dapr configuration
│
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yaml     # Prometheus deployment
│   │   └── rules.yaml          # Alert rules
│   ├── grafana/
│   │   ├── grafana.yaml        # Grafana deployment
│   │   └── dashboards/         # Dashboard JSON files
│   ├── loki/
│   │   └── loki.yaml           # Loki for logs
│   └── jaeger/
│       └── jaeger.yaml         # Jaeger for tracing
│
├── ci-cd/
│   └── .github/
│       └── workflows/
│           ├── ci.yml          # Test and lint
│           ├── build.yml       # Build images
│           └── deploy.yml      # Deploy to DOKS
│
├── helm/
│   └── todo-chatbot-cloud/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-staging.yaml
│       ├── values-production.yaml
│       └── templates/
│           ├── deployment.yaml
│           ├── service.yaml
│           ├── ingress.yaml
│           ├── dapr-annotations.yaml
│           └── hpa.yaml
│
└── docs/
    ├── SETUP.md                # Initial setup guide
    ├── DEPLOYMENT.md           # Deployment procedures
    ├── MONITORING.md           # Monitoring guide
    ├── TROUBLESHOOTING.md      # Common issues
    └── RUNBOOK.md              # Operational runbook
```

---

## 4. Implementation Phases

### Phase 5A: Infrastructure Foundation (Days 1-3)
1. Set up Terraform configuration
2. Provision DOKS cluster
3. Set up Container Registry
4. Configure kubectl access
5. Deploy NGINX Ingress Controller
6. Set up cert-manager for SSL

### Phase 5B: Kafka Integration (Days 4-6)
1. Deploy Strimzi operator
2. Create Kafka cluster
3. Define topics
4. Implement event producers in backend
5. Test event publishing

### Phase 5C: Dapr Integration (Days 7-9)
1. Install Dapr on cluster
2. Configure Dapr components
3. Update deployments with Dapr annotations
4. Implement service invocation
5. Configure pub/sub with Kafka

### Phase 5D: CI/CD Pipeline (Days 10-12)
1. Create GitHub Actions workflows
2. Set up secrets in GitHub
3. Configure DO Container Registry authentication
4. Implement build and push pipeline
5. Implement deployment pipeline

### Phase 5E: Monitoring & Observability (Days 13-15)
1. Deploy Prometheus
2. Deploy Grafana with dashboards
3. Deploy Loki for logs
4. Configure alert rules
5. Set up notification channels

### Phase 5F: Production Hardening (Days 16-18)
1. Configure HPA for auto-scaling
2. Implement network policies
3. Set up RBAC
4. Configure backup procedures
5. Create runbook documentation

---

## 5. Security Considerations

### 5.1 Network Security
- All internal communication via private VPC
- Network policies restricting pod-to-pod communication
- Ingress only through load balancer

### 5.2 Secret Management
- Kubernetes secrets for sensitive data
- Dapr secrets component for application access
- GitHub Actions secrets for CI/CD

### 5.3 Access Control
- RBAC for cluster access
- Service accounts for pods
- Limited external access

---

## 6. Cost Estimation

| Resource | Specification | Monthly Cost |
|----------|---------------|--------------|
| DOKS Cluster | 3x s-2vcpu-4gb nodes | ~$72 |
| Load Balancer | 1x standard | ~$12 |
| Container Registry | Basic tier | ~$5 |
| Block Storage | 50GB for Kafka | ~$5 |
| Managed DB (optional) | Basic PostgreSQL | ~$15 |
| **Total** | | **~$109/month** |

*Note: Costs may vary. Auto-scaling could increase costs during high load.*

---

## 7. Rollback Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    ROLLBACK PROCEDURE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Detect Failure (automated or manual)                    │
│           │                                                  │
│           ▼                                                  │
│  2. helm rollback todo-chatbot [revision]                   │
│           │                                                  │
│           ▼                                                  │
│  3. Verify rollback successful                              │
│           │                                                  │
│           ▼                                                  │
│  4. Investigate root cause                                  │
│           │                                                  │
│           ▼                                                  │
│  5. Fix issue and redeploy                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Architect | | | |
| DevOps Lead | | | |
| Security | | | |
