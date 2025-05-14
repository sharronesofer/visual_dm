# Backup and Restore Procedures

## Backup Overview
- Daily Postgres backups at 2 AM via Kubernetes CronJob (see k8s/backup-cronjob.yaml)
- Backups stored in S3 bucket with encryption
- Credentials managed via Kubernetes secrets

## Retention Policy
- 7 daily backups
- 4 weekly backups
- 12 monthly backups
- Old backups automatically deleted per S3 lifecycle policy

## Backup Verification
- Periodically restore latest backup to staging DB
- Run integrity checks (e.g., pg_restore --list)
- Set up notification for backup failures

## Restore Procedure
1. Identify the most recent valid backup in S3
2. Download and decompress backup file
3. Restore to Postgres:
   ```sh
   gunzip < visualdm-YYYYMMDD.sql.gz | psql -h <host> -U <user> -d <db>
   ```
4. Verify data integrity and application functionality

## Troubleshooting
- Check CronJob logs: `kubectl logs job/<job-name>`
- Check S3 for backup file presence
- For permission errors, verify secret configuration
- For restore errors, check Postgres logs and backup file integrity 