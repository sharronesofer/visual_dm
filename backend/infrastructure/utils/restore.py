"""
restore.py

Script to restore the database from a backup.
- For SQLite: copies a selected backup file to app.db
- For PostgreSQL: uses psql to restore from a .sql file

Usage:
    python utils/restore.py <backup_file>
"""
import os
import shutil
import sys
import logging
import subprocess
import gzip
import hashlib
import json
import argparse
from pathlib import Path
from datetime import datetime
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_restore")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../app.db")
BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backups"))
LOG_FILE = os.path.join(BACKUP_DIR, "backup.log")
ENCRYPTION_KEY = os.getenv("BACKUP_ENCRYPTION_KEY")

def log_event(event):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {event}\n")

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def decompress_file(src, dst):
    with gzip.open(src, 'rb') as f_in, open(dst, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    return dst

def decrypt_file(src, dst, key):
    if not Fernet:
        raise ImportError("cryptography is required for encryption")
    fernet = Fernet(key)
    with open(src, 'rb') as f_in:
        data = f_in.read()
    decrypted = fernet.decrypt(data)
    with open(dst, 'wb') as f_out:
        f_out.write(decrypted)
    return dst

def verify_manifest(backup_path, manifest_path):
    if not os.path.exists(manifest_path):
        logger.warning(f"Manifest not found: {manifest_path}")
        return True
    with open(manifest_path) as f:
        manifest = json.load(f)
    hash_val = hash_file(backup_path)
    if hash_val != manifest.get("hash"):
        logger.error(f"Hash mismatch: {hash_val} != {manifest.get('hash')}")
        log_event(f"Restore failed: hash mismatch for {backup_path}")
        return False
    return True

def restore_sqlite(backup_file, dry_run=False):
    dst = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.db"))
    if dry_run:
        logger.info(f"[DRY RUN] Would restore SQLite database from: {backup_file}")
        return
    shutil.copy2(backup_file, dst)
    logger.info(f"SQLite database restored from: {backup_file}")
    log_event(f"SQLite database restored from: {backup_file}")

def restore_postgres(backup_file, dry_run=False, table=None):
    try:
        if dry_run:
            logger.info(f"[DRY RUN] Would restore PostgreSQL database from: {backup_file}")
            return
        cmd = ["psql", DATABASE_URL, "-f", backup_file]
        if table:
            cmd.extend(["-t", table])
        subprocess.run(cmd, check=True)
        logger.info(f"PostgreSQL database restored from: {backup_file}")
        log_event(f"PostgreSQL database restored from: {backup_file}")
    except Exception as e:
        logger.error(f"PostgreSQL restore failed: {e}")
        log_event(f"PostgreSQL restore failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Database Restore Utility")
    parser.add_argument('backup_file', help='Path to backup file (can be .gz/.enc)')
    parser.add_argument('--manifest', help='Path to manifest file (optional)')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (do not actually restore)')
    parser.add_argument('--verify', action='store_true', help='Verify backup hash before restore')
    parser.add_argument('--table', help='Restore only a specific table (Postgres only)')
    args = parser.parse_args()
    backup_file = args.backup_file
    manifest_path = args.manifest or (backup_file + ".manifest.json")
    # Decrypt if needed
    if backup_file.endswith('.enc') and ENCRYPTION_KEY:
        tmp = backup_file[:-4]
        decrypt_file(backup_file, tmp, ENCRYPTION_KEY.encode())
        backup_file = tmp
    # Decompress if needed
    if backup_file.endswith('.gz'):
        tmp = backup_file[:-3]
        decompress_file(backup_file, tmp)
        backup_file = tmp
    # Verify hash
    if args.verify:
        if not verify_manifest(backup_file, manifest_path):
            logger.error("Backup verification failed. Aborting restore.")
            return
    # Restore
    if DATABASE_URL.startswith("sqlite"):
        restore_sqlite(backup_file, dry_run=args.dry_run)
    elif DATABASE_URL.startswith("postgres"):
        restore_postgres(backup_file, dry_run=args.dry_run, table=args.table)
    else:
        logger.error(f"Unsupported database URL: {DATABASE_URL}")
        log_event(f"Restore failed: unsupported database URL {DATABASE_URL}")

if __name__ == "__main__":
    main() 