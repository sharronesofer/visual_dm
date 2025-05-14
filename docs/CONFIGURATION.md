# Configuration Reference

## Environment Variables
- `FLASK_APP`: Flask app entrypoint
- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Flask secret key
- `POSTGRES_USER`: Postgres username
- `POSTGRES_PASSWORD`: Postgres password
- `POSTGRES_DB`: Database name
- `DATABASE_URL`: SQLAlchemy connection string
- `REDIS_HOST`: Redis hostname
- `REDIS_PORT`: Redis port
- `REDIS_DB`: Redis database index
- `JWT_SECRET_KEY`: JWT signing key
- `JWT_ACCESS_TOKEN_EXPIRES`: JWT access token expiry (seconds)
- `JWT_REFRESH_TOKEN_EXPIRES`: JWT refresh token expiry (seconds)

## Configuration Files
- `.env`: Local environment variables (not committed)
- `docker-compose.yml`: Service definitions and environment
- `k8s/configmap.yaml`: Non-sensitive config for Kubernetes
- `k8s/secret.yaml`: Sensitive config for Kubernetes

## Secret Management
- Use Kubernetes Secrets for all sensitive values
- For production, consider external secret managers (e.g., HashiCorp Vault)
- Rotate secrets regularly and avoid logging secret values 