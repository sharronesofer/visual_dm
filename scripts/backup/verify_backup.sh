#!/bin/bash
# verify_backup.sh: Verify integrity of encrypted, compressed PostgreSQL backup files.
# Usage: source config.env && ./verify_backup.sh <backup_file>

set -euo pipefail

# Load configuration
env_file="$(dirname "$0")/config.env"
if [ -f "$env_file" ]; then
  source "$env_file"
else
  echo "Config file not found: $env_file" >&2
  exit 1
fi

# Required environment variables: ENCRYPTION_KEY
: "${ENCRYPTION_KEY:?}"

BACKUP_FILE="${1:-}"
if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file>" >&2
  exit 1
fi

LOG_FILE="${BACKUP_FILE}.verify.log"

{
  echo "[INFO] Verifying backup file: $BACKUP_FILE"
  # Test decryption and decompression
  openssl enc -d -aes-256-cbc -pbkdf2 -pass env:ENCRYPTION_KEY -in "$BACKUP_FILE" | gunzip -t
  echo "[INFO] Decryption and decompression successful."
  # Optional: Restore to test DB and compare row counts (requires test DB config)
  # Uncomment and configure as needed
  # TEST_DB="test_restore_db"
  # openssl enc -d -aes-256-cbc -pbkdf2 -pass env:ENCRYPTION_KEY -in "$BACKUP_FILE" | gunzip | psql -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$TEST_DB"
  # echo "[INFO] Restore to $TEST_DB completed."
} 2>&1 | tee "$LOG_FILE"

exit 0
