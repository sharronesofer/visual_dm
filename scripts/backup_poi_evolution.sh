#!/bin/bash
set -e

BACKUP_DIR=${1:-./backups}
DB_NAME="visual_dm_test"
DB_USER="postgres"
TABLES="poi_states poi_transitions poi_histories"
DATE=$(date +"%Y%m%d_%H%M%S")
FILENAME="$BACKUP_DIR/poi_evolution_backup_$DATE.sql"

mkdir -p "$BACKUP_DIR"

pg_dump -U "$DB_USER" -d "$DB_NAME" -t poi_states -t poi_transitions -t poi_histories > "$FILENAME"

if [ $? -eq 0 ]; then
  echo "Backup successful: $FILENAME"
else
  echo "Backup failed!"
  exit 1
fi 