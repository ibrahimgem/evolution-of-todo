# Phase V: Enterprise Cloud Deployment
# Terraform Configuration for DigitalOcean Kubernetes Service (DOKS)
#
# [Task]: T001-T010
# [From]: speckit.specify §3.1, speckit.plan §2.1

# Configure DigitalOcean Provider
terraform {
  required_version = ">= 1.0"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

# Create DOKS Cluster
resource "digitalocean_kubernetes_cluster" "todo_chatbot" {
  name    = var.cluster_name
  region  = var.cluster_region
  version = var.kubernetes_version

  # Network Configuration
  vpc_uuid = var.vpc_uuid

  # Node Pool Configuration
  node_pool {
    name       = "worker-pool"
    size       = var.node_size
    auto_scale = var.auto_scale_enabled
    min_nodes  = var.min_nodes
    max_nodes  = var.max_nodes

    # Labels for node identification
    labels = {
      "app.kubernetes.io/component" = "worker"
      "app.kubernetes.io/part-of"   = "todo-chatbot"
    }

    # Taints for specialized workloads (optional)
    # taint {
    #   key    = "dedicated"
    #   value  = "monitoring"
    #   effect = "NO_SCHEDULE"
    # }
  }

  # Add tags for resource management
  tags = [
    "todo-chatbot",
    "production",
    "doks"
  ]
}

# Create Container Registry
resource "digitalocean_container_registry" "todo_chatbot" {
  name                   = var.registry_name
  subscription_tier_slug = var.registry_tier

  # Add tags
  tags = [
    "todo-chatbot",
    "container-registry"
  ]
}

# Create Container Registry Docker Credentials
resource "digitalocean_container_registry_docker_credentials" "todo_chatbot" {
  registry_name = digitalocean_container_registry.todo_chatbot.name
  write         = true
  read          = true
  expiry_seconds = var.registry_credentials_expiry
}

# Create Managed Database (PostgreSQL)
resource "digitalocean_database_cluster" "todo_chatbot" {
  name       = var.database_name
  engine     = "pg"
  version    = var.database_version
  region     = var.cluster_region
  size       = var.database_size
  node_count = var.database_node_count

  # Maintenance window (UTC time)
  maintenance_window {
    day  = "sunday"
    hour = "01:00"
  }

  # Add tags
  tags = [
    "todo-chatbot",
    "database",
    "postgresql"
  ]
}

# Create Database Connection Pool
resource "digitalocean_database_pool" "todo_chatbot" {
  name               = "${var.database_name}-pool"
  cluster_id         = digitalocean_database_cluster.todo_chatbot.id
  db_name            = var.database_name
  mode               = "transaction"
  size               = var.database_pool_size
  user               = digitalocean_database_cluster.todo_chatbot.default_user
}

# Create Private VPC (if not using existing)
resource "digitalocean_vpc" "todo_chatbot" {
  count = var.create_vpc ? 1 : 0

  name   = "${var.cluster_name}-vpc"
  region = var.cluster_region

  # Add tags
  tags = [
    "todo-chatbot",
    "vpc"
  ]
}

# Create Load Balancer (Optional - for external access if needed)
resource "digitalocean_loadbalancer" "todo_chatbot" {
  count = var.create_load_balancer ? 1 : 0

  name   = "${var.cluster_name}-lb"
  region = var.cluster_region
  type   = "lb"

  forwarding_rule {
    entry_protocol  = "https"
    entry_port      = 443
    target_protocol = "http"
    target_port     = 80
    certificate_id  = var.ssl_certificate_id
  }

  healthcheck {
    protocol = "http"
    port     = 80
    path     = "/healthz"
  }

  droplet_tag = "todo-chatbot"

  # Add tags
  tags = [
    "todo-chatbot",
    "load-balancer"
  ]
}

# Create Spaces (Object Storage)
resource "digitalocean_spaces_bucket" "todo_chatbot" {
  name   = var.spaces_bucket_name
  region = var.spaces_region

  # Lifecycle rules for cost optimization
  lifecycle_rule {
    id      = "log-retention"
    enabled = true

    # Delete logs older than 30 days
    expiration {
      days = 30
    }
  }

  # Add tags
  tags = [
    "todo-chatbot",
    "spaces"
  ]
}

# Create DNS Records (if using custom domain)
resource "digitalocean_domain" "todo_chatbot" {
  count = var.create_domain ? 1 : 0

  name       = var.domain_name
  ip_address = digitalocean_kubernetes_cluster.todo_chatbot.endpoint
}

resource "digitalocean_record" "www" {
  count = var.create_domain ? 1 : 0

  domain = digitalocean_domain.todo_chatbot[0].name
  type   = "CNAME"
  name   = "www"
  value  = digitalocean_kubernetes_cluster.todo_chatbot.endpoint
  ttl    = 300
}