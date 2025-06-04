"""
World State File Loader Module - Technical Infrastructure

Handles loading, validating, and migrating world state data from disk.
Provides functions for loading different aspects of world state,
including core state, events, and configuration.

Enhanced with modern features:
- Batch operations for better performance
- Compression support for large states
- Improved error handling and recovery
- Caching for frequently accessed data
"""
import os
import json
import logging
import gzip
import pickle
from typing import Dict, Any, Optional, Tuple, List, Union
from datetime import datetime, timedelta
import shutil
from pathlib import Path
from functools import lru_cache

from backend.infrastructure.utils import ensure_directory, safe_write_json

logger = logging.getLogger(__name__)

class WorldStateLoader:
    """Handles loading and persisting world state data with enhanced performance and reliability."""
    
    def __init__(self, data_dir: str = "data/systems/world_state", enable_compression: bool = True, cache_size: int = 128):
        self.data_dir = Path(data_dir)
        self.state_file = self.data_dir / "state.json"
        self.compressed_state_file = self.data_dir / "state.json.gz"
        self.events_dir = self.data_dir / "events"
        self.history_dir = self.data_dir / "history"
        self.backup_dir = self.data_dir / "backups"
        self.cache_dir = self.data_dir / "cache"
        
        self.enable_compression = enable_compression
        self.cache_size = cache_size
        self._state_cache: Optional[Dict[str, Any]] = None
        self._cache_timestamp: Optional[datetime] = None
        self._cache_ttl = timedelta(minutes=5)  # Cache TTL
        
        # Ensure directories exist
        for directory in [self.data_dir, self.events_dir, self.history_dir, 
                         self.backup_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def load_state(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load the current world state from disk with caching support.
        
        Args:
            use_cache: Whether to use cached state if available
        
        Returns:
            The loaded world state or an empty state if none exists
        """
        # Check cache first
        if use_cache and self._is_cache_valid():
            logger.debug("Using cached world state")
            return self._state_cache.copy()
        
        # Determine which file to load from
        state_file_to_use = None
        if self.enable_compression and self.compressed_state_file.exists():
            state_file_to_use = self.compressed_state_file
            load_func = self._load_compressed_state
        elif self.state_file.exists():
            state_file_to_use = self.state_file
            load_func = self._load_uncompressed_state
        
        if not state_file_to_use:
            logger.info("No state file found, creating new empty state")
            state = self._create_empty_state()
            self._update_cache(state)
            return state
        
        try:
            state = load_func(state_file_to_use)
            
            # Validate the loaded state
            if not self._validate_state(state):
                logger.warning("Loaded state failed validation, creating backup and using empty state")
                self._backup_state(state)
                state = self._create_empty_state()
            else:
                # Migrate if needed
                state = self._migrate_state_if_needed(state)
            
            # Update cache
            self._update_cache(state)
            return state
            
        except Exception as e:
            logger.error(f"Error loading world state: {str(e)}")
            
            # Create backup of corrupted file if it exists
            if state_file_to_use.exists():
                try:
                    backup_path = self.backup_dir / f"corrupted_state_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{state_file_to_use.suffix}"
                    shutil.copy2(state_file_to_use, backup_path)
                    logger.info(f"Created backup of corrupted state at {backup_path}")
                except Exception as backup_error:
                    logger.error(f"Failed to create backup of corrupted state: {str(backup_error)}")
            
            state = self._create_empty_state()
            self._update_cache(state)
            return state
    
    def load_events_batch(self, 
                         event_ids: List[str] = None,
                         event_type: Optional[str] = None, 
                         category: Optional[str] = None,
                         region: Optional[str] = None,
                         since: Optional[datetime] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """
        Load events in batch with enhanced filtering options.
        
        Args:
            event_ids: Specific event IDs to load
            event_type: Optional event type filter
            category: Optional category filter
            region: Optional region filter
            since: Optional datetime filter (events after this time)
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        events = []
        
        try:
            if event_ids:
                # Load specific events by ID
                for event_id in event_ids:
                    event = self.load_event(event_id)
                    if event:
                        events.append(event)
                return events[:limit]
            
            # Get all event files
            event_files = list(self.events_dir.glob('*.json'))
            
            # Sort by modification time (newest first) for efficiency
            event_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Process files with filters
            for event_file in event_files:
                if len(events) >= limit:
                    break
                    
                try:
                    with open(event_file, 'r') as f:
                        event = json.load(f)
                    
                    # Apply filters
                    if not self._event_matches_filters(event, event_type, category, region, since):
                        continue
                    
                    events.append(event)
                    
                except Exception as e:
                    logger.error(f"Error loading event file {event_file}: {str(e)}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"Error loading events batch: {str(e)}")
            return []
    
    def save_state_compressed(self, state: Dict[str, Any]) -> bool:
        """
        Save world state with optional compression.
        
        Args:
            state: The world state to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Update metadata
            state["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            
            # Create backup before saving
            if self.state_file.exists() or self.compressed_state_file.exists():
                self._backup_state()
            
            success = False
            
            if self.enable_compression:
                # Save compressed version
                success = self._save_compressed_state(state)
                if success:
                    # Remove uncompressed version if it exists
                    if self.state_file.exists():
                        self.state_file.unlink()
            
            if not success:
                # Fallback to uncompressed
                success = safe_write_json(str(self.state_file), state)
            
            if success:
                # Update cache
                self._update_cache(state)
                logger.info("World state saved successfully")
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving world state: {str(e)}")
            return False
    
    def save_events_batch(self, events: List[Dict[str, Any]]) -> bool:
        """
        Save multiple events in batch for better performance.
        
        Args:
            events: List of events to save
            
        Returns:
            True if all events saved successfully, False otherwise
        """
        try:
            success_count = 0
            
            for event in events:
                if self.save_event(event):
                    success_count += 1
                else:
                    logger.warning(f"Failed to save event: {event.get('id', 'unknown')}")
            
            logger.info(f"Saved {success_count}/{len(events)} events in batch")
            return success_count == len(events)
            
        except Exception as e:
            logger.error(f"Error saving events batch: {str(e)}")
            return False
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """
        Clean up old backup files to manage disk space.
        
        Args:
            keep_days: Number of days of backups to keep
            
        Returns:
            Number of backup files removed
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=keep_days)
            removed_count = 0
            
            for backup_file in self.backup_dir.glob('*.json*'):
                try:
                    file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_time < cutoff_time:
                        backup_file.unlink()
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"Error processing backup file {backup_file}: {str(e)}")
            
            logger.info(f"Cleaned up {removed_count} old backup files")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up backups: {str(e)}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get statistics about world state storage usage.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            stats = {
                'state_file_size': 0,
                'events_count': 0,
                'events_total_size': 0,
                'backups_count': 0,
                'backups_total_size': 0,
                'total_storage_mb': 0
            }
            
            # State file size
            if self.state_file.exists():
                stats['state_file_size'] = self.state_file.stat().st_size
            elif self.compressed_state_file.exists():
                stats['state_file_size'] = self.compressed_state_file.stat().st_size
            
            # Events statistics
            for event_file in self.events_dir.glob('*.json'):
                stats['events_count'] += 1
                stats['events_total_size'] += event_file.stat().st_size
            
            # Backups statistics
            for backup_file in self.backup_dir.glob('*.json*'):
                stats['backups_count'] += 1
                stats['backups_total_size'] += backup_file.stat().st_size
            
            # Total storage
            total_bytes = stats['state_file_size'] + stats['events_total_size'] + stats['backups_total_size']
            stats['total_storage_mb'] = round(total_bytes / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {}
    
    def _load_compressed_state(self, file_path: Path) -> Dict[str, Any]:
        """Load state from compressed file"""
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_uncompressed_state(self, file_path: Path) -> Dict[str, Any]:
        """Load state from uncompressed file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_compressed_state(self, state: Dict[str, Any]) -> bool:
        """Save state to compressed file"""
        try:
            with gzip.open(self.compressed_state_file, 'wt', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Error saving compressed state: {str(e)}")
            return False
    
    def _is_cache_valid(self) -> bool:
        """Check if the cached state is still valid"""
        if not self._state_cache or not self._cache_timestamp:
            return False
        
        return datetime.utcnow() - self._cache_timestamp < self._cache_ttl
    
    def _update_cache(self, state: Dict[str, Any]):
        """Update the state cache"""
        self._state_cache = state.copy()
        self._cache_timestamp = datetime.utcnow()
    
    def _event_matches_filters(self, 
                             event: Dict[str, Any], 
                             event_type: Optional[str],
                             category: Optional[str],
                             region: Optional[str],
                             since: Optional[datetime]) -> bool:
        """Check if an event matches the given filters"""
        # Event type filter
        if event_type and event.get("type") != event_type:
            return False
        
        # Category filter
        if category:
            event_category = event.get("category")
            if not event_category or event_category != category:
                return False
        
        # Region filter
        if region:
            event_region = event.get("region")
            if not event_region or event_region != region:
                return False
        
        # Time filter
        if since:
            event_time_str = event.get("timestamp")
            if event_time_str:
                try:
                    event_time = datetime.fromisoformat(event_time_str.replace('Z', '+00:00'))
                    if event_time < since:
                        return False
                except (ValueError, TypeError):
                    # If we can't parse the timestamp, include the event
                    pass
        
        return True
    
    def invalidate_cache(self):
        """Manually invalidate the state cache"""
        self._state_cache = None
        self._cache_timestamp = None
    
    def load_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific event by ID.
        
        Args:
            event_id: The ID of the event to load
            
        Returns:
            The event data or None if not found
        """
        event_path = self.events_dir / f"{event_id}.json"
        
        if not event_path.exists():
            logger.warning(f"Event {event_id} not found at {event_path}")
            return None
        
        try:
            with open(event_path, 'r') as f:
                event = json.load(f)
                
            return event
            
        except Exception as e:
            logger.error(f"Error loading event {event_id}: {str(e)}")
            return None
    
    def load_events(self, 
                   event_type: Optional[str] = None, 
                   category: Optional[str] = None,
                   region: Optional[str] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Load events with optional filtering (backward compatibility).
        
        Args:
            event_type: Optional event type filter
            category: Optional category filter
            region: Optional region filter
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        return self.load_events_batch(
            event_type=event_type,
            category=category,
            region=region,
            limit=limit
        )
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """
        Save world state (backward compatibility).
        
        Args:
            state: The world state to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        return self.save_state_compressed(state)
    
    def save_event(self, event: Dict[str, Any]) -> bool:
        """
        Save an event to disk.
        
        Args:
            event: The event to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Ensure the event has an ID
            if "id" not in event:
                event_id = f"event_{int(datetime.utcnow().timestamp())}"
                event["id"] = event_id
            else:
                event_id = event["id"]
            
            # Ensure the event has a timestamp
            if "timestamp" not in event:
                event["timestamp"] = datetime.utcnow().isoformat()
            
            # Save the event
            event_path = self.events_dir / f"{event_id}.json"
            return safe_write_json(event_path, event)
            
        except Exception as e:
            logger.error(f"Error saving event: {str(e)}")
            return False
    
    def load_history(self, key: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Load history for a specific state key.
        
        Args:
            key: The state key to get history for
            limit: Maximum number of history entries to return
            
        Returns:
            List of historical values and timestamps
        """
        history_file = self.history_dir / f"{key.replace('.', '_')}.json"
        
        if not history_file.exists():
            return []
        
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Sort by timestamp (descending) and limit
            sorted_history = sorted(
                history, 
                key=lambda x: x.get("timestamp", ""), 
                reverse=True
            )[:limit]
            
            return sorted_history
            
        except Exception as e:
            logger.error(f"Error loading history for key {key}: {str(e)}")
            return []
    
    def load_all_history(self, 
                        keys: Optional[List[str]] = None, 
                        since: Optional[str] = None,
                        limit: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load history for multiple state keys.
        
        Args:
            keys: Optional list of keys to get history for (all if None)
            since: Optional timestamp to get history since
            limit: Maximum number of history entries per key
            
        Returns:
            Dictionary mapping keys to their history lists
        """
        result = {}
        
        try:
            # Get all history files
            if keys:
                # Only load specific keys
                history_files = [
                    f"{key.replace('.', '_')}.json" for key in keys
                ]
                # Filter to existing files
                history_files = [
                    f for f in history_files 
                    if history_file.exists()
                ]
            else:
                # Load all history files
                history_files = [
                    f for f in self.history_dir.glob('*.json')
                ]
            
            # Process each file
            for filename in history_files:
                key = filename.stem.replace('_', '.')
                
                try:
                    with open(filename, 'r') as f:
                        history = json.load(f)
                    
                    # Filter by timestamp if needed
                    if since:
                        history = [
                            entry for entry in history 
                            if entry.get("timestamp", "") >= since
                        ]
                    
                    # Sort by timestamp (descending) and limit
                    sorted_history = sorted(
                        history, 
                        key=lambda x: x.get("timestamp", ""), 
                        reverse=True
                    )[:limit]
                    
                    result[key] = sorted_history
                    
                except Exception as e:
                    logger.error(f"Error loading history file {filename}: {str(e)}")
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"Error loading history: {str(e)}")
            return {}
    
    def save_history_entry(self, key: str, value: Any, metadata: Dict[str, Any]) -> bool:
        """
        Save a history entry for a state key.
        
        Args:
            key: The state key
            value: The new value
            metadata: Additional metadata for the history entry
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Construct the history entry
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "value": value,
                **metadata
            }
            
            # Load existing history
            history_file = self.history_dir / f"{key.replace('.', '_')}.json"
            
            if history_file.exists():
                try:
                    with open(history_file, 'r') as f:
                        history = json.load(f)
                except:
                    history = []
            else:
                history = []
            
            # Add new entry
            history.append(entry)
            
            # Save the history
            return safe_write_json(history_file, history)
            
        except Exception as e:
            logger.error(f"Error saving history entry for key {key}: {str(e)}")
            return False
    
    def _create_empty_state(self) -> Dict[str, Any]:
        """
        Create a new empty world state.
        
        Returns:
            A minimal valid world state
        """
        return {
            "metadata": {
                "version": "1.0.0",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "last_tick": None
            },
            "regions": {},
            "factions": {},
            "npcs": {},
            "variables": {},
            "active_effects": []
        }
    
    def _validate_state(self, state: Dict[str, Any]) -> bool:
        """
        Validate a world state.
        
        Args:
            state: The state to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check for required top-level keys
        required_keys = ["metadata", "regions", "factions", "variables"]
        for key in required_keys:
            if key not in state:
                logger.error(f"World state missing required key: {key}")
                return False
        
        # Check metadata has required keys
        required_metadata = ["version", "created_at", "last_updated"]
        for key in required_metadata:
            if key not in state["metadata"]:
                logger.error(f"World state metadata missing required key: {key}")
                return False
        
        # Additional validation could be added here
        
        return True
    
    def _migrate_state_if_needed(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate a state to the latest version if needed.
        
        Args:
            state: The state to migrate
            
        Returns:
            The migrated state
        """
        version = state.get("metadata", {}).get("version", "0.0.0")
        
        # Example migration logic
        if version == "0.0.1":
            # Migrate from 0.0.1 to 0.0.2
            state = self._migrate_0_0_1_to_0_0_2(state)
            version = "0.0.2"
        
        if version == "0.0.2":
            # Migrate from 0.0.2 to 1.0.0
            state = self._migrate_0_0_2_to_1_0_0(state)
            version = "1.0.0"
        
        # Update version
        state["metadata"]["version"] = version
        
        return state
    
    def _migrate_0_0_1_to_0_0_2(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Example migration from version 0.0.1 to 0.0.2.
        
        Args:
            state: The state to migrate
            
        Returns:
            The migrated state
        """
        # Example migration logic
        if "npcs" not in state:
            state["npcs"] = {}
        
        return state
    
    def _migrate_0_0_2_to_1_0_0(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Example migration from version 0.0.2 to 1.0.0.
        
        Args:
            state: The state to migrate
            
        Returns:
            The migrated state
        """
        # Example migration logic
        if "active_effects" not in state:
            state["active_effects"] = []
        
        return state
    
    def _backup_state(self, state: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a backup of the current state.
        
        Args:
            state: Optional state to backup (loads from disk if None)
            
        Returns:
            True if backup created successfully, False otherwise
        """
        try:
            # Only backup if state file exists
            if not self.state_file.exists():
                return True
            
            # Generate backup filename with timestamp
            backup_file = self.backup_dir / f"state_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}{self.state_file.suffix}"
            
            # If state provided, write it directly
            if state is not None:
                return safe_write_json(backup_file, state)
            
            # Otherwise, copy the existing file
            shutil.copy2(self.state_file, backup_file)
            logger.info(f"Created state backup at {backup_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating state backup: {str(e)}")
            return False 