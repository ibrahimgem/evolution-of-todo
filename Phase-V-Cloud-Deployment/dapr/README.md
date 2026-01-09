# Phase V: Enterprise Cloud Deployment - Dapr Configuration

## Overview

This directory contains the Dapr (Distributed Application Runtime) configuration for the Todo Chatbot application, enabling microservices patterns with built-in observability, state management, and pub/sub messaging.

**[Task]: T021-T030**
**[From]: speckit.specify §3.3, speckit.plan §2.3**

## Dapr Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Dapr Sidecar  │────▶│   Backend       │
│   (Next.js)     │     │   (Port 3500)   │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                        │
                               ▼                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   Dapr Control  │     │   Kafka         │
                        │   Plane         │     │   (Pub/Sub)     │
                        └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   Redis         │     │   Monitoring    │
                        │   (State Store) │     │   (Prometheus)  │
                        └─────────────────┘     └─────────────────┘
```

## Components

### 1. Dapr Control Plane (`dapr-install.yaml`)
- **Operator**: Manages Dapr components and configurations
- **Sidecar Injector**: Automatically injects Dapr sidecar containers
- **Sentry**: Certificate authority for mTLS
- **Placement**: Actor placement service for distributed actors

### 2. Dapr Components (`components.yaml`)
- **pubsub-kafka**: Kafka-based pub/sub for event streaming
- **statestore**: Redis-based state storage for session management
- **kubernetes-secrets**: Native Kubernetes secret access
- **vault-secrets**: HashiCorp Vault integration (optional)
- **observability**: OpenTelemetry exporter for tracing

### 3. Application Deployments
- **frontend-deployment.yaml**: Next.js frontend with Dapr annotations
- **backend-deployment.yaml**: Python backend with Dapr annotations

### 4. Event Integration
- **dapr-event-producers.py**: Dapr-based event producers
- **dapr-event-consumers.py**: Dapr-based event consumers
- **subscriptions.yaml**: Dapr subscription configuration

## Dapr Building Blocks Used

### Pub/Sub Messaging
```yaml
# Dapr pub/sub configuration
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "todo-chatbot-kafka-kafka-bootstrap.kafka.svc.cluster.local:9093"
```

**Usage**:
```python
# Publishing events
await dapr_client.publish_event(
    pubsub_name="pubsub-kafka",
    topic="todo-events",
    data={"event_type": "TASK_CREATED", "task_id": "123"}
)
```

### State Management
```yaml
# Dapr state store configuration
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
    - name: redisHost
      value: "redis.default.svc.cluster.local:6379"
```

**Usage**:
```python
# Saving state
await dapr_client.save_state(
    store_name="statestore",
    key="user:123",
    value={"name": "John", "email": "john@example.com"}
)

# Getting state
state = await dapr_client.get_state(
    store_name="statestore",
    key="user:123"
)
```

### Secret Management
```yaml
# Dapr secret store configuration
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
```

**Usage**:
```python
# Getting secrets
secret = await dapr_client.get_secret(
    secret_store="kubernetes-secrets",
    key="database-password"
)
```

### Service Invocation
```yaml
# Dapr service invocation (automatic via sidecar)
dapr.io/app-id: "todo-chatbot-backend"
dapr.io/app-port: "3000"
```

**Usage**:
```python
# Invoke another service
response = await dapr_client.invoke_method(
    app_id="todo-chatbot-backend",
    method_name="/api/tasks",
    data={"action": "list"}
)
```

## Deployment

### Prerequisites
- Kubernetes cluster (DOKS) with kubectl access
- Dapr CLI installed locally
- Kafka cluster (from Phase 5B)
- Redis (from components.yaml)

### 1. Install Dapr Control Plane
```bash
# Install Dapr using Helm (recommended)
helm repo add dapr https://dapr.github.io/helm-charts
helm repo update
helm install dapr dapr/dapr \
  --namespace dapr-system \
  --create-namespace \
  --set global.domain="cluster.local" \
  --set dapr_operator.replicas=1 \
  --set dapr_sidecar_injector.replicas=1
```

Or apply manually:
```bash
kubectl apply -f dapr/dapr-install.yaml
```

### 2. Deploy Dapr Components
```bash
kubectl apply -f dapr/components.yaml
```

### 3. Deploy Applications with Dapr Sidecar
```bash
kubectl apply -f dapr/frontend-deployment.yaml
kubectl apply -f dapr/backend-deployment.yaml
```

### 4. Deploy Analytics Consumers
```bash
kubectl apply -f dapr/analytics-consumer-deployment.yaml
```

### 5. Verify Installation
```bash
# Check Dapr control plane
kubectl get pods -n dapr-system

# Check Dapr components
kubectl get components

# Check application pods
kubectl get pods -l app.kubernetes.io/part-of=todo-chatbot
```

## Configuration

### Environment Variables for Applications
```bash
# Backend environment variables
export DAPR_HTTP_PORT=3500
export DAPR_GRPC_PORT=50001
export DAPR_APP_ID=todo-chatbot-backend
export DAPR_CONFIG=todo-chatbot-config
export DAPR_STATE_STORE=statestore
export DAPR_PUBSUB=pubsub-kafka
```

### Dapr Annotations Reference
| Annotation | Description | Example |
|------------|-------------|---------|
| `dapr.io/enabled` | Enable Dapr sidecar | `"true"` |
| `dapr.io/app-id` | Unique application ID | `"todo-chatbot-backend"` |
| `dapr.io/app-port` | Application HTTP port | `"3000"` |
| `dapr.io/config` | Dapr configuration name | `"todo-chatbot-config"` |
| `dapr.io/metrics-port` | Metrics port | `"9090"` |
| `dapr.io/log-level` | Logging level | `"info"` |
| `dapr.io/pubsub-name` | Pub/sub component name | `"pubsub-kafka"` |
| `dapr.io/state-store` | State store component name | `"statestore"` |
| `dapr.io/secret-store` | Secret store component name | `"kubernetes-secrets"` |

## Observability

### Distributed Tracing
```yaml
# Tracing configuration
spec:
  tracing:
    enabled: true
    exporterType: "zipkin"
    exporterAddress: "http://jaeger-collector:9411/api/v2/spans"
    samplingRate: "1"
```

### Metrics
```yaml
# Metrics configuration
spec:
  metrics:
    enabled: true
    port: 9090
    path: "/metrics"
```

### Health Checks
Dapr exposes health check endpoints:
- `/healthz` - Liveness probe
- `/ready` - Readiness probe

## Security

### mTLS (Mutual TLS)
Dapr automatically enables mTLS between sidecars:
```yaml
spec:
  mtls:
    enabled: true
    workloadCertTTL: "24h"
```

### API Token Authentication
```yaml
env:
  - name: DAPR_API_TOKEN
    valueFrom:
      secretKeyRef:
        name: dapr-api-token
        key: dapr-api-token
```

## Resiliency

### Circuit Breaker Configuration
```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: todo-chatbot-resiliency
spec:
  pubsub:
    todo-chatbot-kafka:
      timeout: "5s"
      maxRetries: 3
      circuitBreaker:
        threshold: 0.05
        interval: "30s"
        timeout: "60s"
```

## Troubleshooting

### Common Issues

1. **Sidecar not injected**
   ```bash
   # Check if namespace has dapr.io/enabled label
   kubectl get namespace default --show-labels

   # Check sidecar injector logs
   kubectl logs -n dapr-system -l app=dapr-sidecar-injector
   ```

2. **Pub/sub not working**
   ```bash
   # Check component status
   kubectl get components pubsub-kafka -o yaml

   # Check broker connectivity
   kubectl exec -it <pod-name> -- curl http://localhost:3500/v1.0/healthz
   ```

3. **State store errors**
   ```bash
   # Check Redis connectivity
   kubectl exec -it redis-0 -- redis-cli ping

   # Check state store configuration
   kubectl get components statestore -o yaml
   ```

### Debug Commands
```bash
# Get Dapr sidecar logs
kubectl logs <pod-name> daprd

# Check Dapr API
kubectl exec <pod-name> -- curl http://localhost:3500/v1.0/metadata

# List subscriptions
kubectl exec <pod-name> -- curl http://localhost:3500/v1.0/publish

# Get state store data
kubectl exec <pod-name> -- curl http://localhost:3500/v1.0/state/statestore
```

## Performance Tuning

### Sidecar Resources
```yaml
containers:
  - name: daprd
    resources:
      requests:
        memory: "128Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"
        cpu: "500m"
```

### Kafka Configuration
```yaml
metadata:
  - name: batchSize
    value: "16384"
  - name: batchTimeout
    value: "10ms"
  - name: compression
    value: "gzip"
```

## Cost Optimization

### Resource Recommendations
| Component | CPU Request | Memory Request | Cost Impact |
|-----------|-------------|----------------|-------------|
| Dapr Operator | 100m | 256Mi | Low |
| Sidecar Injector | 50m | 128Mi | Low |
| Application Sidecar | 100m | 256Mi | Medium |

### Recommendations
- Use resource limits to prevent over-provisioning
- Enable auto-scaling for consumers
- Monitor Kafka topic retention policies
- Use Redis eviction policies for cost control

## Next Steps

After Dapr deployment:

1. **Integrate with Backend**: Update backend to use Dapr SDK
2. **Deploy Consumers**: Deploy analytics consumers with Dapr subscriptions
3. **Configure Monitoring**: Set up Prometheus and Grafana dashboards
4. **Load Testing**: Performance test with realistic workloads
5. **Security Hardening**: Implement production security measures

## Related Documentation

- [Phase V Specification](../specs/005-cloud-deployment/spec.md)
- [Phase V Architecture Plan](../specs/005-cloud-deployment/plan.md)
- [Dapr Documentation](https://docs.dapr.io/)
- [Dapr SDK for Python](https://docs.dapr.io/developing-applications/sdks/python/)
- [Dapr SDK for JavaScript](https://docs.dapr.io/developing-applications/sdks/js/)

## Support

For issues with Dapr configuration:

1. Check the [Dapr troubleshooting guide](https://docs.dapr.io/operations/troubleshooting/)
2. Review sidecar logs: `kubectl logs <pod-name> daprd`
3. Check component status: `kubectl get components`
4. Verify network policies: `kubectl get networkpolicies`
5. Check Dapr control plane: `kubectl get pods -n dapr-system`
