# Phase V: Enterprise Cloud Deployment
# Terraform Outputs Configuration
#
# [Task]: T008
# [From]: speckit.specify §3.1, speckit.plan §2.1

# DOKS Cluster Outputs
output "cluster_id" {
  description = "ID of the DOKS cluster"
  value       = digitalocean_kubernetes_cluster.todo_chatbot.id
}

output "cluster_name" {
  description = "Name of the DOKS cluster"
  value       = digitalocean_kubernetes_cluster.todo_chatbot.name
}

output "cluster_endpoint" {
  description = "Endpoint URL of the DOKS cluster"
  value       = digitalocean_kubernetes_cluster.todo_chatbot.endpoint
}

output "cluster_kubeconfig" {
  description = "Kubeconfig for the DOKS cluster (sensitive)"
  value       = digitalocean_kubernetes_cluster.todo_chatbot.kube_config[0].raw_config
  sensitive   = true
}

output "cluster_status" {
  description = "Status of the DOKS cluster"
  value       = digitalocean_kubernetes_cluster.todo_chatbot.status
}

# Container Registry Outputs
output "registry_name" {
  description = "Name of the container registry"
  value       = digitalocean_container_registry.todo_chatbot.name
}

output "registry_server_url" {
  description = "Server URL for the container registry"
  value       = digitalocean_container_registry.todo_chatbot.server_url
}

output "registry_docker_credentials" {
  description = "Docker credentials for the registry (sensitive)"
  value       = digitalocean_container_registry_docker_credentials.todo_chatbot.docker_credentials
  sensitive   = true
}

# Database Outputs
output "database_cluster_id" {
  description = "ID of the database cluster"
  value       = digitalocean_database_cluster.todo_chatbot.id
}

output "database_connection_string" {
  description = "Connection string for the database (sensitive)"
  value       = digitalocean_database_cluster.todo_chatbot.uri
  sensitive   = true
}

output "database_private_connection_string" {
  description = "Private connection string for the database (sensitive)"
  value       = digitalocean_database_cluster.todo_chatbot.private_uri
  sensitive   = true
}

output "database_host" {
  description = "Database host address"
  value       = digitalocean_database_cluster.todo_chatbot.host
}

output "database_port" {
  description = "Database port"
  value       = digitalocean_database_cluster.todo_chatbot.port
}

output "database_name" {
  description = "Database name"
  value       = digitalocean_database_cluster.todo_chatbot.database
}

output "database_user" {
  description = "Database username"
  value       = digitalocean_database_cluster.todo_chatbot.user
}

output "database_password" {
  description = "Database password (sensitive)"
  value       = digitalocean_database_cluster.todo_chatbot.password
  sensitive   = true
}

output "database_pool_connection_string" {
  description = "Connection string for the database pool (sensitive)"
  value       = digitalocean_database_pool.todo_chatbot.connection_string
  sensitive   = true
}

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC (if created)"
  value       = var.create_vpc ? digitalocean_vpc.todo_chatbot[0].id : null
}

output "vpc_name" {
  description = "Name of the VPC (if created)"
  value       = var.create_vpc ? digitalocean_vpc.todo_chatbot[0].name : null
}

output "vpc_default" {
  description = "Whether VPC is default"
  value       = var.create_vpc ? digitalocean_vpc.todo_chatbot[0].default : null
}

# Load Balancer Outputs
output "loadbalancer_id" {
  description = "ID of the load balancer (if created)"
  value       = var.create_load_balancer ? digitalocean_loadbalancer.todo_chatbot[0].id : null
}

output "loadbalancer_ip" {
  description = "IP address of the load balancer (if created)"
  value       = var.create_load_balancer ? digitalocean_loadbalancer.todo_chatbot[0].ip : null
}

output "loadbalancer_status" {
  description = "Status of the load balancer (if created)"
  value       = var.create_load_balancer ? digitalocean_loadbalancer.todo_chatbot[0].status : null
}

# Spaces Outputs
output "spaces_bucket_name" {
  description = "Name of the Spaces bucket"
  value       = digitalocean_spaces_bucket.todo_chatbot.name
}

output "spaces_bucket_region" {
  description = "Region of the Spaces bucket"
  value       = digitalocean_spaces_bucket.todo_chatbot.region
}

output "spaces_bucket_endpoint" {
  description = "Endpoint URL for the Spaces bucket"
  value       = digitalocean_spaces_bucket.todo_chatbot.bucket_domain_name
}

# Domain Outputs
output "domain_name" {
  description = "Domain name (if created)"
  value       = var.create_domain ? digitalocean_domain.todo_chatbot[0].name : null
}

output "domain_ip_address" {
  description = "IP address for the domain (if created)"
  value       = var.create_domain ? digitalocean_domain.todo_chatbot[0].ip_address : null
}

# Cost and Management Outputs
output "estimated_monthly_cost" {
  description = "Estimated monthly cost (approximate)"
  value = "DOKS Cluster: ~$${var.min_nodes * 24} - $${var.max_nodes * 24}/month\n" <<
           "Container Registry: ~$5/month\n" <<
           "Database: ~$15-50/month\n" <<
           "Load Balancer: ~$12/month\n" <<
           "Total: ~$${var.min_nodes * 24 + 32} - $${var.max_nodes * 24 + 67}/month"
}

output "environment_info" {
  description = "Environment configuration summary"
  value = {
    environment   = var.environment
    region        = var.cluster_region
    node_size     = var.node_size
    min_nodes     = var.min_nodes
    max_nodes     = var.max_nodes
    auto_scaling  = var.auto_scale_enabled
    project_name  = var.project_name
    cost_center   = var.cost_center
  }
}

# Connection Information Summary
output "connection_summary" {
  description = "Summary of all connection information needed for deployment"
  value = {
    kubernetes = {
      cluster_name = digitalocean_kubernetes_cluster.todo_chatbot.name
      endpoint     = digitalocean_kubernetes_cluster.todo_chatbot.endpoint
      status       = digitalocean_kubernetes_cluster.todo_chatbot.status
    }
    registry = {
      name        = digitalocean_container_registry.todo_chatbot.name
      server_url  = digitalocean_container_registry.todo_chatbot.server_url
      credentials = "Use registry_docker_credentials output for authentication"
    }
    database = {
      host     = digitalocean_database_cluster.todo_chatbot.host
      port     = digitalocean_database_cluster.todo_chatbot.port
      name     = digitalocean_database_cluster.todo_chatbot.database
      user     = digitalocean_database_cluster.todo_chatbot.user
      ssl_mode = "require"
    }
    spaces = {
      bucket_name = digitalocean_spaces_bucket.todo_chatbot.name
      endpoint    = digitalocean_spaces_bucket.todo_chatbot.bucket_domain_name
      region      = digitalocean_spaces_bucket.todo_chatbot.region
    }
  }
}