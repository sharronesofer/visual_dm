#!/bin/bash
# backup_files.sh: Back up specified directories using rsync, preserving permissions and metadata.
# Usage: source config.env && ./backup_files.sh

set -euo pipefail

# Load configuration
env_file="$(dirname "$0")/config.env"
if [ -f "$env_file" ]; then
  source "$env_file"
else
  echo "Config file not found: $env_file" >&2
  exit 1
fi

# Required environment variables: FILE_SRC_DIRS, FILE_BACKUP_DIR, FILE_EXCLUDES
: "${FILE_SRC_DIRS:?}"
: "${FILE_BACKUP_DIR:?}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$FILE_BACKUP_DIR/backup_files_${TIMESTAMP}.log"

# Build rsync exclude options
EXCLUDE_OPTS=""
if [ -n "${FILE_EXCLUDES:-}" ]; then
  IFS=',' read -ra EXCLUDES <<< "$FILE_EXCLUDES"
  for pattern in "${EXCLUDES[@]}"; do
    EXCLUDE_OPTS+=" --exclude=$pattern"
  done
fi

{
  echo "[INFO] Starting file system backup at $TIMESTAMP"
  for src in $FILE_SRC_DIRS; do
    echo "[INFO] Backing up $src to $FILE_BACKUP_DIR"
    rsync -aAXHv --delete $EXCLUDE_OPTS "$src" "$FILE_BACKUP_DIR/"
  done
  echo "[INFO] File system backup complete."
} 2>&1 | tee "$LOG_FILE"

exit 0
