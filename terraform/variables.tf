// Terraform variables for Visual DM infrastructure

// --- VPC ---
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

// --- EKS ---
variable "eks_cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "eks_node_instance_type" {
  description = "EC2 instance type for EKS worker nodes"
  type        = string
}

variable "eks_node_count" {
  description = "Number of EKS worker nodes"
  type        = number
}

// --- RDS ---
variable "rds_instance_class" {
  description = "Instance class for RDS Postgres"
  type        = string
}

variable "rds_db_name" {
  description = "Database name for RDS Postgres"
  type        = string
}

// --- Redis ---
variable "redis_node_type" {
  description = "Node type for ElastiCache Redis"
  type        = string
}

// --- S3 Buckets ---
variable "s3_backup_bucket" {
  description = "Name of the S3 bucket for backups"
  type        = string
}

variable "s3_media_bucket" {
  description = "Name of the S3 bucket for media files"
  type        = string
}

// --- IAM ---
variable "iam_role_name" {
  description = "Name for IAM role used by EKS nodes"
  type        = string
} 