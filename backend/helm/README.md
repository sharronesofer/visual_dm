# Visual DM Backend Helm Chart

This Helm chart deploys the Visual DM backend API (FastAPI) to a Kubernetes cluster, providing production-grade orchestration, scaling, and configuration.

## Features
- Configurable replica count, resources, and environment variables
- Ingress support (NGINX by default)
- ConfigMap and Secret management for environment variables
- Optional persistent storage (PVC)
- Liveness/readiness probes

## Usage

1. **Configure values.yaml**
   - Set the Docker image repository and tag
   - Update environment variables and secrets
   - Adjust resources, ingress, and persistence as needed

2. **Install the chart**
   ```sh
   helm install visual-dm-backend ./
   ```

3. **Upgrade the chart**
   ```sh
   helm upgrade visual-dm-backend ./
   ```

4. **Uninstall the chart**
   ```sh
   helm uninstall visual-dm-backend
   ```

## Configuration
See `values.yaml` for all available options. Key settings:
- `image.repository`, `image.tag`: Docker image to deploy
- `replicaCount`: Number of backend pods
- `service.*`: Service type and port
- `ingress.*`: Ingress configuration
- `env.*`: Non-sensitive environment variables
- `secretEnv.*`: Sensitive environment variables (secrets)
- `resources.*`: CPU/memory requests and limits
- `persistence.*`: Persistent storage options

## Templates
- `deployment.yaml`: Main Deployment
- `service.yaml`: Service
- `ingress.yaml`: Ingress
- `configmap.yaml`: ConfigMap for env
- `secret.yaml`: Secret for sensitive env
- `pvc.yaml`: PersistentVolumeClaim (optional)

## Persistent Storage

To enable persistent storage (for database files, uploads, etc.), set `persistence.enabled: true` in `values.yaml`. The chart will provision a PersistentVolumeClaim and mount it at `/data` in the container by default.

- Configure `persistence.size`, `persistence.accessMode`, and `persistence.storageClass` as needed.
- The mount path can be changed by editing the `volumeMounts` section in `deployment.yaml`.

## Notes
- Replace all placeholder values (especially secrets) before deploying to production.
- For advanced usage, see the official Helm documentation: https://helm.sh/docs/ 