"""
Change tracking system for world state modifications.

This module provides functionality for tracking, logging, and auditing changes to the world state,
enabling comprehensive change history and analysis.
"""

import uuid
import json
import logging
from typing import Dict, List, Optional, Any, Set, Tuple, Callable
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from app.core.persistence.version_control import ChangeRecord

logger = logging.getLogger(__name__)

class ChangeType(str, Enum):
    """Types of changes that can be tracked."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    REVERT = "revert"
    SYSTEM = "system"

class ChangeCategory(str, Enum):
    """Categories of changes for organization."""
    WORLD = "world"
    REGION = "region"
    ENTITY = "entity"
    PLAYER = "player"
    NPC = "npc"
    ITEM = "item"
    QUEST = "quest"
    ENVIRONMENT = "environment"
    SYSTEM = "system"

@dataclass
class ChangeContext:
    """Context information for a change."""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    source: str = "unknown"
    cause: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ChangeTracker:
    """Tracks and logs changes to the world state."""
    
    def __init__(self):
        """Initialize the change tracker."""
        # List of all change records
        self.changes: List[ChangeRecord] = []
        
        # Recent changes cache (for frequent lookups)
        self.recent_changes: List[ChangeRecord] = []
        self.max_recent_changes = 1000
        
        # Entity modification tracking
        self.modified_entities: Dict[str, Dict[str, Set[str]]] = {}
        
        # Change listeners
        self.change_listeners: List[Callable[[ChangeRecord], None]] = []
        
        # Periodic flush to storage
        self.changes_since_flush = 0
        self.flush_threshold = 500
        
        # Stats
        self.stats = {
            "total_changes": 0,
            "changes_by_type": {},
            "changes_by_category": {},
            "changes_by_entity": {}
        }
    
    def track_change(
        self,
        change_type: ChangeType,
        entity_type: str,
        entity_id: str,
        field_name: Optional[str] = None,
        old_value: Any = None,
        new_value: Any = None,
        context: Optional[ChangeContext] = None
    ) -> ChangeRecord:
        """
        Track a change to the world state.
        
        Args:
            change_type: Type of change
            entity_type: Type of entity being changed
            entity_id: ID of entity being changed
            field_name: Field being changed (if applicable)
            old_value: Old value (if applicable)
            new_value: New value (if applicable)
            context: Change context information
            
        Returns:
            The created change record
        """
        if context is None:
            context = ChangeContext()
        
        # Create change record
        change_id = str(uuid.uuid4())
        change = ChangeRecord(
            timestamp=context.timestamp,
            change_type=change_type,
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            change_id=change_id,
            metadata={
                "user_id": context.user_id,
                "session_id": context.session_id,
                "source": context.source,
                "cause": context.cause,
                **context.metadata
            }
        )
        
        # Add to changes list
        self.changes.append(change)
        
        # Add to recent changes cache
        self.recent_changes.append(change)
        if len(self.recent_changes) > self.max_recent_changes:
            self.recent_changes.pop(0)
        
        # Track modified entity
        self._track_modified_entity(entity_type, entity_id, field_name)
        
        # Notify listeners
        for listener in self.change_listeners:
            try:
                listener(change)
            except Exception as e:
                logger.error(f"Error in change listener: {e}")
        
        # Update stats
        self.stats["total_changes"] += 1
        self.stats["changes_by_type"][change_type] = self.stats["changes_by_type"].get(change_type, 0) + 1
        self.stats["changes_by_category"][entity_type] = self.stats["changes_by_category"].get(entity_type, 0) + 1
        entity_key = f"{entity_type}:{entity_id}"
        self.stats["changes_by_entity"][entity_key] = self.stats["changes_by_entity"].get(entity_key, 0) + 1
        
        # Check if we should flush to storage
        self.changes_since_flush += 1
        if self.changes_since_flush >= self.flush_threshold:
            self.flush()
        
        return change
    
    def _track_modified_entity(self, entity_type: str, entity_id: str, field_name: Optional[str] = None) -> None:
        """Track a modified entity for efficient lookup."""
        if entity_type not in self.modified_entities:
            self.modified_entities[entity_type] = {}
        
        if entity_id not in self.modified_entities[entity_type]:
            self.modified_entities[entity_type][entity_id] = set()
        
        if field_name:
            self.modified_entities[entity_type][entity_id].add(field_name)
    
    def get_changes_for_entity(
        self,
        entity_type: str,
        entity_id: str,
        field_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ChangeRecord]:
        """
        Get changes for a specific entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            field_name: Field to filter by (optional)
            limit: Maximum number of changes to return
            offset: Offset for pagination
            
        Returns:
            List of change records
        """
        # Filter changes by entity type and ID
        filtered_changes = [
            change for change in self.changes
            if change.entity_type == entity_type and change.entity_id == entity_id
        ]
        
        # Further filter by field name if provided
        if field_name:
            filtered_changes = [
                change for change in filtered_changes
                if change.field_name == field_name
            ]
        
        # Sort by timestamp (newest first)
        filtered_changes.sort(key=lambda c: c.timestamp, reverse=True)
        
        # Apply pagination
        return filtered_changes[offset:offset+limit]
    
    def get_recent_changes(self, limit: int = 100, offset: int = 0) -> List[ChangeRecord]:
        """
        Get recent changes.
        
        Args:
            limit: Maximum number of changes to return
            offset: Offset for pagination
            
        Returns:
            List of change records
        """
        # Recent changes are already sorted by timestamp (newest first)
        # due to how we add them to the cache
        return self.recent_changes[::-1][offset:offset+limit]
    
    def get_changes_by_type(self, change_type: ChangeType, limit: int = 100, offset: int = 0) -> List[ChangeRecord]:
        """
        Get changes of a specific type.
        
        Args:
            change_type: Type of changes to get
            limit: Maximum number of changes to return
            offset: Offset for pagination
            
        Returns:
            List of change records
        """
        # Filter changes by type
        filtered_changes = [
            change for change in self.changes
            if change.change_type == change_type
        ]
        
        # Sort by timestamp (newest first)
        filtered_changes.sort(key=lambda c: c.timestamp, reverse=True)
        
        # Apply pagination
        return filtered_changes[offset:offset+limit]
    
    def add_change_listener(self, listener: Callable[[ChangeRecord], None]) -> None:
        """
        Add a listener to be notified of changes.
        
        Args:
            listener: Function to call when a change occurs
        """
        self.change_listeners.append(listener)
    
    def remove_change_listener(self, listener: Callable[[ChangeRecord], None]) -> None:
        """
        Remove a change listener.
        
        Args:
            listener: Listener to remove
        """
        if listener in self.change_listeners:
            self.change_listeners.remove(listener)
    
    def has_entity_been_modified(self, entity_type: str, entity_id: str, field_name: Optional[str] = None) -> bool:
        """
        Check if an entity has been modified.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            field_name: Field to check (optional)
            
        Returns:
            True if the entity has been modified, False otherwise
        """
        if entity_type not in self.modified_entities:
            return False
        
        if entity_id not in self.modified_entities[entity_type]:
            return False
        
        if field_name:
            return field_name in self.modified_entities[entity_type][entity_id]
        
        return True
    
    def get_modified_entities(self, entity_type: Optional[str] = None) -> Dict[str, Dict[str, Set[str]]]:
        """
        Get all modified entities.
        
        Args:
            entity_type: Type of entities to get (optional)
            
        Returns:
            Dictionary of modified entities
        """
        if entity_type:
            return {entity_type: self.modified_entities.get(entity_type, {})}
        
        return self.modified_entities
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get change tracking statistics.
        
        Returns:
            Dictionary of statistics
        """
        return self.stats
    
    def clear(self) -> None:
        """Clear all tracked changes."""
        self.changes.clear()
        self.recent_changes.clear()
        self.modified_entities.clear()
        self.changes_since_flush = 0
        self.stats = {
            "total_changes": 0,
            "changes_by_type": {},
            "changes_by_category": {},
            "changes_by_entity": {}
        }
        logger.info("Cleared all tracked changes")
    
    def flush(self) -> None:
        """Flush changes to persistent storage (to be implemented by subclasses)."""
        self.changes_since_flush = 0
        # This is a placeholder for actual persistence logic
        logger.debug(f"Flushed {self.changes_since_flush} changes to storage")
    
    def export_changes(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Export changes for a time period.
        
        Args:
            start_time: Start timestamp (ISO format)
            end_time: End timestamp (ISO format)
            
        Returns:
            List of change dictionaries
        """
        filtered_changes = self.changes
        
        # Filter by start time
        if start_time:
            filtered_changes = [
                change for change in filtered_changes
                if change.timestamp >= start_time
            ]
        
        # Filter by end time
        if end_time:
            filtered_changes = [
                change for change in filtered_changes
                if change.timestamp <= end_time
            ]
        
        # Convert to dictionaries
        return [change.to_dict() for change in filtered_changes]
    
    def import_changes(self, changes: List[Dict[str, Any]]) -> int:
        """
        Import changes from a list of dictionaries.
        
        Args:
            changes: List of change dictionaries
            
        Returns:
            Number of changes imported
        """
        imported = 0
        for change_dict in changes:
            change = ChangeRecord.from_dict(change_dict)
            self.changes.append(change)
            self._track_modified_entity(change.entity_type, change.entity_id, change.field_name)
            imported += 1
        
        logger.info(f"Imported {imported} changes")
        return imported 