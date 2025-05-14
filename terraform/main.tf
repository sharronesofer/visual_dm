// Terraform main configuration for Visual DM infrastructure

// --- VPC ---
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 4.0"
  // ...variables
}

// --- EKS Cluster ---
module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "~> 19.0"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
  // ...variables
}

// --- RDS (Postgres) ---
module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"
  // ...variables
}

// --- ElastiCache (Redis) ---
module "redis" {
  source  = "terraform-aws-modules/elasticache/aws"
  version = "~> 4.0"
  // ...variables
}

// --- S3 Buckets (Backups, Media) ---
resource "aws_s3_bucket" "backups" {
  bucket = var.s3_backup_bucket
  // ...lifecycle, versioning, encryption
}

resource "aws_s3_bucket" "media" {
  bucket = var.s3_media_bucket
  // ...lifecycle, versioning, encryption
}

// --- IAM Roles and Policies ---
module "iam" {
  source  = "terraform-aws-modules/iam/aws"
  version = "~> 5.0"
  // ...variables
}

// --- Outputs ---
output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "rds_endpoint" {
  value = module.rds.db_instance_endpoint
}

output "redis_endpoint" {
  value = module.redis.primary_endpoint_address
}

output "s3_backup_bucket" {
  value = aws_s3_bucket.backups.bucket
}

output "s3_media_bucket" {
  value = aws_s3_bucket.media.bucket
}

// See variables.tf for input variables and outputs.tf for additional outputs. 