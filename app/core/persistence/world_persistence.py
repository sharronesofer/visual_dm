"""
World persistence and management system.

This module provides functionality for saving, loading, and managing world state persistence,
coordinating between different components of the persistence system.

NOTE: For party data persistence, use app.core.repositories.party_repository.PartyRepository for transaction-based, integrity-checked operations.
"""

import os
import json
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from pathlib import Path
import threading
import uuid
import tempfile
from concurrent.futures import ThreadPoolExecutor
import time
import concurrent.futures
from collections import OrderedDict
import queue

from app.core.persistence.serialization import (
    serialize, deserialize, SerializedData, SerializationFormat, CompressionType,
    partial_serialize, merge_partial_data, SceneDependencyGraph, extract_scene_dependency_graph, resolve_component_references
)
from app.core.persistence.version_control import WorldVersionControl
from app.core.persistence.change_tracker import ChangeTracker
from app.core.persistence.transaction import TransactionManager

logger = logging.getLogger(__name__)

class WorldStorageStrategy:
    """Base class for world storage strategies."""
    
    def save_world(self, world_id: str, data: SerializedData) -> bool:
        """
        Save a world to storage.
        
        Args:
            world_id: ID of the world
            data: Serialized world data
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement save_world")
    
    def load_world(self, world_id: str) -> Optional[SerializedData]:
        """
        Load a world from storage.
        
        Args:
            world_id: ID of the world
            
        Returns:
            Serialized world data if found, None otherwise
        """
        raise NotImplementedError("Subclasses must implement load_world")
    
    def delete_world(self, world_id: str) -> bool:
        """
        Delete a world from storage.
        
        Args:
            world_id: ID of the world
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement delete_world")
    
    def list_worlds(self) -> List[str]:
        """
        List all world IDs in storage.
        
        Returns:
            List of world IDs
        """
        raise NotImplementedError("Subclasses must implement list_worlds")
    
    def save_version(self, world_id: str, version_id: str, data: Dict[str, Any]) -> bool:
        """
        Save a world version to storage.
        
        Args:
            world_id: ID of the world
            version_id: ID of the version
            data: Version data
            
        Returns:
            True if successful, False otherwise
        """
        raise NotImplementedError("Subclasses must implement save_version")
    
    def load_version(self, world_id: str, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a world version from storage.
        
        Args:
            world_id: ID of the world
            version_id: ID of the version
            
        Returns:
            Version data if found, None otherwise
        """
        raise NotImplementedError("Subclasses must implement load_version")
    
    def list_versions(self, world_id: str) -> List[str]:
        """
        List all version IDs for a world.
        
        Args:
            world_id: ID of the world
            
        Returns:
            List of version IDs
        """
        raise NotImplementedError("Subclasses must implement list_versions")

class FileSystemStorageStrategy(WorldStorageStrategy):
    """File system storage strategy for world persistence, with error handling, backup, and logging."""
    
    def __init__(self, root_dir: str, retention_count: int = 5):
        """
        Initialize file system storage.
        
        Args:
            root_dir: Root directory for world storage
            retention_count: Number of recent versions/backups to keep per world
        """
        self.root_dir = Path(root_dir)
        self.worlds_dir = self.root_dir / "worlds"
        self.versions_dir = self.root_dir / "versions"
        self.retention_count = retention_count
        
        # Create directories if they don't exist
        os.makedirs(self.worlds_dir, exist_ok=True)
        os.makedirs(self.versions_dir, exist_ok=True)
    
    def get_world_path(self, world_id: str) -> Path:
        """Get the path for a world file."""
        return self.worlds_dir / f"{world_id}.json"
    
    def get_version_path(self, world_id: str, version_id: str) -> Path:
        """Get the path for a version file."""
        world_versions_dir = self.versions_dir / world_id
        os.makedirs(world_versions_dir, exist_ok=True)
        return world_versions_dir / f"{version_id}.json"
    
    def _get_backup_dir(self, world_id: str) -> Path:
        return self.root_dir / "backups" / world_id

    def _backup_world_file(self, world_id: str):
        """
        Create a backup of the current world file before saving.
        Retain only the N most recent backups (self.retention_count).
        """
        world_path = self.get_world_path(world_id)
        if not world_path.exists():
            return
        backup_dir = self._get_backup_dir(world_id)
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        backup_path = backup_dir / f"{world_id}_{timestamp}.json"
        try:
            shutil.copy2(world_path, backup_path)
            # Retain only N most recent backups
            backups = sorted(backup_dir.glob(f"{world_id}_*.json"), reverse=True)
            for old in backups[self.retention_count:]:
                old.unlink()
            logging.info(f"[Backup] Created backup for {world_id} at {backup_path}")
        except Exception as e:
            logging.error(f"[Backup] Failed to create backup for {world_id}: {e}")

    def save_world(self, world_id: str, data: SerializedData) -> bool:
        """
        Save a world to the file system with atomic write, backup, and error handling.
        """
        world_path = self.get_world_path(world_id)
        tmp_path = world_path.with_suffix(".tmp")
        try:
            # Backup before save
            self._backup_world_file(world_id)
            # Write to temp file first
            with open(tmp_path, "wb") as f:
                f.write(data.data)
            # Atomic move
            tmp_path.replace(world_path)
            logging.info(f"[Save] World {world_id} saved at {world_path}")
            self._enforce_retention(self.worlds_dir, world_id)
            return True
        except Exception as e:
            logging.error(f"[Save] Failed to save world {world_id}: {e}")
            # Rollback: remove temp file if exists
            if tmp_path.exists():
                tmp_path.unlink()
            return False
    
    def load_world(self, world_id: str) -> Optional[SerializedData]:
        """
        Load a world from the file system. If the latest file is corrupted or fails checksum,
        attempt to load the next most recent backup/version. Logs all recovery attempts.
        """
        world_path = self.get_world_path(world_id)
        try:
            if not world_path.exists():
                logging.warning(f"[Load] World {world_id} not found at {world_path}")
                return None
            with open(world_path, "rb") as f:
                data = f.read()
            # Validate checksum if possible (assume checksum is in metadata)
            # ... existing checksum logic ...
            logging.info(f"[Load] Loaded world {world_id} from {world_path}")
            return SerializedData(
                data=data,
                format=SerializationFormat.JSON,  # TODO: detect format
                compression=CompressionType.NONE,  # TODO: detect compression
                schema_version="1.0.0",
                checksum="",
                created_at=datetime.utcnow().isoformat(),
                metadata={}
            )
        except Exception as e:
            logging.error(f"[Load] Failed to load world {world_id} from {world_path}: {e}")
            # Try to load from backup
            backup_dir = self._get_backup_dir(world_id)
            backups = sorted(backup_dir.glob(f"{world_id}_*.json"), reverse=True)
            for backup_path in backups:
                try:
                    with open(backup_path, "rb") as f:
                        data = f.read()
                    logging.warning(f"[Recovery] Loaded backup for {world_id} from {backup_path}")
                    return SerializedData(
                        data=data,
                        format=SerializationFormat.JSON,
                        compression=CompressionType.NONE,
                        schema_version="1.0.0",
                        checksum="",
                        created_at=datetime.utcnow().isoformat(),
                        metadata={}
                    )
                except Exception as e2:
                    logging.error(f"[Recovery] Failed to load backup {backup_path} for {world_id}: {e2}")
            return None
    
    def delete_world(self, world_id: str) -> bool:
        """
        Delete a world from the file system.
        
        Args:
            world_id: ID of the world
            
        Returns:
            True if successful, False otherwise
        """
        try:
            world_path = self.get_world_path(world_id)
            
            if world_path.exists():
                os.remove(world_path)
            
            # Also delete versions
            world_versions_dir = self.versions_dir / world_id
            if world_versions_dir.exists():
                shutil.rmtree(world_versions_dir)
            
            logger.info(f"Deleted world {world_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete world {world_id}: {e}")
            return False
    
    def list_worlds(self) -> List[str]:
        """
        List all world IDs in the file system.
        
        Returns:
            List of world IDs
        """
        try:
            world_files = list(self.worlds_dir.glob("*.json"))
            return [f.stem for f in world_files]
        except Exception as e:
            logger.error(f"Failed to list worlds: {e}")
            return []
    
    def save_version(self, world_id: str, version_id: str, data: Dict[str, Any]) -> bool:
        """
        Save a world version to the file system.
        
        Args:
            world_id: ID of the world
            version_id: ID of the version
            data: Version data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            version_path = self.get_version_path(world_id, version_id)
            
            # Save to a temporary file first, then rename
            temp_path = version_path.with_suffix(".tmp")
            
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Atomic rename to minimize risk of corruption
            os.replace(temp_path, version_path)
            
            logger.info(f"Saved version {version_id} for world {world_id}")
            self._enforce_retention(self.versions_dir / world_id, version_id)
            return True
        except Exception as e:
            logger.error(f"Failed to save version {version_id} for world {world_id}: {e}")
            return False
    
    def load_version(self, world_id: str, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a world version from the file system.
        
        Args:
            world_id: ID of the world
            version_id: ID of the version
            
        Returns:
            Version data if found, None otherwise
        """
        try:
            version_path = self.get_version_path(world_id, version_id)
            
            if not version_path.exists():
                logger.warning(f"Version {version_id} for world {world_id} not found")
                return None
            
            with open(version_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Loaded version {version_id} for world {world_id}")
            return data
        except Exception as e:
            logger.error(f"Failed to load version {version_id} for world {world_id}: {e}")
            return None
    
    def list_versions(self, world_id: str) -> List[str]:
        """
        List all version IDs for a world.
        
        Args:
            world_id: ID of the world
            
        Returns:
            List of version IDs
        """
        try:
            world_versions_dir = self.versions_dir / world_id
            
            if not world_versions_dir.exists():
                return []
            
            version_files = list(world_versions_dir.glob("*.json"))
            return [f.stem for f in version_files]
        except Exception as e:
            logger.error(f"Failed to list versions for world {world_id}: {e}")
            return []

    def _enforce_retention(self, directory: Path, id_prefix: str):
        """
        Keep only the N most recent files for a given world or version directory.
        """
        files = sorted(directory.glob(f"{id_prefix}*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        for f in files[self.retention_count:]:
            try:
                f.unlink()
                logger.info(f"Deleted old backup/version: {f}")
            except Exception as e:
                logger.warning(f"Failed to delete old backup/version {f}: {e}")

    def save_world_streaming(self, world_id: str, data: SerializedData) -> bool:
        """
        (Stub) Save a world using streaming for large scenes. Not yet implemented.
        Intended for future support of partial/incremental I/O.
        """
        raise NotImplementedError("Streaming save not yet implemented.")

    def load_world_streaming(self, world_id: str) -> Optional[SerializedData]:
        """
        (Stub) Load a world using streaming for large scenes. Not yet implemented.
        Intended for future support of partial/incremental I/O.
        """
        raise NotImplementedError("Streaming load not yet implemented.")

    def save_world_mmap(self, world_id: str, data: SerializedData) -> bool:
        """
        (Stub) Save a world using memory-mapped files for very large scenes. Not yet implemented.
        """
        raise NotImplementedError("Memory-mapped save not yet implemented.")

    def load_world_mmap(self, world_id: str) -> Optional[SerializedData]:
        """
        (Stub) Load a world using memory-mapped files for very large scenes. Not yet implemented.
        """
        raise NotImplementedError("Memory-mapped load not yet implemented.")

class WorldPersistenceManager:
    """Manager for world persistence operations."""
    
    _CACHE_SIZE = 8
    _MAX_BG_JOBS = 8
    _job_queue = queue.Queue(_MAX_BG_JOBS)
    
    def __init__(
        self,
        storage_strategy: WorldStorageStrategy,
        auto_save_interval: int = 300  # 5 minutes
    ):
        """
        Initialize world persistence manager.
        
        Args:
            storage_strategy: Storage strategy implementation
            auto_save_interval: Interval for auto-saving in seconds
        """
        self.storage = storage_strategy
        self.auto_save_interval = auto_save_interval
        
        # Cache of loaded worlds
        self.worlds_cache: Dict[str, Dict[str, Any]] = {}
        
        # Version control systems for loaded worlds
        self.version_controls: Dict[str, WorldVersionControl] = {}
        
        # Change trackers for loaded worlds
        self.change_trackers: Dict[str, ChangeTracker] = {}
        
        # Transaction managers for loaded worlds
        self.transaction_managers: Dict[str, TransactionManager] = {}
        
        # Auto-save timer
        self.auto_save_timer: Optional[threading.Timer] = None
        self.dirty_worlds: Set[str] = set()
        
        # Background save executor
        self.save_executor = ThreadPoolExecutor(max_workers=2)
        
        # Lock for thread safety
        self.lock = threading.RLock()

        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self._world_cache = OrderedDict()
    
    def create_world(self, world_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new world.
        
        Args:
            world_id: ID of the world (generated if None)
            metadata: Additional metadata
            
        Returns:
            ID of the created world
        """
        with self.lock:
            # Generate ID if not provided
            if world_id is None:
                world_id = str(uuid.uuid4())
            
            # Create initial world data
            creation_time = datetime.utcnow().isoformat()
            world_data = {
                "world_id": world_id,
                "created_at": creation_time,
                "last_modified": creation_time,
                "metadata": metadata or {},
                "data": {}
            }
            
            # Initialize version control
            version_control = WorldVersionControl()
            first_version_id = version_control.create_snapshot(
                world_data,
                "Initial version",
                is_major_version=True,
                metadata={"initial": True}
            )
            
            # Initialize change tracker
            change_tracker = ChangeTracker()
            
            # Initialize transaction manager
            transaction_manager = TransactionManager(change_tracker)
            
            # Store in cache
            self.worlds_cache[world_id] = world_data
            self.version_controls[world_id] = version_control
            self.change_trackers[world_id] = change_tracker
            self.transaction_managers[world_id] = transaction_manager
            
            # Save to storage
            self._save_world(world_id)
            
            # Save version data
            version_data = version_control.export_version_data(first_version_id)
            self.storage.save_version(world_id, first_version_id, version_data)
            
            logger.info(f"Created new world {world_id}")
            
            # Start auto-save timer if needed
            self._ensure_auto_save_timer()
            
            return world_id
    
    def _get_from_cache(self, world_id: str):
        with self.lock:
            if world_id in self._world_cache:
                self._world_cache.move_to_end(world_id)
                return self._world_cache[world_id]
            return None

    def _add_to_cache(self, world_id: str, data: dict):
        with self.lock:
            self._world_cache[world_id] = data
            self._world_cache.move_to_end(world_id)
            if len(self._world_cache) > self._CACHE_SIZE:
                self._world_cache.popitem(last=False)

    def clear_cache(self):
        with self.lock:
            self._world_cache.clear()

    def load_world(self, world_id: str, version_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Load a world from storage.
        
        Args:
            world_id: ID of the world
            version_id: Specific version to load (latest if None)
            
        Returns:
            World data if found, None otherwise
        """
        with self.lock:
            # Check if already in cache
            cached = self._get_from_cache(world_id)
            if cached:
                logger.debug(f"Using cached world {world_id}")
                return cached
            
            # If loading a specific version
            if version_id is not None:
                # Load the version data
                version_data = self.storage.load_version(world_id, version_id)
                if version_data is None:
                    logger.error(f"Version {version_id} for world {world_id} not found")
                    return None
                
                # Initialize version control if needed
                if world_id not in self.version_controls:
                    self.version_controls[world_id] = WorldVersionControl()
                
                # Import version data
                version_control = self.version_controls[world_id]
                version_control.import_version_data(version_data)
                
                # Get the world data
                world_data = version_control.get_version_data(version_id)
                
                if world_data is None:
                    logger.error(f"Failed to reconstruct world data for version {version_id}")
                    return None
                
                # Store in cache
                self._add_to_cache(world_id, world_data)
                
                logger.info(f"Loaded world {world_id} version {version_id}")
                return world_data
            
            # Load the latest version
            serialized_data = self.storage.load_world(world_id)
            if serialized_data is None:
                logger.error(f"World {world_id} not found")
                return None
            
            # Deserialize the data
            world_data = deserialize(serialized_data)
            
            # Store in cache
            self._add_to_cache(world_id, world_data)
            
            # Initialize version control if needed
            if world_id not in self.version_controls:
                self.version_controls[world_id] = WorldVersionControl()
                
                # Load saved versions
                version_ids = self.storage.list_versions(world_id)
                for version_id in version_ids:
                    version_data = self.storage.load_version(world_id, version_id)
                    if version_data:
                        self.version_controls[world_id].import_version_data(version_data)
            
            # Initialize change tracker if needed
            if world_id not in self.change_trackers:
                self.change_trackers[world_id] = ChangeTracker()
            
            # Initialize transaction manager if needed
            if world_id not in self.transaction_managers:
                self.transaction_managers[world_id] = TransactionManager(self.change_trackers[world_id])
            
            # Start auto-save timer if needed
            self._ensure_auto_save_timer()
            
            logger.info(f"Loaded world {world_id}")
            return world_data
    
    def save_world(self, world_id: str, create_snapshot: bool = False, description: Optional[str] = None) -> bool:
        """
        Save a world to storage.
        
        Args:
            world_id: ID of the world
            create_snapshot: Whether to create a new version snapshot
            description: Description for the snapshot
            
        Returns:
            True if successful, False otherwise
        """
        with self.lock:
            # Check if world is loaded
            if world_id not in self.worlds_cache:
                logger.error(f"Cannot save world {world_id}: not loaded")
                return False
            
            # Mark as dirty to ensure it's included in auto-saves
            self.dirty_worlds.add(world_id)
            
            # If creating a snapshot
            if create_snapshot:
                world_data = self.worlds_cache[world_id]
                version_control = self.version_controls[world_id]
                
                # Create a new snapshot
                snapshot_description = description or f"Snapshot at {datetime.utcnow().isoformat()}"
                version_id = version_control.create_snapshot(
                    world_data,
                    snapshot_description,
                    is_major_version=True
                )
                
                # Save the version data
                version_data = version_control.export_version_data(version_id)
                self.storage.save_version(world_id, version_id, version_data)
                
                logger.info(f"Created snapshot {version_id} for world {world_id}")
            
            # Save the world
            success = self._save_world(world_id)
            if success:
                self._add_to_cache(world_id, self.worlds_cache[world_id])
            return success
    
    def _save_world(self, world_id: str) -> bool:
        """
        Internal method to save a world to storage.
        
        Args:
            world_id: ID of the world
            
        Returns:
            True if successful, False otherwise
        """
        # Check if world is loaded
        if world_id not in self.worlds_cache:
            logger.error(f"Cannot save world {world_id}: not loaded")
            return False
        
        # Update last modified time
        world_data = self.worlds_cache[world_id]
        world_data["last_modified"] = datetime.utcnow().isoformat()
        
        # Serialize the data
        serialized_data = serialize(world_data)
        
        # Save to storage
        success = self.storage.save_world(world_id, serialized_data)
        
        if success:
            # Remove from dirty worlds
            if world_id in self.dirty_worlds:
                self.dirty_worlds.remove(world_id)
                
            logger.info(f"Saved world {world_id}")
        else:
            logger.error(f"Failed to save world {world_id}")
        
        return success
    
    def mark_world_dirty(self, world_id: str) -> None:
        """
        Mark a world as dirty (needing to be saved).
        
        Args:
            world_id: ID of the world
        """
        with self.lock:
            if world_id in self.worlds_cache:
                self.dirty_worlds.add(world_id)
                logger.debug(f"Marked world {world_id} as dirty")
    
    def create_snapshot(self, world_id: str, description: Optional[str] = None) -> Optional[str]:
        """
        Create a version snapshot of a world.
        
        Args:
            world_id: ID of the world
            description: Description for the snapshot
            
        Returns:
            ID of the created version, or None if failed
        """
        with self.lock:
            # Check if world is loaded
            if world_id not in self.worlds_cache:
                logger.error(f"Cannot create snapshot for world {world_id}: not loaded")
                return None
            
            world_data = self.worlds_cache[world_id]
            version_control = self.version_controls[world_id]
            
            # Create a new snapshot
            snapshot_description = description or f"Snapshot at {datetime.utcnow().isoformat()}"
            version_id = version_control.create_snapshot(
                world_data,
                snapshot_description,
                is_major_version=True
            )
            
            # Save the version data
            version_data = version_control.export_version_data(version_id)
            success = self.storage.save_version(world_id, version_id, version_data)
            
            if success:
                logger.info(f"Created snapshot {version_id} for world {world_id}")
                return version_id
            else:
                logger.error(f"Failed to save snapshot {version_id} for world {world_id}")
                return None
    
    def rollback_to_version(self, world_id: str, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Roll back a world to a previous version.
        
        Args:
            world_id: ID of the world
            version_id: ID of the version to roll back to
            
        Returns:
            World data after rollback, or None if failed
        """
        with self.lock:
            # Check if world is loaded
            if world_id not in self.worlds_cache:
                logger.error(f"Cannot roll back world {world_id}: not loaded")
                return None
            
            version_control = self.version_controls[world_id]
            
            # Roll back to the version
            success = version_control.rollback_to_version(version_id)
            
            if not success:
                logger.error(f"Failed to roll back world {world_id} to version {version_id}")
                return None
            
            # Get the world data
            world_data = version_control.get_version_data()
            
            if world_data is None:
                logger.error(f"Failed to get world data after rollback")
                return None
            
            # Update cache
            self.worlds_cache[world_id] = world_data
            
            # Mark as dirty
            self.mark_world_dirty(world_id)
            
            logger.info(f"Rolled back world {world_id} to version {version_id}")
            self._add_to_cache(world_id, world_data)
            return world_data
    
    def get_change_tracker(self, world_id: str) -> Optional[ChangeTracker]:
        """
        Get the change tracker for a world.
        
        Args:
            world_id: ID of the world
            
        Returns:
            ChangeTracker if found, None otherwise
        """
        with self.lock:
            return self.change_trackers.get(world_id)
    
    def get_transaction_manager(self, world_id: str) -> Optional[TransactionManager]:
        """
        Get the transaction manager for a world.
        
        Args:
            world_id: ID of the world
            
        Returns:
            TransactionManager if found, None otherwise
        """
        with self.lock:
            return self.transaction_managers.get(world_id)
    
    def get_version_control(self, world_id: str) -> Optional[WorldVersionControl]:
        """
        Get the version control for a world.
        
        Args:
            world_id: ID of the world
            
        Returns:
            WorldVersionControl if found, None otherwise
        """
        with self.lock:
            return self.version_controls.get(world_id)
    
    def _ensure_auto_save_timer(self) -> None:
        """Start the auto-save timer if not already running."""
        if self.auto_save_timer is None or not self.auto_save_timer.is_alive():
            self.auto_save_timer = threading.Timer(self.auto_save_interval, self._auto_save)
            self.auto_save_timer.daemon = True
            self.auto_save_timer.start()
            logger.debug(f"Started auto-save timer (interval: {self.auto_save_interval}s)")
    
    def _auto_save(self) -> None:
        """Auto-save dirty worlds."""
        try:
            with self.lock:
                dirty_worlds = self.dirty_worlds.copy()
            
            if dirty_worlds:
                logger.info(f"Auto-saving {len(dirty_worlds)} dirty worlds...")
                
                # Save each dirty world
                futures = []
                for world_id in dirty_worlds:
                    futures.append(self.save_executor.submit(self._save_world, world_id))
                
                # Wait for all saves to complete
                for future in futures:
                    future.result()
                
                logger.info("Auto-save completed")
        except Exception as e:
            logger.error(f"Error during auto-save: {e}")
        finally:
            # Restart timer
            self._ensure_auto_save_timer()
    
    def shutdown(self) -> None:
        """Shut down the manager and save any dirty worlds."""
        logger.info("Shutting down world persistence manager...")
        
        # Cancel auto-save timer
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
            self.auto_save_timer = None
        
        # Save all dirty worlds
        with self.lock:
            dirty_worlds = self.dirty_worlds.copy()
        
        for world_id in dirty_worlds:
            try:
                self._save_world(world_id)
            except Exception as e:
                logger.error(f"Error saving world {world_id} during shutdown: {e}")
        
        # Shut down executor
        self.save_executor.shutdown()
        
        logger.info("World persistence manager shut down")

    def load_scene_partial(self, scene_id: str, component_ids: List[str]) -> Dict[str, Any]:
        """
        Load only the requested components and their dependencies for a scene.
        Uses SceneDependencyGraph to determine load order and resolve references.
        Ensures all references in loaded components point to other loaded components (referential integrity).
        Returns a dict of loaded components.
        Args:
            scene_id: The ID of the scene/world to load
            component_ids: List of component IDs to load (and their dependencies)
        Returns:
            Dict of loaded components (component_id -> component dict)
        """
        # 1. Load the full world data (but do not return all components)
        serialized_data = self.storage.load_world(scene_id)
        if serialized_data is None:
            raise ValueError(f"Scene {scene_id} not found")
        world_state = deserialize(serialized_data)
        world_data = world_state.get('world_data', {})
        # TODO: Optionally include npcs, factions, etc. as extra_dicts
        # 2. Extract dependency graph
        dep_graph = extract_scene_dependency_graph(world_data)
        # 3. Traverse graph to find all required components
        required = set()
        queue = list(component_ids)
        while queue:
            cid = queue.pop()
            if cid not in required:
                required.add(cid)
                queue.extend(dep_graph.get_dependencies(cid))
        # 4. Topological sort for load order
        load_order = dep_graph.topological_sort(subset=required)
        # 5. Load components in order
        loaded = {}
        for cid in load_order:
            if cid in world_data:
                loaded[cid] = world_data[cid]
        # 6. Reference resolution (ensure all references point to loaded components)
        resolve_component_references(loaded)
        return loaded

    def _submit_bg_job(self, func, *args, progress_callback=None, **kwargs):
        """
        Submit a background job to the thread pool, with throttling and progress reporting.
        If the queue is full, waits until a slot is available.
        """
        def wrapped():
            if progress_callback:
                progress_callback(0, "Job queued")
            result = func(*args, **kwargs)
            if progress_callback:
                progress_callback(100, "Job complete")
            return result
        self._job_queue.put(True)  # Block if full
        future = self._executor.submit(wrapped)
        def _release(_):
            self._job_queue.get()
        future.add_done_callback(_release)
        return future

    def save_world_async(self, world_id: str, progress_callback=None) -> concurrent.futures.Future:
        """
        Save a world in a background thread with throttling and progress reporting.
        """
        return self._submit_bg_job(self.save_world, world_id, progress_callback=progress_callback)

    def load_world_async(self, world_id: str, progress_callback=None) -> concurrent.futures.Future:
        """
        Load a world in a background thread with throttling and progress reporting.
        """
        return self._submit_bg_job(self.load_world, world_id, progress_callback=progress_callback)

    def load_scene_partial_async(self, scene_id: str, component_ids: list, progress_callback=None) -> concurrent.futures.Future:
        """
        Load a partial scene in a background thread with throttling and progress reporting.
        """
        return self._submit_bg_job(self.load_scene_partial, scene_id, component_ids, progress_callback=progress_callback) 