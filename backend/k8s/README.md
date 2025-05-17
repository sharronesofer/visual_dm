# Kubernetes Manifests for Visual DM Backend

This directory contains Kubernetes YAML manifests for deploying the Visual DM backend API and its dependencies in a Kubernetes cluster.

## Contents
- `deployment.yaml`: Main Deployment resource for the backend API
- `service.yaml`: ClusterIP Service exposing the backend API
- `ingress.yaml`: Ingress resource for external access (optional, requires ingress controller)
- `configmap.yaml`: Configuration for environment variables and non-sensitive settings
- `secret.yaml`: Kubernetes Secret for sensitive environment variables (e.g., database credentials, JWT secret)
- `persistentvolumeclaim.yaml`: PVC for persistent storage (if needed)

## Usage

1. **Configure Secrets and ConfigMaps**
   - Edit `configmap.yaml` and `secret.yaml` to match your environment.

2. **Apply Manifests**
   ```sh
   kubectl apply -f .
   ```

3. **Verify Deployment**
   - Check pods, services, and ingress:
     ```sh
     kubectl get pods,svc,ingress
     ```

4. **Access the API**
   - If using Ingress, access via the configured hostname.
   - Otherwise, use `kubectl port-forward` or expose the service as needed.

## Notes
- These manifests are suitable for production and development clusters.
- For advanced configuration, use the Helm chart in `../helm/`.
- Adjust resource requests/limits and replica counts as needed for your environment.

## Persistent Storage

To enable persistent storage (for database files, uploads, etc.), apply the `persistentvolumeclaim.yaml` manifest and uncomment the relevant section in `deployment.yaml` to mount the PVC at `/data` (or another path as needed):

- Apply the PVC:
  ```sh
  kubectl apply -f persistentvolumeclaim.yaml
  ```
- Edit `deployment.yaml` to uncomment the `volumeMounts` and `volumes` sections, then re-apply the deployment.

Adjust the storage size and mount path as needed for your use case.

## Horizontal Pod Autoscaling

To enable automatic scaling based on CPU utilization:

- With raw manifests: Create an HPA manifest (see `hpa.yaml` for an example) and apply it:
  ```sh
  kubectl apply -f hpa.yaml
  ```
- With Helm: Set `autoscaling.enabled: true` in `values.yaml` and configure `minReplicas`, `maxReplicas`, and `targetCPUUtilizationPercentage` as needed.

This will automatically scale the number of backend pods based on observed CPU usage. 