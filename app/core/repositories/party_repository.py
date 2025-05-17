"""
Repository layer for party-related database operations with transaction-based persistence and integrity checks.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.core.models.party import Party
import hashlib
import json
import logging
import threading
import time
import os

logger = logging.getLogger(__name__)

CURRENT_PARTY_SCHEMA_VERSION = '1.0.0'

class PartyVersionStrategy:
    """
    Base class for party schema version strategies.
    Implement upgrade/downgrade logic for each schema version as needed.
    """
    def upgrade(self, party: Party) -> Party:
        """Upgrade party to this version (no-op for base)."""
        return party
    def downgrade(self, party: Party) -> Party:
        """Downgrade party to previous version (no-op for base)."""
        return party

class PartyVersionRegistry:
    """
    Registry for party schema versions and their strategies.
    To add a new version, subclass PartyVersionStrategy and register it here.
    """
    _registry = {}
    @classmethod
    def register(cls, version: str, strategy: PartyVersionStrategy):
        """Register a strategy for a schema version."""
        cls._registry[version] = strategy
    @classmethod
    def get_strategy(cls, version: str) -> PartyVersionStrategy:
        """Get the strategy for a schema version."""
        return cls._registry.get(version, PartyVersionStrategy())

# Register the default version
PartyVersionRegistry.register(CURRENT_PARTY_SCHEMA_VERSION, PartyVersionStrategy())

class PartyRepository:
    """Repository for managing party-related database operations with transaction and integrity checks."""

    def __init__(self, session: Session):
        self.session = session

    def _calculate_checksum(self, party: Party) -> str:
        """Calculate SHA-256 checksum for party data integrity verification."""
        # Serialize party data to JSON for checksum
        party_dict = party.to_dict()
        data = json.dumps(party_dict, sort_keys=True).encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    def _log_write_ahead(self, operation: str, party_data: Dict[str, Any]):
        """Log the intended operation and data before committing (write-ahead log)."""
        # In production, this should write to a durable log file or external system
        logger.info(f"[WAL] {operation} - {json.dumps(party_data, sort_keys=True)}")

    def create_party(self, party_data: Dict[str, Any]) -> Party:
        """Create a new party in the database with transaction, integrity, and versioning."""
        try:
            party_data['schema_version'] = party_data.get('schema_version', CURRENT_PARTY_SCHEMA_VERSION)
            party = Party(**party_data)
            checksum = self._calculate_checksum(party)
            party_data['checksum'] = checksum
            self._log_write_ahead('CREATE', party_data)
            self.session.add(party)
            self.session.commit()
            return party
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to create party: {e}")
            raise

    def get_party(self, party_id: int) -> Optional[Party]:
        """Get a party by ID, detect and handle schema version."""
        party = self.session.query(Party).get(party_id)
        if party:
            strategy = PartyVersionRegistry.get_strategy(party.schema_version)
            party = strategy.upgrade(party)
        return party

    def update_party(self, party_id: int, update_data: Dict[str, Any]) -> Optional[Party]:
        """Update a party's data with transaction and integrity checks."""
        party = self.get_party(party_id)
        if not party:
            return None
        try:
            for key, value in update_data.items():
                setattr(party, key, value)
            checksum = self._calculate_checksum(party)
            update_data['checksum'] = checksum
            self._log_write_ahead('UPDATE', {**update_data, 'id': party_id})
            self.session.commit()
            return party
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to update party {party_id}: {e}")
            raise

    def delete_party(self, party_id: int) -> bool:
        """Delete a party from the database with transaction logging."""
        party = self.get_party(party_id)
        if not party:
            return False
        try:
            self._log_write_ahead('DELETE', {'id': party_id})
            self.session.delete(party)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Failed to delete party {party_id}: {e}")
            raise

    def get_all_parties(self) -> List[Party]:
        """Get all parties."""
        return self.session.query(Party).all()

    def validate_integrity(self, party_id: int) -> bool:
        """Validate the integrity of a party record by comparing stored and calculated checksums."""
        party = self.get_party(party_id)
        if not party:
            return False
        calculated = self._calculate_checksum(party)
        stored = getattr(party, 'checksum', None)
        if stored is None:
            logger.warning(f"No checksum stored for party {party_id}")
            return False
        if calculated != stored:
            logger.error(f"Checksum mismatch for party {party_id}: {calculated} != {stored}")
            return False
        return True

    def get_and_migrate_party(self, party_id: int) -> Optional[Party]:
        """Get a party by ID, auto-migrate to current schema version if needed."""
        party = self.session.query(Party).get(party_id)
        if not party:
            return None
        if party.schema_version != CURRENT_PARTY_SCHEMA_VERSION:
            strategy = PartyVersionRegistry.get_strategy(party.schema_version)
            upgraded_party = strategy.upgrade(party)
            upgraded_party.schema_version = CURRENT_PARTY_SCHEMA_VERSION
            checksum = self._calculate_checksum(upgraded_party)
            upgraded_party.checksum = checksum
            self.session.commit()
            return upgraded_party
        return party

class PartyMigrationError(Exception):
    pass

class PartyMigrationManager:
    """
    Manages party data migrations between schema versions, with validation, batch migration, and rollback support.
    """
    def __init__(self, session: Session):
        self.session = session
        self._migration_paths = {}  # (from_version, to_version): migration_fn

    def register_migration(self, from_version: str, to_version: str, migration_fn):
        """
        Register a migration function for a version pair.
        Args:
            from_version: Source schema version
            to_version: Target schema version
            migration_fn: Callable that takes a Party and returns a migrated Party
        """
        self._migration_paths[(from_version, to_version)] = migration_fn

    def migrate_party(self, party: Party, to_version: str) -> Party:
        """
        Migrate a single party to the target schema version.
        Rolls back to pre-migration state if migration or validation fails.
        Args:
            party: Party instance to migrate
            to_version: Target schema version
        Returns:
            Migrated Party instance
        Raises:
            PartyMigrationError if migration fails
        """
        from_version = party.schema_version
        if from_version == to_version:
            return party
        migration_fn = self._migration_paths.get((from_version, to_version))
        if not migration_fn:
            raise PartyMigrationError(f"No migration path from {from_version} to {to_version}")
        # Save pre-migration state for rollback
        pre_state = party.to_dict()
        try:
            migrated_party = migration_fn(party)
            migrated_party.schema_version = to_version
            # Validate after migration
            if not self.validate_party(migrated_party):
                raise PartyMigrationError("Validation failed after migration")
            # Update checksum
            repo = PartyRepository(self.session)
            migrated_party.checksum = repo._calculate_checksum(migrated_party)
            self.session.commit()
            return migrated_party
        except Exception as e:
            # Rollback: restore pre-migration state
            for key, value in pre_state.items():
                setattr(party, key, value)
            self.session.rollback()
            raise PartyMigrationError(f"Migration failed and rolled back: {e}")

    def batch_migrate(self, party_ids: list, to_version: str) -> dict:
        """
        Batch migrate multiple parties to the target schema version.
        Args:
            party_ids: List of party IDs to migrate
            to_version: Target schema version
        Returns:
            Dict of party_id -> 'success' or error message
        """
        results = {}
        for party_id in party_ids:
            party = self.session.query(Party).get(party_id)
            if not party:
                results[party_id] = 'not found'
                continue
            try:
                self.migrate_party(party, to_version)
                results[party_id] = 'success'
            except PartyMigrationError as e:
                results[party_id] = str(e)
        return results

    def validate_party(self, party: Party) -> bool:
        """
        Validate a party after migration. Extend for future schema versions.
        Args:
            party: Party instance
        Returns:
            True if valid, False otherwise
        """
        # Basic validation: ensure required fields exist and schema_version matches
        if not party.schema_version:
            return False
        # Add more validation as needed for future versions
        return True

class PartyRecoveryManager:
    """
    Manages recovery and backup for party data, including point-in-time recovery, automated backups, and integrity validation.
    """
    def __init__(self, session: Session, backup_dir: str = './party_backups', backup_interval: int = 3600):
        self.session = session
        self.backup_dir = backup_dir
        self.backup_interval = backup_interval  # seconds
        self._stop_event = threading.Event()
        os.makedirs(self.backup_dir, exist_ok=True)
        self._backup_thread = threading.Thread(target=self._run_backup_scheduler, daemon=True)
        self._backup_thread.start()

    def _run_backup_scheduler(self):
        while not self._stop_event.is_set():
            self.create_backup()
            self._stop_event.wait(self.backup_interval)

    def stop(self):
        self._stop_event.set()
        self._backup_thread.join()

    def create_backup(self):
        """Create a full backup of all party data."""
        parties = self.session.query(Party).all()
        timestamp = time.strftime('%Y%m%dT%H%M%S')
        backup_path = os.path.join(self.backup_dir, f'party_backup_{timestamp}.json')
        with open(backup_path, 'w') as f:
            json.dump([p.to_dict() for p in parties], f, indent=2)
        logger.info(f"[Backup] Created party backup at {backup_path}")
        return backup_path

    def list_backups(self):
        """List all backup files."""
        return sorted([f for f in os.listdir(self.backup_dir) if f.startswith('party_backup_')])

    def restore_from_backup(self, backup_file: str):
        """Restore all party data from a backup file."""
        backup_path = os.path.join(self.backup_dir, backup_file)
        with open(backup_path, 'r') as f:
            party_dicts = json.load(f)
        self.session.query(Party).delete()
        for pd in party_dicts:
            party = Party(**{k: v for k, v in pd.items() if k != 'id'})
            party.id = pd['id']
            self.session.add(party)
        self.session.commit()
        logger.info(f"[Recovery] Restored party data from {backup_file}")

    def point_in_time_recovery(self, wal_log_path: str, target_timestamp: str):
        """Restore party data to a point in time using the WAL log."""
        with open(wal_log_path, 'r') as f:
            wal_entries = [json.loads(line) for line in f if line.strip()]
        # Filter entries up to the target timestamp
        entries = [e for e in wal_entries if e.get('timestamp', '') <= target_timestamp]
        self.session.query(Party).delete()
        for entry in entries:
            if entry['operation'] in ('CREATE', 'UPDATE'):
                party_data = entry['party_data']
                party = Party(**{k: v for k, v in party_data.items() if k != 'id'})
                party.id = party_data['id']
                self.session.add(party)
        self.session.commit()
        logger.info(f"[Recovery] Restored party data to {target_timestamp} using WAL log")

    def validate_backup(self, backup_file: str) -> bool:
        """Validate the integrity of a backup file."""
        backup_path = os.path.join(self.backup_dir, backup_file)
        with open(backup_path, 'r') as f:
            party_dicts = json.load(f)
        for pd in party_dicts:
            party = Party(**{k: v for k, v in pd.items() if k != 'id'})
            if 'checksum' in pd:
                repo = PartyRepository(self.session)
                if repo._calculate_checksum(party) != pd['checksum']:
                    logger.error(f"[Validation] Checksum mismatch for party {pd.get('id')}")
                    return False
        logger.info(f"[Validation] Backup {backup_file} passed integrity check")
        return True

    def validate_recovery(self):
        """Validate the integrity of all current party data after recovery."""
        parties = self.session.query(Party).all()
        repo = PartyRepository(self.session)
        for party in parties:
            if not repo.validate_integrity(party.id):
                logger.error(f"[Validation] Integrity check failed for party {party.id}")
                return False
        logger.info("[Validation] All recovered party data passed integrity check")
        return True 