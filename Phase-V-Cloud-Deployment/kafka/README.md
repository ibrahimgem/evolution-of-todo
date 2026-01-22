# Phase V: Enterprise Cloud Deployment - Kafka Configuration

## Overview

This directory contains the Apache Kafka configuration and event streaming implementation for the Todo Chatbot application, deployed using Strimzi operator on DOKS.

**[Task]: T011-T020**
**[From]: speckit.specify §3.2, speckit.plan §2.2**

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Backend App   │───▶│     Kafka       │───▶│  Consumers     │
│   (Producers)   │    │   (Strimzi)     │    │ (Analytics)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │    Kafka UI     │
                       │  (Monitoring)   │
                       └─────────────────┘
```

## Components

### 1. Strimzi Operator (`strimzi-operator.yaml`)
- **Purpose**: Kubernetes operator for managing Kafka clusters
- **Features**:
  - Automated Kafka cluster management
  - Topic and user management
  - Security and authentication
  - Monitoring integration
- **Version**: 0.40.0

### 2. Kafka Cluster (`kafka-cluster.yaml`)
- **Brokers**: 3 nodes with KRaft mode (no Zookeeper)
- **Storage**: 10GB persistent storage per broker
- **Listeners**:
  - Internal (port 9092) - Plain text
  - TLS (port 9093) - Encrypted internal
  - External (port 9094) - Encrypted external
- **Features**:
  - High availability with 3 replicas
  - JMX metrics for monitoring
  - Network policies for security

### 3. Topics Configuration (`topics.yaml`)
- **todo-events**: Task CRUD operations (6 partitions, 3 replicas)
- **chat-events**: Conversation events (6 partitions, 3 replicas)
- **user-events**: Authentication events (3 partitions, 3 replicas)
- **dlq**: Dead letter queue (3 partitions, 3 replicas)
- **analytics-events**: Analytics processing (4 partitions, 3 replicas)
- **system-events**: System monitoring (2 partitions, 3 replicas)

### 4. Kafka UI (`kafka-ui.yaml`)
- **Purpose**: Web-based Kafka management and monitoring
- **Features**:
  - Topic visualization and management
  - Message browsing and inspection
  - Consumer group monitoring
  - Schema registry integration
  - JMX metrics dashboard

### 5. Event Producers (`event-producers.py`)
- **TodoEventProducer**: Task CRUD event production
- **ChatEventProducer**: Chat conversation events
- **UserEventProducer**: User authentication events
- **SystemEventProducer**: System health and error events
- **Features**:
  - Async message production
  - Error handling and retries
  - Dead letter queue integration
  - Message schema validation

### 6. Event Consumers (`event-consumers.py`)
- **TaskAnalyticsConsumer**: Task usage analytics
- **ChatAnalyticsConsumer**: Conversation analytics
- **UserBehaviorConsumer**: User behavior patterns
- **SystemMetricsConsumer**: System performance monitoring
- **Features**:
  - Exactly-once processing
  - Consumer group management
  - Error handling and DLQ
  - Performance metrics

### 7. Testing Framework (`test-event-flow.py`)
- **Purpose**: Comprehensive Kafka testing utilities
- **Tests**:
  - Infrastructure validation
  - Functional testing
  - Performance benchmarking
  - End-to-end flow validation
  - Message format validation

## Deployment

### Prerequisites
- DOKS cluster with kubectl access
- DigitalOcean API token
- kubectl configured for cluster access

### 1. Install Strimzi Operator
```bash
kubectl apply -f kafka/strimzi-operator.yaml
```

### 2. Deploy Kafka Cluster
```bash
kubectl apply -f kafka/kafka-cluster.yaml
```

### 3. Create Topics and Users
```bash
kubectl apply -f kafka/topics.yaml
```

### 4. Deploy Kafka UI
```bash
kubectl apply -f kafka/kafka-ui.yaml
```

### 5. Verify Installation
```bash
# Check operator status
kubectl get pods -n kafka

# Check cluster status
kubectl get kafka -n kafka

# Check topics
kubectl get kafkatopics -n kafka
```

## Configuration

### Environment Variables
```bash
export KAFKA_BOOTSTRAP_SERVERS="todo-chatbot-kafka-kafka-bootstrap:9093"
export SCHEMA_REGISTRY_URL="http://todo-chatbot-schema-registry:8081"
export KAFKA_CLIENT_CERT="/path/to/client.crt"
export KAFKA_CLIENT_KEY="/path/to/client.key"
```

### Application Integration
```python
from kafka.event_producers import create_producers

# Create producers
producers = create_producers(
    bootstrap_servers="todo-chatbot-kafka-kafka-bootstrap:9093",
    schema_registry_url="http://todo-chatbot-schema-registry:8081"
)

# Use todo producer
todo_producer = producers['todo']
todo_producer.produce_task_created(task_data, user_id)
```

## Monitoring

### Metrics Collection
- **JMX Exporter**: Exposes Kafka metrics to Prometheus
- **Kafka UI**: Web-based monitoring dashboard
- **Prometheus**: Metrics storage and alerting
- **Grafana**: Visualization dashboards

### Key Metrics to Monitor
- **Broker Metrics**: CPU, memory, disk usage
- **Topic Metrics**: Message rates, partition counts
- **Consumer Metrics**: Lag, throughput
- **System Metrics**: Error rates, latency

### Alerts
```yaml
# Example Prometheus alerts
groups:
  - name: kafka-alerts
    rules:
      - alert: KafkaBrokerDown
        expr: up{job="kafka"} == 0
        for: 5m
        labels:
          severity: critical
      - alert: HighConsumerLag
        expr: kafka_consumer_lag > 1000
        for: 2m
        labels:
          severity: warning
```

## Security

### Authentication
- TLS certificates for encryption
- mTLS for client authentication
- ACLs for topic-level permissions

### Authorization
- Role-based access control
- Topic-specific permissions
- Consumer group restrictions

### Network Security
- Network policies for pod isolation
- Private VPC for cluster communication
- Ingress TLS termination

## Performance Tuning

### Broker Configuration
```yaml
# Optimize for high throughput
num.network.threads: 8
num.io.threads: 8
socket.send.buffer.bytes: 102400
socket.receive.buffer.bytes: 102400
```

### Producer Configuration
```yaml
# Optimize for low latency
acks: 1
linger.ms: 5
batch.size: 16384
compression.type: gzip
```

### Consumer Configuration
```yaml
# Optimize for throughput
fetch.min.bytes: 1024
max.partition.fetch.bytes: 10485760
enable.auto.commit: true
auto.commit.interval.ms: 5000
```

## Troubleshooting

### Common Issues

1. **Topics not created**
   ```bash
   kubectl describe kafkatopic todo-events -n kafka
   ```

2. **Producers failing**
   ```bash
   kubectl logs -f deployment/todo-chatbot-producer -n kafka
   ```

3. **Consumers lagging**
   ```bash
   kubectl exec -it kafka-cluster-entity-operator-xxx -n kafka -- \
   ./bin/kafka-consumer-groups.sh --bootstrap-server localhost:9093 \
   --describe --group analytics-consumer
   ```

4. **SSL/TLS issues**
   ```bash
   kubectl get secrets -n kafka
   kubectl describe secret todo-chatbot-kafka-clients-ca-cert -n kafka
   ```

### Debug Commands
```bash
# Check cluster health
kubectl get kafka -n kafka -o wide

# Check topic details
kubectl get kafkatopics -n kafka -o yaml

# Check user permissions
kubectl get kafkausers -n kafka

# Port forward for local access
kubectl port-forward -n kafka svc/kafka-ui 8080:8080
```

## Cost Optimization

### Resource Usage
- **Brokers**: 3 nodes × 1GB RAM × 500m CPU
- **Storage**: 10GB × 3 nodes = 30GB total
- **Network**: Internal traffic only for best performance

### Cost Reduction Strategies
- Adjust broker count based on load
- Use smaller instance types for development
- Implement topic retention policies
- Monitor and clean up unused topics

## Next Steps

After Kafka deployment:

1. **Integrate with Backend**: Update backend to use event producers
2. **Setup Analytics**: Deploy analytics consumers and dashboards
3. **Configure Monitoring**: Set up Prometheus and Grafana
4. **Load Testing**: Performance test with realistic workloads
5. **Security Hardening**: Implement production security measures

## Related Documentation

- [Phase V Specification](../specs/005-cloud-deployment/spec.md)
- [Phase V Architecture Plan](../specs/005-cloud-deployment/plan.md)
- [Strimzi Documentation](https://strimzi.io/docs/)
- [Kafka Documentation](https://kafka.apache.org/documentation/)

## Support

For issues with Kafka configuration:

1. Check the [Strimzi troubleshooting guide](https://strimzi.io/docs/operators/latest/full/using.html#troubleshooting)
2. Review cluster events: `kubectl get events -n kafka`
3. Check operator logs: `kubectl logs -f deployment/strimzi-cluster-operator -n kafka`
4. Verify topic creation: `kubectl get kafkatopics -n kafka`