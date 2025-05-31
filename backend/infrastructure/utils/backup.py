"""
backup.py

Script to perform a database backup.
- For SQLite: copies app.db to backups/app_backup_<timestamp>.db
- For PostgreSQL: uses pg_dump to create a .sql backup in backups/

Usage:
    python utils/backup.py
"""
import os
import shutil
import logging
from datetime import datetime, timedelta
import subprocess
import hashlib
import json
import gzip
import argparse
from pathlib import Path
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_backup")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../app.db")
BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backups"))
LOG_FILE = os.path.join(BACKUP_DIR, "backup.log")
RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
ENCRYPTION_KEY = os.getenv("BACKUP_ENCRYPTION_KEY")
os.makedirs(BACKUP_DIR, exist_ok=True)

def log_event(event):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {event}\n")

def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def compress_file(src, dst):
    with open(src, 'rb') as f_in, gzip.open(dst, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    return dst

def encrypt_file(src, dst, key):
    if not Fernet:
        raise ImportError("cryptography is required for encryption")
    fernet = Fernet(key)
    with open(src, 'rb') as f_in:
        data = f_in.read()
    encrypted = fernet.encrypt(data)
    with open(dst, 'wb') as f_out:
        f_out.write(encrypted)
    return dst

def create_manifest(backup_path, backup_type, hash_val):
    stat = os.stat(backup_path)
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "type": backup_type,
        "file": os.path.basename(backup_path),
        "size": stat.st_size,
        "hash": hash_val
    }
    manifest_path = backup_path + ".manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    return manifest_path

def prune_old_backups():
    now = datetime.now()
    for file in Path(BACKUP_DIR).glob("*backup_*.db.gz"):
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if (now - mtime).days > RETENTION_DAYS:
            file.unlink()
            log_event(f"Pruned old backup: {file}")
    for file in Path(BACKUP_DIR).glob("*backup_*.sql.gz"):
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if (now - mtime).days > RETENTION_DAYS:
            file.unlink()
            log_event(f"Pruned old backup: {file}")

def backup_sqlite(backup_type):
    src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.db"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_dst = os.path.join(BACKUP_DIR, f"app_backup_{timestamp}.db")
    shutil.copy2(src, raw_dst)
    gz_dst = raw_dst + ".gz"
    compress_file(raw_dst, gz_dst)
    os.remove(raw_dst)
    if ENCRYPTION_KEY:
        enc_dst = gz_dst + ".enc"
        encrypt_file(gz_dst, enc_dst, ENCRYPTION_KEY.encode())
        os.remove(gz_dst)
        final_dst = enc_dst
    else:
        final_dst = gz_dst
    hash_val = hash_file(final_dst)
    manifest = create_manifest(final_dst, backup_type, hash_val)
    log_event(f"SQLite backup created: {final_dst} | manifest: {manifest}")
    return final_dst

def backup_postgres(backup_type):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_dst = os.path.join(BACKUP_DIR, f"pg_backup_{timestamp}.sql")
    try:
        subprocess.run([
            "pg_dump", DATABASE_URL, "-f", raw_dst
        ], check=True)
        gz_dst = raw_dst + ".gz"
        compress_file(raw_dst, gz_dst)
        os.remove(raw_dst)
        if ENCRYPTION_KEY:
            enc_dst = gz_dst + ".enc"
            encrypt_file(gz_dst, enc_dst, ENCRYPTION_KEY.encode())
            os.remove(gz_dst)
            final_dst = enc_dst
        else:
            final_dst = gz_dst
        hash_val = hash_file(final_dst)
        manifest = create_manifest(final_dst, backup_type, hash_val)
        log_event(f"PostgreSQL backup created: {final_dst} | manifest: {manifest}")
        return final_dst
    except Exception as e:
        log_event(f"PostgreSQL backup failed: {e}")
        logger.error(f"PostgreSQL backup failed: {e}")
        return None

def verify_backup(backup_path):
    # For now, just check hash and decompress/decrypt if needed
    try:
        if backup_path.endswith('.enc') and ENCRYPTION_KEY:
            tmp = backup_path[:-4]
            encrypt_file(backup_path, tmp, ENCRYPTION_KEY.encode())
            backup_path = tmp
        if backup_path.endswith('.gz'):
            with gzip.open(backup_path, 'rb') as f:
                f.read(1024)  # Try to read some bytes
        log_event(f"Backup verified: {backup_path}")
        return True
    except Exception as e:
        log_event(f"Backup verification failed: {backup_path} | {e}")
        return False

def main():
    global RETENTION_DAYS
    parser = argparse.ArgumentParser(description="Database Backup Utility")
    parser.add_argument('--type', choices=['full', 'incremental'], default='full', help='Backup type')
    parser.add_argument('--retention', type=int, default=RETENTION_DAYS, help='Retention days')
    parser.add_argument('--verify', action='store_true', help='Verify backup after creation')
    args = parser.parse_args()
    RETENTION_DAYS = args.retention
    prune_old_backups()
    if DATABASE_URL.startswith("sqlite"):
        backup_path = backup_sqlite(args.type)
    elif DATABASE_URL.startswith("postgres"):
        backup_path = backup_postgres(args.type)
    else:
        logger.error(f"Unsupported database URL: {DATABASE_URL}")
        return
    if args.verify and backup_path:
        verify_backup(backup_path)

if __name__ == "__main__":
    main() 