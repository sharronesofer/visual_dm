"""
db_health.py

Script to check database health and collect basic metrics.
- For SQLite: checks file size and table count
- For PostgreSQL: connects and counts tables

Usage:
    python utils/db_health.py
"""
import os
import logging
import sqlite3
from sqlalchemy import create_engine, inspect
import gzip
import hashlib
import json
import argparse
from datetime import datetime
try:
    from cryptography.fernet import Fernet
except ImportError:
    Fernet = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_health")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///../app.db")
BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backups"))
LOG_FILE = os.path.join(BACKUP_DIR, "backup.log")
ENCRYPTION_KEY = os.getenv("BACKUP_ENCRYPTION_KEY")

def log_event(event):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
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
        f_out.write(f_in.read())
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
        log_event(f"Backup verification failed: hash mismatch for {backup_path}")
        return False
    return True

def verify_backup(backup_file, manifest_path=None):
    try:
        orig_file = backup_file
        if not os.path.exists(backup_file):
            logger.error(f"Backup file does not exist: {backup_file}")
            log_event(f"Backup file does not exist: {backup_file}")
            return False
        if backup_file.endswith('.enc') and ENCRYPTION_KEY:
            tmp = backup_file[:-4]
            decrypt_file(backup_file, tmp, ENCRYPTION_KEY.encode())
            backup_file = tmp
        if backup_file.endswith('.gz'):
            tmp = backup_file[:-3]
            decompress_file(backup_file, tmp)
            backup_file = tmp
        if manifest_path:
            if not verify_manifest(backup_file, manifest_path):
                logger.error(f"Backup verification failed for {orig_file}")
                log_event(f"Backup verification failed for {orig_file}")
                return False
        logger.info(f"Backup verified: {orig_file}")
        log_event(f"Backup verified: {orig_file}")
        return True
    except Exception as e:
        logger.error(f"Backup verification error: {backup_file} | {e}")
        log_event(f"Backup verification error: {backup_file} | {e}")
        return False

def check_sqlite():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../app.db"))
    if not os.path.exists(db_path):
        logger.error(f"SQLite database file not found: {db_path}")
        return
    size = os.path.getsize(db_path)
    logger.info(f"SQLite DB file size: {size/1024:.2f} KB")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
    table_count = cursor.fetchone()[0]
    logger.info(f"SQLite table count: {table_count}")
    conn.close()
    log_event(f"SQLite health check: size={size}, tables={table_count}")

def check_postgres():
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"PostgreSQL table count: {len(tables)}")
        log_event(f"PostgreSQL health check: tables={len(tables)}")
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        log_event(f"PostgreSQL health check failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="DB Health and Backup Verification Utility")
    parser.add_argument('--verify-backup', help='Path to backup file to verify')
    parser.add_argument('--manifest', help='Path to manifest file (optional)')
    args = parser.parse_args()
    if args.verify_backup:
        verify_backup(args.verify_backup, args.manifest or (args.verify_backup + ".manifest.json"))
        return
    if DATABASE_URL.startswith("sqlite"):
        check_sqlite()
    elif DATABASE_URL.startswith("postgres"):
        check_postgres()
    else:
        logger.error(f"Unsupported database URL: {DATABASE_URL}")

if __name__ == "__main__":
    main() 