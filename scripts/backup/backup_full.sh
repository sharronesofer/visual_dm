#!/bin/bash
# backup_full.sh: Perform a full PostgreSQL database backup with compression and encryption.
# Usage: source config.env && ./backup_full.sh

set -euo pipefail

# Load configuration
env_file="$(dirname "$0")/config.env"
if [ -f "$env_file" ]; then
  source "$env_file"
else
  echo "Config file not found: $env_file" >&2
  exit 1
fi

# Required environment variables: PGHOST, PGPORT, PGUSER, PGDATABASE, BACKUP_DIR, ENCRYPTION_KEY
: "${PGHOST:?}"
: "${PGPORT:?}"
: "${PGUSER:?}"
: "${PGDATABASE:?}"
: "${BACKUP_DIR:?}"
: "${ENCRYPTION_KEY:?}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${PGDATABASE}_full_${TIMESTAMP}.sql.gz.enc"
LOG_FILE="$BACKUP_DIR/backup_full_${TIMESTAMP}.log"

{
  echo "[INFO] Starting full backup for $PGDATABASE at $TIMESTAMP"
  pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$PGDATABASE" \
    | gzip \
    | openssl enc -aes-256-cbc -salt -pbkdf2 -pass env:ENCRYPTION_KEY \
    > "$BACKUP_FILE"
  echo "[INFO] Backup complete: $BACKUP_FILE"
  echo "[INFO] Verifying backup file..."
  openssl enc -d -aes-256-cbc -pbkdf2 -pass env:ENCRYPTION_KEY -in "$BACKUP_FILE" | gunzip -t
  echo "[INFO] Backup file integrity verified."
} 2>&1 | tee "$LOG_FILE"

exit 0
