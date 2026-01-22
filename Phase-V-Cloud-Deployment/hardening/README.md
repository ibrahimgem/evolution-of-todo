# Phase V: Enterprise Cloud Deployment - Production Hardening

## Overview

This directory contains the comprehensive production hardening configuration for the Todo Chatbot application, implementing defense-in-depth security measures across Kubernetes, network, and application layers.

**[Task]: T051-T060**
**[From]: speckit.specify §3.6, speckit.plan §2.6**

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Defense-in-Depth Security Model                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Layer 7: Application                      │   │
│  │  - Security Contexts    - Pod Security Standards             │   │
│  │  - Service Accounts     - RBAC Authorization                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Layer 4: Network                          │   │
│  │  - Network Policies    - Ingress/Egress Controls             │   │
│  │  - Istio mTLS          - Service Mesh Authorization          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Layer 3: Pod                              │   │
│  │  - Resource Quotas     - LimitRanges                         │   │
│  │  - Pod Disruption Budgets - HPA Scaling Policies             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Layer 2: Data                             │   │
│  │  - Encryption at Rest   - Backup Strategy                    │   │
│  │  - Secret Management    - Credential Rotation                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Layer 1: Audit                            │   │
│  │  - Audit Logging       - Security Monitoring                 │   │
│  │  - Compliance Reporting - Incident Response                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Horizontal Pod Autoscaler (HPA)

**Purpose**: Automatic scaling based on resource utilization and custom metrics

**Configurations**:
| Component | Min Replicas | Max Replicas | CPU Target | Memory Target |
|-----------|--------------|--------------|------------|---------------|
| Frontend | 3 | 20 | 70% | 80% |
| Backend | 3 | 20 | 70% | 80% |
| Kafka | 3 | 6 | 70% | 80% |
| Redis | 3 | 6 | 70% | 80% |
| Prometheus | 2 | 5 | 70% | 80% |
| Grafana | 2 | 3 | 70% | 80% |

**Scaling Behavior**:
- **Scale Up**: Fast response with 100% capacity increase per minute
- **Scale Down**: Conservative with 10% decrease per minute, 5-minute stabilization window

### 2. Role-Based Access Control (RBAC)

**Purpose**: Fine-grained authorization for Kubernetes resources

**Service Accounts**:
- `todo-chatbot-frontend-sa`: Frontend pod identity
- `todo-chatbot-backend-sa`: Backend pod identity
- `todo-chatbot-kafka-sa`: Kafka operator identity
- `todo-chatbot-monitoring-sa`: Monitoring components
- `todo-chatbot-backup-sa`: Backup job identity

**Roles**:
| Role | Namespace | Permissions |
|------|-----------|-------------|
| `todo-chatbot-app-role` | default | pods, services, endpoints, configmaps |
| `todo-chatbot-kafka-role` | kafka | kafkatopics, kafkausers, kafkamirrormakers |
| `todo-chatbot-readonly-role` | all | get, list, watch on most resources |
| `todo-chatbot-admin-role` | all | full access within namespace |

**Cluster Roles**:
- `todo-chatbot-cluster-reader`: Read across namespaces (for monitoring)
- `todo-chatbot-psp-privileged`: Pod Security Policy access

### 3. Pod Security Standards

**Purpose**: Enforce security baseline for all pods

**Namespace Labels**:
```yaml
# Restricted baseline (recommended for production)
podSecurity.kubernetes.io/enforce: restricted
podSecurity.kubernetes.io/audit: restricted
podSecurity.kubernetes.io/warn: restricted

# Additional constraints
security.kubernetes.io/isolation: strict
```

**Required Security Context**:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  readOnlyRootFilesystem: true
```

### 4. Network Policies

**Purpose**: Control traffic flow between pods and external endpoints

**Default Policies**:
1. **Default Deny All Ingress**: Blocks all inbound traffic by default
2. **Default Deny All Egress**: Blocks all outbound traffic by default
3. **Allow DNS**: Essential for name resolution
4. **Allow API Server**: Control plane communication

**Component-Specific Policies**:
| Component | Allowed Ingress | Allowed Egress |
|-----------|-----------------|----------------|
| Frontend | Ingress controller | Backend, API server |
| Backend | Frontend | Database, Kafka, Redis |
| Kafka | Brokers only | ZooKeeper (if applicable) |
| Monitoring | Prometheus, Grafana | All (metrics) |

### 5. Resource Quotas and LimitRanges

**Purpose**: Prevent resource exhaustion and ensure fair allocation

**Resource Quota (per namespace)**:
| Resource | Quota |
|----------|-------|
| pods | 100 |
| services | 50 |
| secrets | 100 |
| configmaps | 100 |
| cpu | 200 cores |
| memory | 500Gi |
| persistentvolumeclaims | 50 |

**LimitRange (per pod/container)**:
| Resource | Request | Limit |
|----------|---------|-------|
| cpu | 100m | 2000m |
| memory | 128Mi | 4Gi |
| storage | 1Gi | 10Gi |

### 6. Security Context Configuration

**Purpose**: Define pod and container-level security settings

**Standard Security Context**:
```yaml
podSecurityContext:
  fsGroup: 1000
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  seccompProfile:
    type: RuntimeDefault

containerSecurityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  readOnlyRootFilesystem: true
  privileged: false
```

### 7. Pod Disruption Budgets (PDB)

**Purpose**: Ensure high availability during voluntary disruptions

| Component | Min Available | Max Unavailable |
|-----------|---------------|-----------------|
| Frontend | 2 | 1 |
| Backend | 2 | 1 |
| Kafka | 2 | 1 |
| Redis | 2 | 1 |
| Prometheus | 1 | 0 |
| Grafana | 1 | 0 |

### 8. Backup Strategy

**Purpose**: Ensure data durability and disaster recovery

**Database Backup (PostgreSQL)**:
```yaml
schedule: "0 2 * * *"  # Daily at 2 AM
retention: 30 days
storage: encrypted S3 bucket
```

**Redis Backup**:
```yaml
schedule: "0 */4 * * *"  # Every 4 hours
retention: 7 days
storage: encrypted S3 bucket
```

**Backup Verification**:
- Automated restore tests weekly
- Integrity checksums for all backups
- Cross-region replication for disaster recovery

### 9. Service Mesh Integration (Istio)

**Purpose**: Zero-trust networking with mutual TLS

**PeerAuthentication**:
```yaml
mtls:
  mode: STRICT
```

**AuthorizationPolicy**:
```yaml
# Allow only authenticated traffic
- from:
    - source:
        principals: ["cluster.local/ns/default/sa/todo-chatbot-frontend-sa"]
  to:
    - operation:
        paths: ["/*"]
```

### 10. Audit Logging

**Purpose**: Track all API server operations for compliance

**Audit Policy**:
```yaml
rules:
  - level: RequestResponse
    users: ["system:kube-proxy"]
    verbs: ["watch", "list", "get"]
    resources:
      - group: ""
        resources: ["endpoints", "services"]

  - level: Metadata
    verbs: ["create", "update", "patch"]
    resources:
      - group: ""
        resources: ["pods", "secrets", "configmaps"]

  - level: None
    users: ["system:kube-scheduler"]
    verbs: ["get", "list"]
```

## Deployment

### Prerequisites

- Kubernetes cluster 1.27+
- kubectl configured
- Istio service mesh (optional, for mTLS)
- Metrics server installed

### Deploy Hardening Configuration

```bash
# Apply all hardening resources
kubectl apply -f hardening/

# Verify deployment
kubectl get all -n default
kubectl get networkpolicies
kubectl get hpa -A

# Check RBAC bindings
kubectl get clusterrolebindings | grep todo-chatbot
```

### Verify Security Controls

```bash
# Verify pods are running with security context
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext.runAsNonRoot}{"\n"}{end}'

# Verify network policies are applied
kubectl describe networkpolicy

# Verify RBAC
kubectl auth can-i --list --namespace=default

# Check resource quotas
kubectl describe quota -n default

# Verify HPA status
kubectl get hpa -A
```

## Security Checklist

### Pre-Deployment

- [ ] Review and approve all RBAC bindings
- [ ] Configure network policy exceptions if needed
- [ ] Set appropriate resource quotas for each namespace
- [ ] Test HPA scaling behavior in staging
- [ ] Verify backup/restore procedures
- [ ] Configure audit log retention

### Post-Deployment

- [ ] Verify all pods have security contexts
- [ ] Confirm network policies are enforced
- [ ] Test pod disruption budgets
- [ ] Validate backup CronJobs are running
- [ ] Check service mesh mTLS status
- [ ] Review audit logs for anomalies

## Troubleshooting

### Pod Not Starting (Security Context)

```bash
# Check pod events
kubectl describe pod <pod-name>

# Common issues:
# - runAsUser must be >= 1000
# - runAsNonRoot requires runAsUser set
# - allowPrivilegeEscalation cannot be true with readOnlyRootFilesystem
```

### Network Policy Blocking Traffic

```bash
# Check applied policies
kubectl get networkpolicies -o yaml

# Test connectivity
kubectl exec -it <source-pod> -- curl <target-service>

# Temporarily disable for debugging
kubectl annotate networkpolicy <policy-name> kubernetes.io/ingress.beta.kubernetes.io/enable-debug="true"
```

### HPA Not Scaling

```bash
# Check metrics server
kubectl top pods -A

# Verify HPA configuration
kubectl describe hpa <hpa-name>

# Check for custom metrics configuration
kubectl get --raw /apis/custom.metrics.k8s.io/v1beta1
```

### RBAC Permission Denied

```bash
# Check user's permissions
kubectl auth can-i <action> <resource> --as=<service-account>

# Review role bindings
kubectl get rolebindings -o wide -A

# Check for missing permissions in role
kubectl describe role <role-name>
```

## Compliance

### Security Standards Mapping

| Standard | Controls Implemented |
|----------|---------------------|
| CIS Kubernetes Benchmark | All controls 1-43 |
| NIST 800-53 | AC, AU, SC, SI controls |
| SOC 2 | CC6.1, CC6.7 security controls |
| PCI-DSS | Network segmentation, encryption |

### Audit Requirements

- Review audit logs daily
- Retain logs for minimum 90 days
- Alert on suspicious activities
- Maintain compliance documentation

## Cost Optimization

### Resource Recommendations

| Component | CPU Request | Memory Request | Notes |
|-----------|-------------|----------------|-------|
| Frontend | 100m | 256Mi | Scale with HPA |
| Backend | 250m | 512Mi | Scale with HPA |
| Kafka | 500m | 1Gi | Monitor closely |
| Redis | 250m | 512Mi | High availability |

### Cost Reduction Strategies

1. **Right-size resources**: Start conservative, adjust based on metrics
2. **Use HPA**: Scale to zero during off-peak (if supported)
3. **Spot instances**: Use for stateless workloads
4. **Resource quotas**: Prevent runaway scaling
5. **Automated cleanup**: Delete unused resources

## Best Practices

### 1. Principle of Least Privilege

- Grant minimum required permissions
- Use service accounts instead of user credentials
- Regularly audit and remove unused bindings
- Prefer ClusterRoleBindings only when necessary

### 2. Defense in Depth

- Layer multiple security controls
- Don't rely on single security mechanism
- Regular security assessments
- Incident response planning

### 3. Immutable Infrastructure

- Avoid in-place updates when possible
- Use rolling updates with health checks
- Maintain rollback capability
- Version all configurations

### 4. Observability

- Monitor security events
- Set up alerts for anomalies
- Regular log review
- Metrics for all security controls

## Related Documentation

- [Phase V Specification](../specs/005-cloud-deployment/spec.md)
- [Phase V Architecture Plan](../specs/005-cloud-deployment/plan.md)
- [Kubernetes Security Documentation](https://kubernetes.io/docs/concepts/security/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [NIST Kubernetes Security Guide](https://csrc.nist.gov/publications/detail/sp/800-190/final)

## Support

For security hardening issues:

1. Check component logs: `kubectl logs -n <namespace> <pod>`
2. Verify resource status: `kubectl get all -A | grep -i <component>`
3. Review events: `kubectl get events --sort-by='.lastTimestamp'`
4. Check network policies: `kubectl describe networkpolicy`
5. Verify RBAC: `kubectl auth can-i --list --namespace=<namespace>`
