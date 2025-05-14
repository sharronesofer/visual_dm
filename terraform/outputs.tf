// Terraform outputs for Visual DM infrastructure

// --- EKS ---
output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = module.eks.cluster_name
}

// --- RDS ---
output "rds_endpoint" {
  description = "Endpoint for the RDS Postgres instance"
  value       = module.rds.db_instance_endpoint
}

// --- Redis ---
output "redis_endpoint" {
  description = "Primary endpoint for ElastiCache Redis"
  value       = module.redis.primary_endpoint_address
}

// --- S3 Buckets ---
output "s3_backup_bucket" {
  description = "Name of the S3 backup bucket"
  value       = aws_s3_bucket.backups.bucket
}

output "s3_media_bucket" {
  description = "Name of the S3 media bucket"
  value       = aws_s3_bucket.media.bucket
} 