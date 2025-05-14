#!/bin/bash
# backup_incremental.sh: Archive PostgreSQL WAL files for incremental backup.
# Usage: source config.env && ./backup_incremental.sh

set -euo pipefail

# Load configuration
env_file="$(dirname "$0")/config.env"
if [ -f "$env_file" ]; then
  source "$env_file"
else
  echo "Config file not found: $env_file" >&2
  exit 1
fi

# Required environment variables: PGWAL_DIR, BACKUP_DIR, ENCRYPTION_KEY
: "${PGWAL_DIR:?}"
: "${BACKUP_DIR:?}"
: "${ENCRYPTION_KEY:?}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$BACKUP_DIR/backup_incremental_${TIMESTAMP}.log"

{
  echo "[INFO] Archiving WAL files from $PGWAL_DIR at $TIMESTAMP"
  for wal_file in "$PGWAL_DIR"/*; do
    [ -f "$wal_file" ] || continue
    base_name=$(basename "$wal_file")
    dest_file="$BACKUP_DIR/${base_name}_${TIMESTAMP}.wal.enc"
    openssl enc -aes-256-cbc -salt -pbkdf2 -pass env:ENCRYPTION_KEY -in "$wal_file" -out "$dest_file"
    echo "[INFO] Archived and encrypted $wal_file to $dest_file"
  done
  echo "[INFO] WAL archiving complete."
} 2>&1 | tee "$LOG_FILE"

exit 0
