# Phase V: Enterprise Cloud Deployment
# Terraform Variables Configuration
#
# [Task]: T007
# [From]: speckit.specify §3.1, speckit.plan §2.1

# DigitalOcean Provider Configuration
variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
  sensitive   = true
}

# Cluster Configuration
variable "cluster_name" {
  description = "Name of the DOKS cluster"
  type        = string
  default     = "todo-chatbot-prod"
}

variable "cluster_region" {
  description = "Region for the DOKS cluster"
  type        = string
  default     = "nyc1"
}

variable "kubernetes_version" {
  description = "Kubernetes version for the cluster"
  type        = string
  default     = "1.28.x"
}

variable "node_size" {
  description = "Droplet size for worker nodes"
  type        = string
  default     = "s-2vcpu-4gb"
}

variable "auto_scale_enabled" {
  description = "Enable auto-scaling for the node pool"
  type        = bool
  default     = true
}

variable "min_nodes" {
  description = "Minimum number of nodes in the node pool"
  type        = number
  default     = 3
}

variable "max_nodes" {
  description = "Maximum number of nodes in the node pool"
  type        = number
  default     = 10
}

variable "vpc_uuid" {
  description = "VPC UUID for the cluster (optional - will create new if not provided)"
  type        = string
  default     = null
}

# Container Registry Configuration
variable "registry_name" {
  description = "Name of the container registry"
  type        = string
  default     = "todo-chatbot-registry"
}

variable "registry_tier" {
  description = "Subscription tier for the container registry"
  type        = string
  default     = "basic"
}

variable "registry_credentials_expiry" {
  description = "Expiry time for registry credentials in seconds"
  type        = number
  default     = 86400
}

# Database Configuration
variable "database_name" {
  description = "Name of the PostgreSQL database cluster"
  type        = string
  default     = "todo-chatbot-db"
}

variable "database_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15"
}

variable "database_size" {
  description = "Database droplet size"
  type        = string
  default     = "db-s-dev-database-general-1vcpu-1gb"
}

variable "database_node_count" {
  description = "Number of database nodes"
  type        = number
  default     = 1
}

variable "database_pool_size" {
  description = "Connection pool size"
  type        = number
  default     = 20
}

# Storage Configuration
variable "spaces_bucket_name" {
  description = "Name of the Spaces bucket"
  type        = string
  default     = "todo-chatbot-assets"
}

variable "spaces_region" {
  description = "Region for Spaces bucket"
  type        = string
  default     = "nyc3"
}

# Load Balancer Configuration
variable "create_load_balancer" {
  description = "Create a DigitalOcean Load Balancer"
  type        = bool
  default     = false
}

variable "ssl_certificate_id" {
  description = "SSL certificate ID for load balancer"
  type        = string
  default     = null
}

# Domain Configuration
variable "create_domain" {
  description = "Create DNS domain records"
  type        = bool
  default     = false
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

# VPC Configuration
variable "create_vpc" {
  description = "Create a new VPC"
  type        = bool
  default     = false
}

# Environment Configuration
variable "environment" {
  description = "Environment name (production, staging, etc.)"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name for tagging and identification"
  type        = string
  default     = "todo-chatbot"
}

# Security Configuration
variable "enable_private_network" {
  description = "Enable private network for enhanced security"
  type        = bool
  default     = true
}

variable "enable_monitoring" {
  description = "Enable DigitalOcean monitoring"
  type        = bool
  default     = true
}

# Cost Management
variable "cost_center" {
  description = "Cost center tag for billing"
  type        = string
  default     = "engineering"
}

variable "budget_alert_threshold" {
  description = "Budget alert threshold in USD"
  type        = number
  default     = 100
}