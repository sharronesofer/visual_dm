#!/bin/bash
# prune_backups.sh: Delete old backup files based on retention policy.
# Usage: source config.env && ./prune_backups.sh

set -euo pipefail

# Load configuration
env_file="$(dirname "$0")/config.env"
if [ -f "$env_file" ]; then
  source "$env_file"
else
  echo "Config file not found: $env_file" >&2
  exit 1
fi

# Required environment variables: BACKUP_DIR, RETENTION_DAYS
: "${BACKUP_DIR:?}"
: "${RETENTION_DAYS:?}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$BACKUP_DIR/prune_backups_${TIMESTAMP}.log"

{
  echo "[INFO] Pruning backups older than $RETENTION_DAYS days in $BACKUP_DIR at $TIMESTAMP"
  find "$BACKUP_DIR" -type f -name "*.enc" -mtime +$RETENTION_DAYS -print -delete
  echo "[INFO] Pruning complete."
} 2>&1 | tee "$LOG_FILE"

exit 0
