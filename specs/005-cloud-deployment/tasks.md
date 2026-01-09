# Phase V: Enterprise Cloud Deployment - Tasks

## Document Information
- **Phase**: V
- **Version**: 1.0.0
- **Status**: Draft
- **Created**: 2026-01-08
- **From**: spec.md, plan.md

---

## Task Overview

| Phase | Tasks | Priority | Estimated Days |
|-------|-------|----------|----------------|
| 5A: Infrastructure | T001-T010 | P1 | 3 |
| 5B: Kafka | T011-T020 | P1 | 3 |
| 5C: Dapr | T021-T030 | P1 | 3 |
| 5D: CI/CD | T031-T040 | P2 | 3 |
| 5E: Monitoring | T041-T050 | P2 | 3 |
| 5F: Hardening | T051-T060 | P3 | 3 |

---

## Phase 5A: Infrastructure Foundation

### T001: Create Terraform Project Structure
**Priority**: P1 | **From**: plan.md §DD-001
**Description**: Set up Terraform project with proper structure for DOKS provisioning
**Preconditions**: Terraform installed, DigitalOcean account with API token
**Outputs**:
- [ ] `terraform/main.tf` - Provider configuration
- [ ] `terraform/variables.tf` - Input variables
- [ ] `terraform/outputs.tf` - Output definitions
- [ ] `terraform/versions.tf` - Version constraints

### T002: Provision DOKS Cluster
**Priority**: P1 | **From**: spec.md §US1, plan.md §DD-001
**Description**: Create DigitalOcean Kubernetes cluster with Terraform
**Preconditions**: T001 complete
**Outputs**:
- [ ] `terraform/doks.tf` - DOKS cluster resource
- [ ] Cluster provisioned with 3 worker nodes
- [ ] Auto-scaling configured (3-10 nodes)
- [ ] kubectl configured to access cluster

### T003: Set Up Container Registry
**Priority**: P1 | **From**: plan.md §DD-002
**Description**: Create DigitalOcean Container Registry for images
**Preconditions**: T001 complete
**Outputs**:
- [ ] `terraform/registry.tf` - Registry resource
- [ ] Registry created with basic tier
- [ ] Docker configured to push to registry

### T004: Configure kubectl and Helm Access
**Priority**: P1 | **From**: spec.md §US1
**Description**: Set up local tools to access DOKS cluster
**Preconditions**: T002 complete
**Outputs**:
- [ ] kubeconfig downloaded and configured
- [ ] kubectl can list nodes
- [ ] Helm can deploy charts

### T005: Deploy NGINX Ingress Controller
**Priority**: P1 | **From**: plan.md §2.1
**Description**: Install NGINX Ingress for external traffic routing
**Preconditions**: T004 complete
**Outputs**:
- [ ] Ingress controller deployed via Helm
- [ ] Load balancer provisioned automatically
- [ ] External IP assigned

### T006: Set Up cert-manager for SSL
**Priority**: P1 | **From**: spec.md §US1
**Description**: Install cert-manager for automatic SSL certificate management
**Preconditions**: T005 complete
**Outputs**:
- [ ] cert-manager deployed via Helm
- [ ] ClusterIssuer for Let's Encrypt configured
- [ ] Test certificate issued successfully

### T007: Configure DNS and Domain
**Priority**: P1 | **From**: spec.md §US1
**Description**: Set up custom domain pointing to load balancer
**Preconditions**: T005 complete, domain available
**Outputs**:
- [ ] A record pointing to load balancer IP
- [ ] Domain resolves correctly
- [ ] Ingress configured with domain

### T008: Deploy Application to DOKS (Basic)
**Priority**: P1 | **From**: spec.md §US1
**Description**: Deploy frontend and backend using Phase IV Helm charts
**Preconditions**: T003, T004, T007 complete
**Outputs**:
- [ ] Images pushed to DO Container Registry
- [ ] Helm charts updated for cloud deployment
- [ ] Application accessible via domain

### T009: Verify Health Checks and SSL
**Priority**: P1 | **From**: spec.md §US1
**Description**: Ensure application is healthy with valid SSL
**Preconditions**: T008 complete
**Outputs**:
- [ ] Health endpoints return 200
- [ ] SSL certificate valid
- [ ] HTTPS redirect working

### T010: Document Infrastructure Setup
**Priority**: P1 | **From**: plan.md §3
**Description**: Create documentation for infrastructure
**Preconditions**: T001-T009 complete
**Outputs**:
- [ ] `docs/SETUP.md` - Setup instructions
- [ ] Terraform state backup configured
- [ ] Access credentials documented securely

---

## Phase 5B: Kafka Integration

### T011: Deploy Strimzi Operator
**Priority**: P1 | **From**: plan.md §DD-010
**Description**: Install Strimzi Kafka operator on DOKS
**Preconditions**: Phase 5A complete
**Outputs**:
- [ ] `kafka/strimzi-operator.yaml` - Operator deployment
- [ ] Strimzi CRDs installed
- [ ] Operator running in kafka namespace

### T012: Create Kafka Cluster
**Priority**: P1 | **From**: plan.md §DD-010
**Description**: Deploy 3-broker Kafka cluster with Zookeeper
**Preconditions**: T011 complete
**Outputs**:
- [ ] `kafka/kafka-cluster.yaml` - Cluster definition
- [ ] 3 Kafka brokers running
- [ ] 3 Zookeeper nodes running
- [ ] Persistent storage attached

### T013: Create Kafka Topics
**Priority**: P1 | **From**: plan.md §DD-011
**Description**: Define and create Kafka topics for events
**Preconditions**: T012 complete
**Outputs**:
- [ ] `kafka/topics.yaml` - Topic definitions
- [ ] `todo-events` topic (6 partitions)
- [ ] `chat-events` topic (6 partitions)
- [ ] `user-events` topic (3 partitions)
- [ ] `dlq` topic (3 partitions)

### T014: Deploy Kafka UI
**Priority**: P2 | **From**: plan.md §DD-010
**Description**: Deploy Kafka UI for debugging and monitoring
**Preconditions**: T012 complete
**Outputs**:
- [ ] `kafka/kafka-ui.yaml` - UI deployment
- [ ] Kafka UI accessible via ingress
- [ ] Can browse topics and messages

### T015: Create Event Schemas
**Priority**: P1 | **From**: spec.md §Appendix A
**Description**: Define event schemas for Kafka messages
**Preconditions**: T013 complete
**Outputs**:
- [ ] `kafka/schemas/task-event.json`
- [ ] `kafka/schemas/chat-event.json`
- [ ] `kafka/schemas/user-event.json`

### T016: Implement Kafka Producer in Backend
**Priority**: P1 | **From**: spec.md §US2
**Description**: Add Kafka producer to backend for task events
**Preconditions**: T013, T015 complete
**Outputs**:
- [ ] `backend/src/kafka/producer.py` - Kafka producer
- [ ] Task CRUD operations publish events
- [ ] Events follow defined schema

### T017: Implement Kafka Consumer (Optional)
**Priority**: P2 | **From**: spec.md §US2
**Description**: Create consumer for processing events (analytics, notifications)
**Preconditions**: T016 complete
**Outputs**:
- [ ] `backend/src/kafka/consumer.py` - Kafka consumer
- [ ] Consumer group configured
- [ ] Events processed and logged

### T018: Implement Dead Letter Queue Handling
**Priority**: P2 | **From**: spec.md §US2
**Description**: Handle failed messages with DLQ
**Preconditions**: T016 complete
**Outputs**:
- [ ] Failed messages sent to DLQ topic
- [ ] DLQ monitoring configured
- [ ] Retry mechanism documented

### T019: Test Kafka Integration
**Priority**: P1 | **From**: spec.md §US2
**Description**: Verify Kafka is working end-to-end
**Preconditions**: T016 complete
**Outputs**:
- [ ] Create task → event published
- [ ] Event visible in Kafka UI
- [ ] Consumer receives event

### T020: Document Kafka Setup
**Priority**: P1 | **From**: plan.md §3
**Description**: Document Kafka configuration and usage
**Preconditions**: T011-T019 complete
**Outputs**:
- [ ] `docs/KAFKA.md` - Kafka documentation
- [ ] Event schemas documented
- [ ] Troubleshooting guide

---

## Phase 5C: Dapr Integration

### T021: Install Dapr on DOKS
**Priority**: P1 | **From**: plan.md §DD-020
**Description**: Deploy Dapr control plane to cluster
**Preconditions**: Phase 5A complete
**Outputs**:
- [ ] `dapr/dapr-install.yaml` - Dapr installation
- [ ] Dapr operator running
- [ ] Dapr sidecar injector running
- [ ] Dapr dashboard accessible

### T022: Configure Pub/Sub Component (Kafka)
**Priority**: P1 | **From**: plan.md §DD-020
**Description**: Create Dapr pub/sub component using Kafka
**Preconditions**: T021, Phase 5B complete
**Outputs**:
- [ ] `dapr/components/pubsub.yaml` - Pub/sub config
- [ ] Component connects to Kafka brokers
- [ ] Test publish/subscribe works

### T023: Configure State Store Component (Redis)
**Priority**: P2 | **From**: plan.md §DD-020
**Description**: Deploy Redis and configure Dapr state store
**Preconditions**: T021 complete
**Outputs**:
- [ ] Redis deployed via Helm
- [ ] `dapr/components/statestore.yaml` - State store config
- [ ] Test state operations work

### T024: Configure Secrets Component
**Priority**: P2 | **From**: plan.md §DD-020
**Description**: Configure Dapr to use Kubernetes secrets
**Preconditions**: T021 complete
**Outputs**:
- [ ] `dapr/components/secrets.yaml` - Secrets config
- [ ] Application can read secrets via Dapr

### T025: Update Backend Deployment for Dapr
**Priority**: P1 | **From**: plan.md §DD-021
**Description**: Add Dapr annotations to backend deployment
**Preconditions**: T021 complete
**Outputs**:
- [ ] Backend deployment has Dapr annotations
- [ ] Dapr sidecar injected
- [ ] Backend app-id: "backend"

### T026: Update Frontend Deployment for Dapr
**Priority**: P1 | **From**: plan.md §DD-021
**Description**: Add Dapr annotations to frontend deployment
**Preconditions**: T021 complete
**Outputs**:
- [ ] Frontend deployment has Dapr annotations
- [ ] Dapr sidecar injected
- [ ] Frontend app-id: "frontend"

### T027: Implement Service Invocation via Dapr
**Priority**: P1 | **From**: plan.md §DD-022
**Description**: Update frontend to call backend via Dapr
**Preconditions**: T025, T026 complete
**Outputs**:
- [ ] Frontend calls backend via Dapr sidecar
- [ ] Service discovery automatic
- [ ] Retries and timeouts configured

### T028: Implement Pub/Sub via Dapr
**Priority**: P1 | **From**: spec.md §US3
**Description**: Use Dapr pub/sub instead of direct Kafka
**Preconditions**: T022, T025 complete
**Outputs**:
- [ ] Backend publishes via Dapr pub/sub
- [ ] Dapr routes to Kafka
- [ ] Same event schema maintained

### T029: Test Dapr Integration
**Priority**: P1 | **From**: spec.md §US3
**Description**: Verify Dapr is working correctly
**Preconditions**: T025-T028 complete
**Outputs**:
- [ ] Service invocation works
- [ ] Pub/sub works
- [ ] State store works (if configured)

### T030: Document Dapr Setup
**Priority**: P1 | **From**: plan.md §3
**Description**: Document Dapr configuration and usage
**Preconditions**: T021-T029 complete
**Outputs**:
- [ ] `docs/DAPR.md` - Dapr documentation
- [ ] Component configurations documented
- [ ] Troubleshooting guide

---

## Phase 5D: CI/CD Pipeline

### T031: Create GitHub Actions CI Workflow
**Priority**: P2 | **From**: plan.md §DD-030
**Description**: Set up continuous integration workflow
**Preconditions**: GitHub repository access
**Outputs**:
- [ ] `.github/workflows/ci.yml` - CI workflow
- [ ] Runs on pull requests
- [ ] Runs tests and linting

### T032: Create GitHub Actions Build Workflow
**Priority**: P2 | **From**: plan.md §DD-030
**Description**: Set up container image build workflow
**Preconditions**: T031 complete
**Outputs**:
- [ ] `.github/workflows/build.yml` - Build workflow
- [ ] Builds frontend and backend images
- [ ] Tags with git SHA

### T033: Configure DO Registry Authentication
**Priority**: P2 | **From**: spec.md §US4
**Description**: Set up GitHub secrets for DO Registry
**Preconditions**: T003 complete
**Outputs**:
- [ ] `DIGITALOCEAN_ACCESS_TOKEN` secret
- [ ] `REGISTRY_NAME` secret
- [ ] Docker login works in workflow

### T034: Create GitHub Actions Deploy Workflow
**Priority**: P2 | **From**: plan.md §DD-030
**Description**: Set up continuous deployment workflow
**Preconditions**: T032, T033 complete
**Outputs**:
- [ ] `.github/workflows/deploy.yml` - Deploy workflow
- [ ] Pushes images to DO Registry
- [ ] Deploys via Helm

### T035: Configure kubeconfig for GitHub Actions
**Priority**: P2 | **From**: spec.md §US4
**Description**: Set up DOKS access from GitHub Actions
**Preconditions**: T002, T034 complete
**Outputs**:
- [ ] `KUBE_CONFIG` secret configured
- [ ] kubectl works in workflow
- [ ] Helm upgrade works

### T036: Implement Staging Deployment
**Priority**: P2 | **From**: spec.md §US4
**Description**: Create staging environment and workflow
**Preconditions**: T034, T035 complete
**Outputs**:
- [ ] Staging namespace created
- [ ] `values-staging.yaml` configured
- [ ] Deploy to staging on PR merge

### T037: Implement Production Deployment
**Priority**: P2 | **From**: spec.md §US4
**Description**: Create production deployment with approval
**Preconditions**: T036 complete
**Outputs**:
- [ ] Production namespace created
- [ ] `values-production.yaml` configured
- [ ] Manual approval required for prod

### T038: Implement Rollback Mechanism
**Priority**: P2 | **From**: spec.md §US4
**Description**: Add rollback capability to pipeline
**Preconditions**: T034 complete
**Outputs**:
- [ ] Rollback workflow/script
- [ ] `helm rollback` automated
- [ ] Documented procedure

### T039: Add Notifications
**Priority**: P3 | **From**: spec.md §US4
**Description**: Add Slack/Discord notifications for deployments
**Preconditions**: T034 complete
**Outputs**:
- [ ] Slack webhook configured
- [ ] Success/failure notifications
- [ ] Deployment summary included

### T040: Document CI/CD Pipeline
**Priority**: P2 | **From**: plan.md §3
**Description**: Document CI/CD setup and usage
**Preconditions**: T031-T039 complete
**Outputs**:
- [ ] `docs/CICD.md` - CI/CD documentation
- [ ] Workflow diagrams
- [ ] Secrets management documented

---

## Phase 5E: Monitoring & Observability

### T041: Deploy Prometheus
**Priority**: P2 | **From**: plan.md §DD-040
**Description**: Deploy Prometheus for metrics collection
**Preconditions**: Phase 5A complete
**Outputs**:
- [ ] `monitoring/prometheus/prometheus.yaml`
- [ ] Prometheus deployed via Helm
- [ ] Service discovery configured

### T042: Configure Application Metrics
**Priority**: P2 | **From**: spec.md §US5
**Description**: Add metrics endpoints to applications
**Preconditions**: T041 complete
**Outputs**:
- [ ] Backend `/metrics` endpoint
- [ ] Frontend metrics (if applicable)
- [ ] Prometheus scraping metrics

### T043: Deploy Grafana
**Priority**: P2 | **From**: plan.md §DD-041
**Description**: Deploy Grafana for visualization
**Preconditions**: T041 complete
**Outputs**:
- [ ] `monitoring/grafana/grafana.yaml`
- [ ] Grafana deployed via Helm
- [ ] Prometheus data source configured

### T044: Create Grafana Dashboards
**Priority**: P2 | **From**: plan.md §DD-041
**Description**: Create dashboards for application monitoring
**Preconditions**: T043 complete
**Outputs**:
- [ ] Application Overview dashboard
- [ ] Kubernetes dashboard
- [ ] Kafka dashboard
- [ ] Dapr dashboard

### T045: Deploy Loki for Logs
**Priority**: P2 | **From**: spec.md §US5
**Description**: Deploy Loki for log aggregation
**Preconditions**: T043 complete
**Outputs**:
- [ ] `monitoring/loki/loki.yaml`
- [ ] Loki deployed via Helm
- [ ] Grafana data source configured
- [ ] Logs visible in Grafana

### T046: Deploy Jaeger for Tracing
**Priority**: P3 | **From**: spec.md §US5
**Description**: Deploy Jaeger for distributed tracing
**Preconditions**: Phase 5A complete
**Outputs**:
- [ ] `monitoring/jaeger/jaeger.yaml`
- [ ] Jaeger deployed via Helm
- [ ] Traces visible in UI

### T047: Configure Alert Rules
**Priority**: P2 | **From**: plan.md §DD-042
**Description**: Create Prometheus alert rules
**Preconditions**: T041 complete
**Outputs**:
- [ ] `monitoring/prometheus/rules.yaml`
- [ ] High error rate alert
- [ ] Pod not ready alert
- [ ] Kafka lag alert

### T048: Configure Alert Manager
**Priority**: P2 | **From**: spec.md §US5
**Description**: Set up alert routing and notifications
**Preconditions**: T047 complete
**Outputs**:
- [ ] Alert Manager deployed
- [ ] Slack integration configured
- [ ] Alert routing rules defined

### T049: Test Monitoring Stack
**Priority**: P2 | **From**: spec.md §US5
**Description**: Verify monitoring is working end-to-end
**Preconditions**: T041-T048 complete
**Outputs**:
- [ ] Metrics visible in Grafana
- [ ] Logs visible in Grafana
- [ ] Alerts fire correctly

### T050: Document Monitoring Setup
**Priority**: P2 | **From**: plan.md §3
**Description**: Document monitoring configuration
**Preconditions**: T041-T049 complete
**Outputs**:
- [ ] `docs/MONITORING.md` - Monitoring guide
- [ ] Dashboard access documented
- [ ] Alert response procedures

---

## Phase 5F: Production Hardening

### T051: Configure Horizontal Pod Autoscaler
**Priority**: P2 | **From**: spec.md §US6
**Description**: Set up HPA for automatic scaling
**Preconditions**: T042 complete (metrics required)
**Outputs**:
- [ ] HPA for frontend (2-10 replicas)
- [ ] HPA for backend (2-10 replicas)
- [ ] Scaling based on CPU/memory

### T052: Configure Pod Disruption Budgets
**Priority**: P2 | **From**: spec.md §US6
**Description**: Ensure minimum availability during updates
**Preconditions**: Phase 5A complete
**Outputs**:
- [ ] PDB for frontend (minAvailable: 1)
- [ ] PDB for backend (minAvailable: 1)

### T053: Implement Network Policies
**Priority**: P2 | **From**: spec.md §US7
**Description**: Restrict pod-to-pod communication
**Preconditions**: Phase 5A complete
**Outputs**:
- [ ] Default deny policy
- [ ] Allow frontend → backend
- [ ] Allow backend → Kafka
- [ ] Allow backend → database

### T054: Configure RBAC
**Priority**: P2 | **From**: spec.md §US7
**Description**: Set up role-based access control
**Preconditions**: Phase 5A complete
**Outputs**:
- [ ] Service accounts for apps
- [ ] Roles for CI/CD
- [ ] ClusterRoles for monitoring

### T055: Enable Secret Encryption
**Priority**: P2 | **From**: spec.md §US7
**Description**: Ensure secrets are encrypted at rest
**Preconditions**: Phase 5A complete
**Outputs**:
- [ ] Encryption config for etcd
- [ ] Verify secrets encrypted

### T056: Implement Image Scanning
**Priority**: P3 | **From**: spec.md §US7
**Description**: Add container image scanning to CI/CD
**Preconditions**: T031 complete
**Outputs**:
- [ ] Trivy or similar scanner added
- [ ] Fails build on critical vulnerabilities
- [ ] Reports generated

### T057: Configure Database Backups
**Priority**: P2 | **From**: spec.md §US6
**Description**: Set up automated database backups
**Preconditions**: Database running
**Outputs**:
- [ ] Daily backups configured
- [ ] 30-day retention
- [ ] Restore procedure tested

### T058: Create Disaster Recovery Runbook
**Priority**: P2 | **From**: spec.md §US6
**Description**: Document DR procedures
**Preconditions**: T057 complete
**Outputs**:
- [ ] `docs/RUNBOOK.md` - Operational runbook
- [ ] Failover procedures
- [ ] Recovery procedures

### T059: Load Testing
**Priority**: P3 | **From**: spec.md §4.1
**Description**: Perform load testing to verify performance
**Preconditions**: Phase 5E complete
**Outputs**:
- [ ] Load test scripts (k6 or similar)
- [ ] 1000 concurrent users tested
- [ ] Performance report generated

### T060: Final Documentation and Handoff
**Priority**: P1 | **From**: plan.md §3
**Description**: Complete all documentation
**Preconditions**: All tasks complete
**Outputs**:
- [ ] `docs/DEPLOYMENT.md` - Complete deployment guide
- [ ] `docs/TROUBLESHOOTING.md` - Common issues
- [ ] Architecture diagrams finalized
- [ ] All credentials documented securely

---

## Task Dependencies Graph

```
Phase 5A (Infrastructure)
T001 ──▶ T002 ──▶ T004 ──▶ T005 ──▶ T006 ──▶ T007 ──▶ T008 ──▶ T009 ──▶ T010
    └──▶ T003 ──────────────────────────────────────────────┘

Phase 5B (Kafka) - Requires Phase 5A
T011 ──▶ T012 ──▶ T013 ──▶ T015 ──▶ T016 ──▶ T017 ──▶ T018 ──▶ T019 ──▶ T020
              └──▶ T014

Phase 5C (Dapr) - Requires Phase 5A, 5B partial
T021 ──▶ T022 ──▶ T025 ──▶ T027 ──▶ T028 ──▶ T029 ──▶ T030
    ├──▶ T023 ──────┘
    ├──▶ T024
    └──▶ T026 ─────────┘

Phase 5D (CI/CD) - Can run parallel to 5B, 5C
T031 ──▶ T032 ──▶ T033 ──▶ T034 ──▶ T035 ──▶ T036 ──▶ T037 ──▶ T038 ──▶ T039 ──▶ T040

Phase 5E (Monitoring) - Requires Phase 5A
T041 ──▶ T042 ──▶ T043 ──▶ T044 ──▶ T045 ──▶ T047 ──▶ T048 ──▶ T049 ──▶ T050
                      └──▶ T046

Phase 5F (Hardening) - Requires all above
T051 ──┬──▶ T059 ──▶ T060
T052 ──┤
T053 ──┤
T054 ──┤
T055 ──┤
T056 ──┤
T057 ──▶ T058
```

---

## Quick Reference

### P1 Tasks (Must Have)
- T001-T010: Infrastructure
- T011-T013, T015-T016, T019-T020: Kafka core
- T021-T022, T025-T030: Dapr core
- T060: Final documentation

### P2 Tasks (Should Have)
- T014, T017-T018: Kafka extras
- T023-T024: Dapr extras
- T031-T040: CI/CD
- T041-T045, T047-T050: Monitoring core
- T051-T055, T057-T058: Hardening

### P3 Tasks (Nice to Have)
- T046: Distributed tracing
- T039: Notifications
- T056: Image scanning
- T059: Load testing
