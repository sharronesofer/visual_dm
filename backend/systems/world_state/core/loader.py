"""
World State Loader Module

Handles loading, validating, and migrating world state data from disk.
Provides functions for loading different aspects of world state,
including core state, events, and configuration.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import shutil

from backend.systems.world_state.core.types import WorldState, StateCategory, WorldRegion
from backend.infrastructure.utils import ensure_directory, safe_write_json

logger = logging.getLogger(__name__)

class WorldStateLoader:
    """Handles loading and persisting world state data."""
    
    def __init__(self, data_dir: str = "data/world_state"):
        self.data_dir = data_dir
        self.state_file = os.path.join(data_dir, "state.json")
        self.events_dir = os.path.join(data_dir, "events")
        self.history_dir = os.path.join(data_dir, "history")
        self.backup_dir = os.path.join(data_dir, "backups")
        
        # Ensure directories exist
        ensure_directory(self.data_dir)
        ensure_directory(self.events_dir)
        ensure_directory(self.history_dir)
        ensure_directory(self.backup_dir)
    
    def load_state(self) -> Dict[str, Any]:
        """
        Load the current world state from disk.
        
        Returns:
            The loaded world state or an empty state if none exists
        """
        if not os.path.exists(self.state_file):
            logger.info(f"No state file found at {self.state_file}, creating new empty state")
            return self._create_empty_state()
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            # Validate the loaded state
            if not self._validate_state(state):
                logger.warning("Loaded state failed validation, creating backup and using empty state")
                self._backup_state(state)
                return self._create_empty_state()
            
            # Migrate if needed
            state = self._migrate_state_if_needed(state)
            
            return state
            
        except Exception as e:
            logger.error(f"Error loading world state: {str(e)}")
            
            # If we already have a state file but it's corrupted,
            # create a backup before returning an empty state
            if os.path.exists(self.state_file):
                try:
                    with open(self.state_file, 'r') as f:
                        corrupted_data = f.read()
                    
                    backup_path = os.path.join(
                        self.backup_dir, 
                        f"corrupted_state_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                    )
                    
                    with open(backup_path, 'w') as f:
                        f.write(corrupted_data)
                        
                    logger.info(f"Created backup of corrupted state at {backup_path}")
                    
                except Exception as backup_error:
                    logger.error(f"Failed to create backup of corrupted state: {str(backup_error)}")
            
            return self._create_empty_state()
    
    def load_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a specific event by ID.
        
        Args:
            event_id: The ID of the event to load
            
        Returns:
            The event data or None if not found
        """
        event_path = os.path.join(self.events_dir, f"{event_id}.json")
        
        if not os.path.exists(event_path):
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
                   category: Optional[StateCategory] = None,
                   region: Optional[WorldRegion] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Load events with optional filtering.
        
        Args:
            event_type: Optional event type filter
            category: Optional category filter
            region: Optional region filter
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        events = []
        
        try:
            # Get all event files
            event_files = [f for f in os.listdir(self.events_dir) if f.endswith('.json')]
            
            # Process each file
            for i, filename in enumerate(sorted(event_files, reverse=True)):
                if i >= limit:
                    break
                    
                try:
                    with open(os.path.join(self.events_dir, filename), 'r') as f:
                        event = json.load(f)
                    
                    # Apply filters
                    if event_type and event.get("type") != event_type:
                        continue
                        
                    if category:
                        event_category = event.get("category")
                        if not event_category or event_category != category.name:
                            continue
                    
                    if region:
                        event_region = event.get("region")
                        if not event_region or event_region != region.name:
                            continue
                    
                    events.append(event)
                    
                except Exception as e:
                    logger.error(f"Error loading event file {filename}: {str(e)}")
                    continue
            
            return events
            
        except Exception as e:
            logger.error(f"Error loading events: {str(e)}")
            return []
    
    def load_history(self, key: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Load history for a specific state key.
        
        Args:
            key: The state key to get history for
            limit: Maximum number of history entries to return
            
        Returns:
            List of historical values and timestamps
        """
        history_file = os.path.join(self.history_dir, f"{key.replace('.', '_')}.json")
        
        if not os.path.exists(history_file):
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
                    if os.path.exists(os.path.join(self.history_dir, f))
                ]
            else:
                # Load all history files
                history_files = [
                    f for f in os.listdir(self.history_dir) 
                    if f.endswith('.json')
                ]
            
            # Process each file
            for filename in history_files:
                key = filename.replace('.json', '').replace('_', '.')
                
                try:
                    with open(os.path.join(self.history_dir, filename), 'r') as f:
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
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """
        Save the current world state to disk.
        
        Args:
            state: The world state to save
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Validate before saving
            if not self._validate_state(state):
                logger.error("Cannot save invalid state")
                return False
            
            # Create a backup before saving
            if os.path.exists(self.state_file):
                self._backup_state()
            
            # Save the state
            return safe_write_json(self.state_file, state)
            
        except Exception as e:
            logger.error(f"Error saving world state: {str(e)}")
            return False
    
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
            event_path = os.path.join(self.events_dir, f"{event_id}.json")
            return safe_write_json(event_path, event)
            
        except Exception as e:
            logger.error(f"Error saving event: {str(e)}")
            return False
    
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
            history_file = os.path.join(self.history_dir, f"{key.replace('.', '_')}.json")
            
            if os.path.exists(history_file):
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
            if not os.path.exists(self.state_file):
                return True
            
            # Generate backup filename with timestamp
            backup_file = os.path.join(
                self.backup_dir, 
                f"state_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
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