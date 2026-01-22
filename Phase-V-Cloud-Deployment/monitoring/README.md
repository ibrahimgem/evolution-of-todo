# Phase V: Enterprise Cloud Deployment - Monitoring Stack

## Overview

This directory contains the complete monitoring stack for the Todo Chatbot application, implementing Prometheus for metrics, Grafana for visualization, Loki for log aggregation, and Jaeger for distributed tracing.

**[Task]: T041-T050**
**[From]: speckit.specify §3.5, speckit.plan §2.5**

## Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Monitoring Stack Architecture                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  Frontend   │    │   Backend   │    │   Kafka     │             │
│  │  (Next.js)  │    │  (Python)   │    │  (Strimzi)  │             │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘             │
│         │                  │                  │                     │
│         └──────────────────┼──────────────────┘                     │
│                            │                                        │
│                            ▼                                        │
│              ┌─────────────────────────┐                            │
│              │   Promtail (Log Agent)  │                            │
│              │   - Log collection      │                            │
│              │   - Kubernetes pods     │                            │
│              │   - Docker containers   │                            │
│              └───────────┬─────────────┘                            │
│                          │                                          │
│                          ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      Data Storage Layer                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │  │
│  │  │Prometheus│  │   Loki   │  │ Jaeger   │  │Elastic   │     │  │
│  │  │(Metrics) │  │ (Logs)   │  │(Traces)  │  │search    │     │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                          │                                          │
│                          ▼                                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                   Visualization & Alerting                    │  │
│  │  ┌────────────────────────────────────────────────────────┐   │  │
│  │  │                   Grafana                              │   │  │
│  │  │  - Dashboards    - Alerting    - SSO Integration      │   │  │
│  │  └────────────────────────────────────────────────────────┘   │  │
│  │                                                                 │  │
│  │  ┌────────────────────────────────────────────────────────┐   │  │
│  │  │                   AlertManager                         │   │  │
│  │  │  - Alert routing    - Notifications    - Silencing    │   │  │
│  │  └────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Prometheus (`prometheus-deployment.yaml`)

**Purpose**: Metrics collection and storage

**Features**:
- Multi-replica deployment (2 replicas)
- Persistent storage (50GB)
- Alerting rules and recording rules
- Service discovery for Kubernetes
- Dapr metrics scraping
- Kafka metrics scraping

**Key Configuration**:
```yaml
scrape_interval: 15s
storage:
  tsdb:
    path: /prometheus
    retention: 15d
```

**Resources**:
```yaml
requests:
  memory: 512Mi
  cpu: 250m
limits:
  memory: 2Gi
  cpu: 1000m
```

### 2. Grafana (`grafana-deployment.yaml`)

**Purpose**: Visualization and dashboards

**Features**:
- Pre-configured dashboards:
  - Overview Dashboard
  - Application Performance Dashboard
  - Kafka Metrics Dashboard
  - Infrastructure Dashboard
- Data sources:
  - Prometheus (metrics)
  - Loki (logs)
  - Jaeger (traces)
- Basic authentication via ingress
- Persistent storage (10GB)

**Dashboards**:
1. **Overview**: Request rate, error rate, latency, active users
2. **Application Performance**: Request distribution, throughput, database queries
3. **Kafka**: Message rate, under-replicated partitions, request rate
4. **Infrastructure**: CPU, memory, pod status, network I/O

### 3. Loki (`loki-deployment.yaml`)

**Purpose**: Log aggregation

**Components**:
- **Loki**: Log storage and querying (2 replicas)
- **Promtail**: Log collection daemon (DaemonSet)

**Features**:
- 720-hour (30-day) log retention
- Kubernetes pod log collection
- Docker container log collection
- JSON log parsing and labeling
- Persistent storage (100GB)

### 4. Jaeger (`jaeger-deployment.yaml`)

**Purpose**: Distributed tracing

**Components**:
- **Collector**: Span collection and processing (2 replicas)
- **Query**: Trace querying and UI (2 replicas)
- **Agent**: Sidecar agent for span collection (DaemonSet)
- **Elasticsearch**: Span storage (1 node)

**Features**:
- OpenTelemetry and Jaeger protocol support
- Zipkin compatibility
- Trace-based alerting
- Persistent storage (50GB)

## Deployment

### Prerequisites
- Kubernetes cluster (DOKS)
- kubectl configured
- Helm 3.x (optional)

### Deploy Monitoring Stack

```bash
# Deploy all monitoring components
kubectl apply -f monitoring/

# Check deployment status
kubectl get pods -n monitoring

# View logs
kubectl logs -n monitoring -l app.kubernetes.io/name=prometheus
```

### Access Monitoring Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| Prometheus | prometheus.todo-chatbot.example.com | Basic auth |
| Grafana | grafana.todo-chatbot.example.com | admin/password |
| Jaeger | jaeger.todo-chatbot.example.com | Basic auth |

### Verify Installation

```bash
# Check Prometheus targets
kubectl exec -n monitoring prometheus-0 -- curl localhost:9090/api/v1/targets

# Check Grafana datasources
kubectl exec -n monitoring grafana-0 -- curl -u admin:password \
  localhost:3000/api/datasources

# Query logs from Loki
kubectl exec -n monitoring loki-0 -- curl localhost:3100/loki/api/v1/query \
  --data-raw 'query={namespace="default"}'
```

## Metrics Reference

### Application Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | HTTP request duration |
| `todo_tasks_completed_total` | Counter | Total completed tasks |
| `todo_tasks_created_total` | Counter | Total created tasks |
| `chat_messages_total` | Counter | Total chat messages |
| `user_sessions_active` | Gauge | Active user sessions |

### Kafka Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kafka_server_broker_topic_messages_in_per_sec` | Rate | Messages per second |
| `kafka_server_replicamanager_underreplicatedpartitions` | Gauge | Under-replicated partitions |
| `kafka_controller_kafkacontroller_offlinepartitionscount` | Gauge | Offline partitions |
| `kafka_server_broker_topic_requests_per_sec` | Rate | Requests per second |

### Infrastructure Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `container_cpu_usage_seconds_total` | Counter | CPU usage |
| `container_memory_working_set_bytes` | Gauge | Memory usage |
| `kube_pod_status_ready` | Gauge | Pod readiness status |
| `kube_deployment_status_replicas_ready` | Gauge | Deployment ready replicas |

## Alerting Rules

### Critical Alerts

| Alert | Expression | Description |
|-------|------------|-------------|
| `HighErrorRate` | Error rate > 5% for 5m | Service experiencing high errors |
| `KafkaOfflinePartitions` | Offline partitions > 0 | Kafka cluster issue |
| `DaprSidecarDown` | Dapr sidecar not responding | Sidecar failure |

### Warning Alerts

| Alert | Expression | Description |
|-------|------------|-------------|
| `HighLatency` | P95 latency > 2s | Performance degradation |
| `HighCPUUsage` | CPU > 90% for 10m | Resource pressure |
| `HighMemoryUsage` | Memory > 90% for 10m | Resource pressure |
| `PodNotReady` | Pod not ready for 5m | Deployment issue |

## Log Query Examples

### Loki Log Queries

```logql
# Error logs in last hour
{namespace="default"} | json | level="error"

# Frontend logs
{app_kubernetes_io_name="todo-chatbot-frontend"} |= "ERROR"

# Backend API logs
{app_kubernetes_io_name="todo-chatbot-backend"} | json | duration > 1s

# Kafka logs
{namespace="kafka"} |= "ERROR"
```

### Log Parsing

```yaml
# Example log format
{
  "level": "info",
  "msg": "Task created",
  "service": "backend",
  "time": "2024-01-15T10:30:00Z"
}
```

## Tracing

### Jaeger Query Examples

```promql
# Find traces by service
service = "todo-chatbot-backend"

# Find slow traces
duration > 5s

# Find traces with errors
tag(error=true)

# Find traces by operation
operation = "POST /api/tasks"
```

### Trace Sampling

```yaml
# Dapr tracing configuration
dapr.io/tracing-sampling-rate: "1"  # 100% sampling
dapr.io/tracing-otel-scraper-url: "http://jaeger-collector:14268/api/traces"
```

## Troubleshooting

### Common Issues

1. **Prometheus not scraping targets**
   ```bash
   # Check service discovery
   kubectl exec -n monitoring prometheus-0 -- \
     curl localhost:9090/api/v1/targets
   ```

2. **Grafana dashboards not loading**
   ```bash
   # Check datasource configuration
   kubectl exec -n monitoring grafana-0 -- \
     curl -u admin:password localhost:3000/api/datasources
   ```

3. **No logs in Loki**
   ```bash
   # Check Promtail logs
   kubectl logs -n monitoring -l app.kubernetes.io/name=promtail

   # Verify log paths
   kubectl exec -n monitoring promtail-xxx -- ls /var/log
   ```

4. **Jaeger spans not appearing**
   ```bash
   # Check collector logs
   kubectl logs -n monitoring -l app.kubernetes.io/name=jaeger-collector

   # Verify Elasticsearch connection
   kubectl exec -n monitoring elasticsearch-0 -- \
     curl localhost:9200/_cat/indices
   ```

### Debug Commands

```bash
# Prometheus metrics endpoint
kubectl exec -n monitoring prometheus-0 -- \
  curl localhost:9090/metrics

# Grafana health check
kubectl exec -n monitoring grafana-0 -- \
  curl -u admin:password localhost:3000/api/health

# Loki readiness
kubectl exec -n monitoring loki-0 -- \
  curl localhost:3100/ready

# Jaeger health
kubectl exec -n monitoring jaeger-query-0 -- \
  curl localhost:16687/
```

## Performance Optimization

### Prometheus Tuning

```yaml
# Increase scrape interval for high-volume services
scrape_interval: 30s

# Reduce retention for cost optimization
storage:
  tsdb:
    retention: 7d

# Limit queries
query:
  max_concurrency: 5
  timeout: 2m
```

### Loki Tuning

```yaml
# Reduce log retention
retention_period: 168h  # 7 days

# Limit queries
querier:
  max_concurrent: 8

# Increase compression
chunk_store_config:
  max_look_back_period: 168h
```

### Grafana Optimization

```yaml
# Reduce refresh rate
refresh: 1m

# Limit data points
max_data_points: 1000

# Use dashboard variables
```

## Cost Management

### Resource Recommendations

| Component | CPU Request | Memory Request | Storage |
|-----------|-------------|----------------|---------|
| Prometheus | 250m | 512Mi | 50GB |
| Grafana | 100m | 256Mi | 10GB |
| Loki | 100m | 256Mi | 100GB |
| Jaeger | 100m | 256Mi | 50GB |
| Promtail | 50m | 128Mi | N/A |
| Elasticsearch | 250m | 512Mi | 50GB |

### Cost Reduction Strategies

1. **Adjust retention periods** based on compliance requirements
2. **Use downsampling** for historical data
3. **Limit log volume** with sampling
4. **Schedule resource-intensive queries** during off-peak hours
5. **Use spot instances** where possible

## Integration with Dapr

### Dapr Tracing Configuration

```yaml
# Backend deployment annotations
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-chatbot-backend"
  dapr.io/config: "todo-chatbot-config"

# Configuration for tracing
spec:
  tracing:
    enabled: true
    exporterType: "zipkin"
    exporterAddress: "http://jaeger-collector:9411/api/v2/spans"
    samplingRate: "1"
```

### Dapr Metrics

Dapr automatically exposes metrics on port 9090:
- `dapr_http_server_handled_total`
- `dapr_grpc_server_handled_total`
- `dapr_sidecar_injected`
- `dapr_component_loaded`

## Best Practices

### 1. Dashboard Design

- Use consistent color schemes
- Include time range selectors
- Add description tooltips
- Use appropriate graph types
- Include related links

### 2. Alert Configuration

- Set appropriate thresholds
- Use multi-stage alerts (warning before critical)
- Add runbook links
- Test alert rules
- Avoid alert fatigue

### 3. Log Management

- Use structured logging
- Include correlation IDs
- Set appropriate log levels
- Implement log rotation
- Monitor log volume

### 4. Tracing Strategy

- Trace critical paths only
- Use sampling for high-volume services
- Include business context in spans
- Set appropriate span duration limits

## Next Steps

After monitoring stack deployment:

1. **Configure Alerts**: Set up AlertManager routes and receivers
2. **Integrate with PagerDuty**: Add on-call rotations
3. **Set up SLOs**: Define service level objectives
4. **Create Runbooks**: Document incident response procedures
5. **Implement SLO Monitoring**: Track reliability metrics

## Related Documentation

- [Phase V Specification](../specs/005-cloud-deployment/spec.md)
- [Phase V Architecture Plan](../specs/005-cloud-deployment/plan.md)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.io/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Dapr Observability](https://docs.dapr.io/operations/observability/)

## Support

For monitoring issues:

1. Check component logs: `kubectl logs -n monitoring -l app.kubernetes.io/name=<component>`
2. Verify resource availability: `kubectl top pods -n monitoring`
3. Check service endpoints: `kubectl get endpoints -n monitoring`
4. Review network policies: `kubectl get networkpolicies -n monitoring`
5. Check resource quotas: `kubectl get resourcequota -n monitoring`
