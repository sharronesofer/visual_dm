# Kubernetes Orchestration for Visual_DM

## Overview
This directory contains Kubernetes manifests for deploying, scaling, and managing the Visual_DM application and its supporting infrastructure using industry best practices. The architecture includes Node.js (web), Python (websocket), and backend (FastAPI) services, all containerized and orchestrated via Kubernetes.

## Architecture Diagram

```mermaid
graph TD
  subgraph Cluster
    A[web-app Deployment]
    B[web-app Service]
    C[Ingress]
    D[web-app HPA]
    E[web-app-data PVC]
    F[gp3-storage StorageClass]
    G[web-app-backup CronJob]
    H[db StatefulSet]
    I[db-headless Service]
    J[db-secret Secret]
    K[python-ws Deployment]
    L[python-ws Service]
    M[backend Deployment]
    N[backend Service]
  end
  A -- uses --> B
  B -- exposed by --> C
  A -- scaled by --> D
  A -- mounts --> E
  E -- provisioned by --> F
  E -- backed up by --> G
  H -- uses --> I
  H -- mounts --> E
  H -- uses --> J
  K -- uses --> L
  M -- uses --> N
```

## Manifests
- `web-deployment.yaml`: Node.js web service deployment
- `web-service.yaml`: Node.js web service
- `python-deployment.yaml`: Python websocket service deployment
- `python-service.yaml`: Python websocket service
- `backend-deployment.yaml`: FastAPI backend deployment
- `backend-service.yaml`: FastAPI backend service
- `hpa.yaml`: Horizontal Pod Autoscaler for web-app
- `storageclass.yaml`: StorageClass for dynamic EBS provisioning
- `pvc.yaml`: PersistentVolumeClaim for app data
- `backup-job.yaml`: CronJob for daily backups
- `statefulset.yaml`: StatefulSet for PostgreSQL with headless service
- `db-secret.yaml`: Secret for database password
- `rbac.yaml`: RBAC roles and bindings for least-privilege access
- `networkpolicy.yaml`: Network policies for service isolation

## Deployment Steps
1. **Create Namespace (if needed):**
   ```sh
   kubectl create namespace visual-dm # or your chosen namespace
   ```
2. **Apply StorageClass:**
   ```sh
   kubectl apply -f k8s/storageclass.yaml
   ```
3. **Apply PersistentVolumeClaim:**
   ```sh
   kubectl apply -f k8s/pvc.yaml
   ```
4. **Apply Secrets:**
   ```sh
   kubectl apply -f k8s/db-secret.yaml
   kubectl apply -f k8s/secret.yaml
   ```
5. **Apply Deployments and Services:**
   ```sh
   kubectl apply -f k8s/web-deployment.yaml
   kubectl apply -f k8s/web-service.yaml
   kubectl apply -f k8s/python-deployment.yaml
   kubectl apply -f k8s/python-service.yaml
   kubectl apply -f k8s/backend-deployment.yaml
   kubectl apply -f k8s/backend-service.yaml
   ```
6. **Apply Ingress:**
   ```sh
   kubectl apply -f k8s/ingress.yaml
   ```
7. **Apply HPA:**
   ```sh
   kubectl apply -f k8s/hpa.yaml
   ```
8. **Apply RBAC and Network Policies:**
   ```sh
   kubectl apply -f k8s/rbac.yaml
   kubectl apply -f k8s/networkpolicy.yaml
   ```
9. **Apply Backup CronJob:**
   ```sh
   kubectl apply -f k8s/backup-job.yaml
   ```

## Best Practices
- Use `gp3-storage` for cost-effective, performant EBS volumes.
- All sensitive data is managed via Kubernetes Secrets.
- HPA is configured for CPU scaling; adjust metrics as needed.
- Backups are performed daily; update the backup job for your cloud provider.
- StatefulSets are used for databases to ensure stable network identity and storage.
- RBAC is configured for least-privilege access to resources.
- Network policies restrict traffic between services and namespaces for security.
- Resource requests and limits are set for all deployments to ensure fair scheduling and prevent resource contention.

## Performance Monitoring & Regression Testing
- Liveness and readiness probes are configured for all services to ensure health and availability.
- Integrate performance monitoring tools (e.g., Prometheus, Grafana) using `servicemonitor.yaml` and `prometheus.yaml`.
- Automated performance regression tests should be run in CI/CD and results exported to monitoring dashboards.
- Alerts are configured for critical metrics (e.g., frame time, memory usage) and can be extended with Prometheus alert rules.

## Disaster Recovery & Runbook
- **Restore from Backup:**
  - Extract the latest backup from the backup location (e.g., S3).
  - Restore data to the PVC by running a job that mounts the PVC and untars the backup.
- **Scaling:**
  - Adjust `replicas` in StatefulSet or HPA limits as needed.
- **CI/CD:**
  - Store manifests in version control.
  - Use GitOps tools (e.g., ArgoCD, Flux) to automate deployment.
  - Validate manifests with `kubectl apply --dry-run=client` and `kubeval`.

## Notes
- Update image tags and resource requests/limits for your workload.
- For production, use a dedicated namespace and enable RBAC.
- Consider Helm for templating and managing complex deployments. 