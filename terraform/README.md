# Terraform Infrastructure as Code for Visual DM

This directory contains Terraform code to provision and manage cloud infrastructure for the Visual DM platform.

## Components Managed
- **EKS (Kubernetes) Cluster**
- **RDS (Postgres) Database**
- **ElastiCache (Redis)**
- **S3 Buckets (Backups, Media)**
- **IAM Roles and Policies**
- **VPC, Subnets, Security Groups**

## Usage

1. **Install Terraform**
   - https://www.terraform.io/downloads.html

2. **Initialize the Directory**
   ```sh
   terraform init
   ```

3. **Configure Variables**
   - Copy `terraform.tfvars.example` to `terraform.tfvars` and fill in your values.

4. **Plan the Deployment**
   ```sh
   terraform plan
   ```

5. **Apply the Deployment**
   ```sh
   terraform apply
   ```

6. **Destroy Resources (if needed)**
   ```sh
   terraform destroy
   ```

## State Management
- Use remote state (e.g., S3 + DynamoDB) for team environments.
- Never commit `terraform.tfstate` to version control.

## Files
- `main.tf` – Main infrastructure resources
- `variables.tf` – Input variables
- `outputs.tf` – Output values

## Best Practices
- Use workspaces for dev/staging/prod
- Use environment variables for secrets
- Review plan output before applying
- Store state securely

---
For more details, see the comments in each `.tf` file. 