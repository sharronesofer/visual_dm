#!/bin/bash
# monitor_backups.sh: Monitor backup status, verify latest backup, and send notifications on failure.
# Usage: source config.env && ./monitor_backups.sh

set -euo pipefail

# Load configuration
env_file="$(dirname "$0")/config.env"
if [ -f "$env_file" ]; then
  source "$env_file"
else
  echo "Config file not found: $env_file" >&2
  exit 1
fi

# Required environment variables: BACKUP_DIR, NOTIFY_EMAIL, NOTIFY_SLACK_WEBHOOK
: "${BACKUP_DIR:?}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$BACKUP_DIR/monitor_backups_${TIMESTAMP}.log"

# Find the most recent backup file
LATEST_BACKUP=$(find "$BACKUP_DIR" -type f -name "*.enc" -printf "%T@ %p\n" | sort -n | tail -1 | cut -d' ' -f2-)

notify_failure() {
  MSG="$1"
  echo "[ALERT] $MSG"
  if [ -n "${NOTIFY_EMAIL:-}" ]; then
    echo "$MSG" | mail -s "[Backup Alert] Failure detected" "$NOTIFY_EMAIL"
  fi
  if [ -n "${NOTIFY_SLACK_WEBHOOK:-}" ]; then
    curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$MSG\"}" "$NOTIFY_SLACK_WEBHOOK"
  fi
}

{
  echo "[INFO] Monitoring backups at $TIMESTAMP"
  if [ -z "$LATEST_BACKUP" ]; then
    notify_failure "No recent backup files found in $BACKUP_DIR."
    exit 2
  fi
  echo "[INFO] Latest backup: $LATEST_BACKUP"
  # Run verify_backup.sh on the latest backup
  if ! ./verify_backup.sh "$LATEST_BACKUP"; then
    notify_failure "Backup verification failed for $LATEST_BACKUP."
    exit 3
  fi
  echo "[INFO] Backup verification successful."
} 2>&1 | tee "$LOG_FILE"

exit 0
