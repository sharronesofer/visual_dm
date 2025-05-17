#!/bin/bash
set -e

BACKUP_FILE=$1
DB_NAME="visual_dm_test"
DB_USER="postgres"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: $0 <backup_file.sql>"
  exit 1
fi

read -p "This will overwrite POI evolution tables in $DB_NAME. Are you sure? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
  echo "Restore cancelled."
  exit 0
fi

psql -U "$DB_USER" -d "$DB_NAME" -f "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "Restore successful from $BACKUP_FILE"
else
  echo "Restore failed!"
  exit 1
fi 