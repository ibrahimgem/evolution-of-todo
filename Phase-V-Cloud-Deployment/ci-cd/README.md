# Phase V: Enterprise Cloud Deployment - CI/CD Pipeline

## Overview

This directory contains the complete CI/CD pipeline configuration for the Todo Chatbot application, implemented using GitHub Actions. The pipeline handles automated building, testing, security scanning, and deployment to DigitalOcean Kubernetes Service (DOKS).

**[Task]: T031-T040**
**[From]: speckit.specify §3.4, speckit.plan §2.4**

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     GitHub Actions CI/CD Pipeline                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │   Push/PR   │───▶│   Quality   │───▶│   Testing   │             │
│  │  Triggered  │    │   Checks    │    │   Backend   │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│                                             │                       │
│                                             ▼                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                        BUILD STAGE                              │ │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │ │
│  │  │   Frontend   │    │   Backend    │    │   Security   │     │ │
│  │  │    Build     │    │    Build     │    │    Scan      │     │ │
│  │  └──────────────┘    └──────────────┘    └──────────────┘     │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                             │                       │
│                                             ▼                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  Terraform  │───▶│   K8s       │───▶│ Integration │             │
│  │   Infra     │    │  Deploy     │    │   Tests     │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│                                             │                       │
│                                             ▼                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                     NOTIFICATIONS & MONITORING                  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Workflow Files

### 1. Main Pipeline (`ci-cd-pipeline.yml`)

The main CI/CD pipeline with 10 jobs:

| Job | Purpose | Triggers |
|-----|---------|----------|
| `code-quality` | Linting, formatting, security scanning | Every push/PR |
| `test-backend` | Python unit tests with coverage | After code-quality |
| `test-frontend` | JavaScript/TypeScript tests | After code-quality |
| `build` | Docker image building and scanning | After tests pass |
| `terraform` | Infrastructure as Code deployment | After build (push to main) |
| `deploy-k8s` | Kubernetes deployment | After terraform |
| `integration-tests` | API and E2E testing | After deployment |
| `notify` | Slack/notification delivery | After deployment |
| `rollback` | Manual rollback workflow | Manual trigger |

### 2. Environment Configuration (`environment-config.yml`)

Manages environment-specific infrastructure:

- **Actions**: plan, apply, destroy
- **Environments**: development, staging, production
- **Regions**: Multiple DigitalOcean regions

### 3. Security Scanning (`security-scan.yml`)

Scheduled and on-demand security scanning:

- Dependency vulnerability scanning
- Dockerfile best practices
- Kubernetes security
- Secret detection
- Code security analysis

## Pipeline Configuration

### Triggers

```yaml
# Automatic triggers
on:
  push:
    branches: [main, develop]
    paths:
      - 'Phase-II-Full-Stack-Web-Application/**'
      - 'Phase-III-AI-Chatbot/**'
      - 'Phase-IV-Local-K8s-Deployment/**'
      - 'Phase-V-Cloud-Deployment/**'
      - '.github/workflows/**'

  pull_request:
    branches: [main, develop]

  # Manual trigger
  workflow_dispatch:
    inputs:
      environment:
        required: true
        default: 'staging'
      skip_tests:
        required: false
        default: 'false'
```

### Environments

The pipeline supports three environments:

| Environment | Purpose | Configuration |
|-------------|---------|---------------|
| `development` | Feature testing | 1-2 nodes, dev resources |
| `staging` | Pre-production testing | 2-5 nodes, staging resources |
| `production` | Live deployment | 3-10 nodes, prod resources |

### Required Secrets

Configure these in GitHub repository settings:

```bash
# Docker Hub
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN

# DigitalOcean
DO_TOKEN

# Kubernetes (base64 encoded kubeconfig)
KUBECONFIG_STAGING
KUBECONFIG_PRODUCTION

# Application Secrets
OPENAI_API_KEY
DATABASE_URL
NEXT_PUBLIC_API_URL

# Notifications
SLACK_WEBHOOK_URL
```

## Pipeline Stages

### 1. Code Quality

- **Frontend**: ESLint, Prettier, TypeScript type checking
- **Backend**: Ruff linting, MyPy type checking
- **Security**: Trivy filesystem scanning

### 2. Testing

**Backend Tests:**
```yaml
- Unit tests with pytest
- Coverage reporting (Codecov)
- Database migrations
- Service integration tests
```

**Frontend Tests:**
```yaml
- TypeScript type checking
- Jest unit tests
- Coverage reporting (Codecov)
- Playwright E2E tests
```

### 3. Build

**Docker Image Building:**
```yaml
- Multi-stage Docker builds
- Build cache (GitHub Actions cache)
- Metadata extraction (tags, labels)
- Vulnerability scanning (Trivy)
```

**Image Tags:**
```yaml
# Tag strategy
- SHA: ${{ github.sha }}
- Branch: ${{ ref }}
- Latest: latest (main branch only)
```

### 4. Infrastructure (Terraform)

**Resources Created:**
- DigitalOcean Kubernetes Cluster (DOKS)
- Container Registry
- Managed PostgreSQL Database
- VPC and Networking
- Load Balancer (optional)
- DNS Records (optional)

**Terraform Workflow:**
```bash
1. terraform init
2. terraform validate
3. terraform plan -out=tfplan
4. terraform apply tfplan
```

### 5. Kubernetes Deployment

**Deployments:**
1. Kafka (Strimzi operator + cluster)
2. Redis (state store)
3. Dapr control plane
4. Backend application
5. Frontend application

**Deployment Strategy:**
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 0
```

**Health Checks:**
```yaml
- Readiness probes
- Liveness probes
- Startup probes
```

### 6. Integration Testing

```python
# Tests performed
- Backend health check
- API endpoint testing
- Database connectivity
- Cache functionality
- Service mesh integration
```

### 7. Notifications

**Channels:**
- Slack (#deployments)
- GitHub commit comments
- Deployment summary

**Events:**
- Deployment started
- Deployment completed
- Deployment failed
- Rollback executed

### 8. Rollback

Manual rollback workflow:
```bash
kubectl rollout undo deployment/todo-chatbot-backend
kubectl rollout undo deployment/todo-chatbot-frontend
```

## Security Features

### Container Security

- **Build-time**: Multi-stage builds, minimal base images
- **Scan-time**: Trivy vulnerability scanning
- **Runtime**: Non-root users, read-only filesystems

### Secrets Management

- GitHub Secrets for sensitive data
- Kubernetes secrets for runtime
- HashiCorp Vault integration (optional)
- Secrets rotation support

### Network Security

- Network policies
- mTLS encryption (Dapr)
- Private container registry
- VPC isolation

## Monitoring & Observability

### Metrics

```yaml
- Build duration
- Test coverage
- Vulnerability count
- Deployment success rate
- API response time
```

### Tracing

```yaml
- Distributed tracing (Jaeger)
- OpenTelemetry integration
- Custom spans for key operations
```

### Logging

```yaml
- Structured JSON logging
- Log aggregation (Loki)
- Log-based alerting
```

## Performance Optimization

### Build Caching

```yaml
- Docker layer caching (GitHub Actions cache)
- NPM package caching
- Python pip caching
- Terraform state caching
```

### Parallel Execution

```yaml
- Frontend and backend tests run in parallel
- Multiple security scans run in parallel
- Independent deployment stages
```

### Resource Optimization

```yaml
- Minimal container images
- Efficient test parallelization
- Optimized CI runner selection
```

## Troubleshooting

### Common Issues

1. **Build failures**
   ```bash
   # Check Docker build logs
   # Verify cache is being used
   # Check for dependency issues
   ```

2. **Terraform failures**
   ```bash
   # Verify DO token is valid
   # Check resource limits
   # Review state locking
   ```

3. **Kubernetes deployment failures**
   ```bash
   # Check pod logs: kubectl logs <pod-name>
   # Check events: kubectl get events
   # Verify kubeconfig is correct
   ```

### Debug Commands

```bash
# View pipeline logs
gh run view <run-id> --log

# Check workflow status
gh run list --workflow=ci-cd-pipeline.yml

# Cancel running workflow
gh run cancel <run-id>

# Rerun workflow
gh run rerun <run-id>
```

## Cost Management

### Optimization Strategies

1. **Use appropriate instance sizes**
   - Development: 1vcpu/1GB
   - Staging: 2vcpu/4GB
   - Production: 2vcpu/4GB (scaled)

2. **Optimize build frequency**
   - Skip tests on documentation changes
   - Use path filtering
   - Cache expensive operations

3. **Resource limits**
   - Set container resource limits
   - Use spot instances where possible
   - Monitor and adjust over time

### Cost Tracking

```yaml
- GitHub Actions minutes usage
- DigitalOcean resource costs
- Container registry storage
- Network bandwidth
```

## Best Practices

### 1. Pipeline Configuration

- Keep pipelines fast (< 15 minutes)
- Fail fast with early checks
- Use caching aggressively
- Parallelize independent jobs

### 2. Security

- Scan every commit
- Require all checks to pass
- Use signed commits
- Rotate secrets regularly

### 3. Deployment

- Use immutable tags
- Implement health checks
- Have a rollback plan
- Monitor deployments

### 4. Testing

- Test in production-like environments
- Automate all tests
- Measure coverage
- Test failure scenarios

## Next Steps

After CI/CD pipeline deployment:

1. **Configure GitHub Secrets** - Set up all required secrets
2. **Set up Environments** - Create staging and production environments
3. **Configure Notifications** - Set up Slack/Discord webhooks
4. **Enable Branch Protection** - Require status checks
5. **Set up Monitoring** - Deploy Prometheus/Grafana
6. **Load Testing** - Add performance test stage
7. **Blue/Green Deployments** - Implement zero-downtime deployments

## Related Documentation

- [Phase V Specification](../specs/005-cloud-deployment/spec.md)
- [Phase V Architecture Plan](../specs/005-cloud-deployment/plan.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Kubernetes Documentation](https://kubernetes.io/docs)

## Support

For CI/CD pipeline issues:

1. Check workflow logs in GitHub Actions
2. Review artifact files for errors
3. Check GitHub status page
4. Review the troubleshooting section above
5. Create an issue in the repository
