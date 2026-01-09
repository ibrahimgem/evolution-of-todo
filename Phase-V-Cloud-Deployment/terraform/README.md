# Phase V: Enterprise Cloud Deployment - Terraform

## Overview

This directory contains the Terraform configuration for deploying the Todo Chatbot application to DigitalOcean Kubernetes Service (DOKS) with enterprise-grade infrastructure.

**[Task]: T001-T010**
**[From]: speckit.specify §3.1, speckit.plan §2.1**

## Architecture

The Terraform configuration creates the following infrastructure:

- **DOKS Cluster**: Managed Kubernetes cluster with auto-scaling
- **Container Registry**: DigitalOcean Container Registry for Docker images
- **Database**: Managed PostgreSQL database with connection pooling
- **Storage**: DigitalOcean Spaces for object storage
- **Networking**: Private VPC for secure communication
- **Load Balancer**: Optional external load balancer
- **DNS**: Optional domain management

## Prerequisites

- Terraform >= 1.0
- DigitalOcean account with API token
- `doctl` CLI (optional, for easier management)

## Quick Start

### 1. Set Environment Variables

```bash
export TF_VAR_do_token="your-digitalocean-api-token"
export TF_VAR_cluster_name="todo-chatbot-prod"
export TF_VAR_environment="production"
```

### 2. Initialize Terraform

```bash
cd terraform/
terraform init
```

### 3. Review Configuration

```bash
terraform plan
```

### 4. Apply Configuration

```bash
terraform apply
```

### 5. Access Cluster

After deployment, configure kubectl:

```bash
# Get kubeconfig
terraform output -raw cluster_kubeconfig > kubeconfig.yaml
export KUBECONFIG=./kubeconfig.yaml

# Verify cluster access
kubectl cluster-info
kubectl get nodes
```

## Configuration

### Required Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `do_token` | DigitalOcean API token | - |
| `cluster_name` | DOKS cluster name | "todo-chatbot-prod" |
| `cluster_region` | Cluster region | "nyc1" |
| `node_size` | Worker node size | "s-2vcpu-4gb" |
| `min_nodes` | Min auto-scale nodes | 3 |
| `max_nodes` | Max auto-scale nodes | 10 |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `environment` | Environment name | "production" |
| `kubernetes_version` | K8s version | "1.28.x" |
| `create_vpc` | Create new VPC | false |
| `create_load_balancer` | Create load balancer | false |
| `create_domain` | Create DNS domain | false |

## Outputs

Important outputs from the deployment:

- `cluster_endpoint`: Kubernetes API endpoint
- `cluster_kubeconfig`: Kubeconfig for cluster access
- `registry_server_url`: Container registry URL
- `database_connection_string`: Database connection string
- `spaces_bucket_endpoint`: Object storage endpoint

## Security

- All credentials are marked as sensitive in Terraform
- Private networking enabled for enhanced security
- Database connections require SSL
- Container registry uses Docker authentication

## Cost Management

Estimated monthly costs:
- DOKS Cluster: ~$72-240/month (3-10 nodes)
- Container Registry: ~$5/month
- Database: ~$15-50/month
- Load Balancer: ~$12/month
- **Total**: ~$109-317/month

## Troubleshooting

### Common Issues

1. **API Token Permissions**: Ensure your DO token has read/write permissions
2. **Resource Limits**: Check your DigitalOcean account limits for VPCs, LBs, etc.
3. **Region Availability**: Some resources may not be available in all regions

### Debug Commands

```bash
# Check resource status
terraform show

# Check specific outputs
terraform output cluster_status
terraform output database_connection_string

# Refresh state
terraform refresh
```

## Next Steps

After infrastructure deployment:

1. **Configure kubectl**: Use the generated kubeconfig
2. **Deploy Applications**: Use Helm charts in `/helm/` directory
3. **Set up Monitoring**: Deploy monitoring stack from `/monitoring/`
4. **Configure CI/CD**: Set up GitHub Actions from `/ci-cd/`

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

⚠️ **Warning**: This will permanently delete all infrastructure and data.

## Security Notes

- Store `do_token` securely (never commit to version control)
- Use Terraform workspaces for different environments
- Enable DigitalOcean monitoring and alerts
- Review and update security groups regularly

## Support

For issues with this Terraform configuration:

1. Check the [DigitalOcean Terraform Provider documentation](https://registry.terraform.io/providers/digitalocean/digitalocean/latest/docs)
2. Review the [DOKS documentation](https://docs.digitalocean.com/products/kubernetes/)
3. Check the project [Issues](https://github.com/your-repo/issues) section

## Related Documentation

- [Phase V Specification](../specs/005-cloud-deployment/spec.md)
- [Phase V Architecture Plan](../specs/005-cloud-deployment/plan.md)
- [Kubernetes Deployment Guide](../docs/DEPLOYMENT.md)
- [Monitoring Setup](../docs/MONITORING.md)