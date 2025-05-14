# Operational Runbooks

## Backup and Restore
### PostgreSQL
- **Backup**: Triggered automatically by CronJob. To run manually:
  1. `kubectl create job --from=cronjob/pg-backup pg-backup-manual -n visualdm`
- **Restore**:
  1. Edit `pg-restore-job.yaml` to specify backup file
  2. `kubectl apply -f k8s/pg-restore-job.yaml`
  3. Monitor job logs for completion

### Redis
- **Backup**: Ensure RDB snapshotting is enabled
- **Restore**: Replace RDB file in PVC, restart Redis pod

### Elasticsearch
- **Backup**: Use snapshot API
- **Restore**: Use snapshot API to restore indices

## Scaling
- **Horizontal Scaling**: Edit `hpa.yaml` and apply changes
- **Vertical Scaling**: Edit resource requests/limits in deployment manifests
- **Monitor**: Use Grafana dashboards

## Failover
- **Promote Standby**: Update DNS/load balancer to point to standby
- **Monitor**: Check system health and logs

## Security Incident Response
- **Containment**: Isolate affected pods/nodes
- **Investigation**: Review logs, audit RBAC and network policies
- **Remediation**: Patch vulnerabilities, rotate secrets
- **Recovery**: Restore from backup if needed 