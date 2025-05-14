# Deployment Guide

## Local Development
1. Clone the repository
2. Create and activate a Python virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Set environment variables (see [CONFIGURATION.md](CONFIGURATION.md))
5. Run the app: `flask run` or `python run.py`

## Docker Deployment
1. Build the Docker image: `docker build -t visualdm .`
2. Run with Docker Compose: `docker-compose up`
3. Access the app at http://localhost:5000
4. Configure environment variables in `.env` file

## Kubernetes Deployment (Production-Grade)

### 1. Prerequisites
- Kubernetes cluster (minikube, kind, or cloud provider)
- `kubectl` configured for your cluster
- (Recommended) `helm` for monitoring/logging stack
- Docker image(s) pushed to a registry accessible by your cluster
- Review [CONFIGURATION.md](CONFIGURATION.md) and [SECURITY.md](SECURITY.md)

### 2. Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```
- Use a dedicated namespace (e.g., `visual-dm`) for workload isolation.

### 3. Apply ConfigMaps and Secrets
- Edit `k8s/configmap.yaml` and `k8s/secrets.yaml` (or `k8s/secret.yaml`) with your environment-specific values.
- Apply them:
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml   # or secret.yaml
```
- Store all sensitive values in Secrets. See [CONFIGURATION.md](CONFIGURATION.md) for required keys.

### 4. Deploy Core Services
- **Web Application:**
  ```bash
  kubectl apply -f k8s/web-deployment.yaml
  kubectl apply -f k8s/web-service.yaml
  ```
- **Database (Postgres):**
  ```bash
  kubectl apply -f k8s/postgres-deployment.yaml
  kubectl apply -f k8s/postgres-service.yaml
  ```
- **Redis:**
  ```bash
  kubectl apply -f k8s/redis-deployment.yaml
  kubectl apply -f k8s/redis-service.yaml
  ```
- **Elasticsearch:**
  ```bash
  kubectl apply -f k8s/elasticsearch.yaml
  kubectl apply -f k8s/elasticsearch-service.yaml
  ```
- **Persistent Volumes:**
  - All stateful workloads use `volumeClaimTemplates` or PVCs (see `k8s/pvc.yaml`, `k8s/postgres-deployment.yaml`, etc.)

### 5. Monitoring & Logging
- **Prometheus:**
  ```bash
  kubectl apply -f k8s/prometheus.yaml
  kubectl apply -f k8s/servicemonitor.yaml
  ```
- **Grafana:**
  ```bash
  kubectl apply -f k8s/grafana.yaml
  ```
- **ELK Stack (Elasticsearch, Logstash, Kibana):**
  ```bash
  kubectl apply -f k8s/elk.yaml
  ```

### 6. Ingress Setup (with TLS)
- Edit `k8s/ingress.yaml` to set your domain and TLS secret.
- Apply:
  ```bash
  kubectl apply -f k8s/ingress.yaml
  ```
- Ensure your DNS points to the ingress controller's external IP.
- Use cert-manager or your cloud provider to provision TLS certificates.

### 7. RBAC and ServiceAccount
- Apply RBAC and ServiceAccount manifests:
  ```bash
  kubectl apply -f k8s/serviceaccount.yaml
  kubectl apply -f k8s/rbac.yaml
  ```
- Principle of least privilege: only grant access to required resources.

### 8. Network Policies
- Enforce network segmentation:
  ```bash
  kubectl apply -f k8s/networkpolicy.yaml
  ```
- Default deny all, then allow only required traffic (see manifest for examples).

### 9. Autoscaling (HPA)
- Apply autoscaler:
  ```bash
  kubectl apply -f k8s/hpa.yaml
  # or for alternate config:
  kubectl apply -f k8s/autoscaler.yaml
  ```
- Adjust min/max replicas and CPU utilization as needed.

### 10. Backup & Restore Automation
- **Postgres Backups:**
  ```bash
  kubectl apply -f k8s/pg-backup-cronjob.yaml
  ```
- **Restore:**
  - Edit `k8s/pg-restore-job.yaml` to specify the backup file.
  - Apply:
    ```bash
    kubectl apply -f k8s/pg-restore-job.yaml
    ```

### 11. Health Checks & Readiness Probes
- All deployments include liveness and readiness probes (see `k8s/web-deployment.yaml`, `k8s/postgres-deployment.yaml`, etc.).
- Validate with:
  ```bash
  kubectl get pods -n visual-dm
  kubectl describe pod <pod-name> -n visual-dm
  ```

### 12. Validate Deployment Health
- Check all pods and services:
  ```bash
  kubectl get all -n visual-dm
  kubectl get ingress -n visual-dm
  kubectl get pvc -n visual-dm
  kubectl logs <pod-name> -n visual-dm
  ```
- Access Grafana and Prometheus dashboards for metrics.
- Use Kibana for log aggregation and search.

### 13. Upgrades & Rollbacks
- Use rolling updates for Deployments/StatefulSets:
  ```bash
  kubectl set image deployment/visual-dm-web web=<new-image>:<tag> -n visual-dm
  ```
- Rollback if needed:
  ```bash
  kubectl rollout undo deployment/visual-dm-web -n visual-dm
  ```
- For database migrations, use a migration job or run manually in a pod.

### 14. Best Practices
- Use resource requests/limits for all containers.
- Use `readOnlyRootFilesystem: true` and drop all capabilities for security.
- Store all secrets in Kubernetes Secrets, never in ConfigMaps or images.
- Regularly test backups and restores.
- Monitor for pod restarts, OOM kills, and failed probes.
- Use `kubectl diff -f <manifest>` before applying changes.
- Keep manifests under version control.

### 15. Troubleshooting
- **Pod CrashLoopBackOff:**
  - Check logs: `kubectl logs <pod> -n visual-dm`
  - Check resource limits and environment variables.
- **PersistentVolumeClaim Pending:**
  - Ensure your cluster has a default StorageClass and enough resources.
- **Ingress not routing:**
  - Check DNS, ingress controller status, and TLS secret.
- **Database connection errors:**
  - Check secrets, service endpoints, and pod logs.
- **No metrics/logs in Grafana/Kibana:**
  - Check ServiceMonitor, Prometheus, and ELK pod health.
- **NetworkPolicy blocks traffic:**
  - Review policy rules and pod labels.

---
For configuration details, see [CONFIGURATION.md](CONFIGURATION.md).
For security best practices, see [SECURITY.md](SECURITY.md).
Reference all Kubernetes manifests in the `k8s/` directory for further customization.

## Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Kubernetes cluster (minikube, kind, or cloud)
- kubectl, helm (for monitoring/logging)

# Advanced Deployment Strategies

## Blue-Green Deployment
Blue-green deployment minimizes downtime and risk by running two production environments ("blue" and "green"). At any time, only one environment is live. Deploy new versions to the idle environment, run tests, then switch traffic when ready.

- Use [Argo Rollouts](https://argoproj.github.io/argo-rollouts/) or similar tools for automated blue-green deployments.
- Example manifest: `k8s/rollout-bluegreen.yaml`
- Steps:
  1. Deploy new version to "green".
  2. Run health checks and validation.
  3. Switch service traffic from "blue" to "green".
  4. Roll back by switching back to "blue" if needed.

## Canary Deployment
Canary deployment gradually shifts traffic to a new version, reducing risk by exposing only a subset of users initially.

- Use [Argo Rollouts](https://argoproj.github.io/argo-rollouts/) or native Kubernetes strategies.
- Example manifest: `k8s/rollout-canary.yaml`
- Steps:
  1. Deploy new version as a canary.
  2. Route a small percentage of traffic to the canary.
  3. Monitor metrics and errors.
  4. Gradually increase traffic if healthy.
  5. Roll back if issues are detected.

## References
- See `k8s/rollout-bluegreen.yaml` and `k8s/rollout-canary.yaml` for manifest examples.
- For more, see [Kubernetes Deployment Strategies](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#strategy).

--- 