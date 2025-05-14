#!/bin/bash
# manifest_generator.sh: Generate a manifest of all files in the backup directory.
# Usage: source config.env && ./manifest_generator.sh

set -euo pipefail

# Load configuration
env_file="$(dirname "$0")/config.env"
if [ -f "$env_file" ]; then
  source "$env_file"
else
  echo "Config file not found: $env_file" >&2
  exit 1
fi

# Required environment variable: FILE_BACKUP_DIR
: "${FILE_BACKUP_DIR:?}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MANIFEST_FILE="$FILE_BACKUP_DIR/manifest_${TIMESTAMP}.txt"
LOG_FILE="$FILE_BACKUP_DIR/manifest_generator_${TIMESTAMP}.log"

{
  echo "[INFO] Generating manifest for $FILE_BACKUP_DIR at $TIMESTAMP"
  find "$FILE_BACKUP_DIR" -type f | sort > "$MANIFEST_FILE"
  echo "[INFO] Manifest generated: $MANIFEST_FILE"
} 2>&1 | tee "$LOG_FILE"

exit 0
