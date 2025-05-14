"""
World version control system.

This module provides a comprehensive version control system for world states,
allowing for tracking changes, creating snapshots, and rolling back to previous versions.
"""

import uuid
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
import json
import logging
from dataclasses import dataclass, field, asdict
from app.core.persistence.serialization import SerializedData, serialize, deserialize

logger = logging.getLogger(__name__)

@dataclass
class ChangeRecord:
    """Record of a change to the world state."""
    timestamp: str
    change_type: str  # "create", "update", "delete"
    entity_type: str
    entity_id: str
    field_name: Optional[str] = None
    old_value: Any = None
    new_value: Any = None
    change_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeRecord':
        """Create from dictionary."""
        return cls(**data)

@dataclass
class WorldVersion:
    """Represents a version of the world state."""
    version_id: str
    timestamp: str
    description: str
    major_version: int
    minor_version: int
    patch_version: int
    parent_version_id: Optional[str] = None
    full_data_id: Optional[str] = None
    changes_since_parent: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldVersion':
        """Create from dictionary."""
        return cls(**data)
    
    def get_version_string(self) -> str:
        """Get the version number as a string."""
        return f"{self.major_version}.{self.minor_version}.{self.patch_version}"

class WorldVersionControl:
    """Manages versioning for world states."""
    
    def __init__(self):
        """Initialize the version control system."""
        # Dictionary of version_id -> WorldVersion
        self.versions: Dict[str, WorldVersion] = {}
        
        # Dictionary of version_id -> SerializedData for full snapshots
        self.full_snapshots: Dict[str, SerializedData] = {}
        
        # Dictionary of change_id -> ChangeRecord
        self.changes: Dict[str, ChangeRecord] = {}
        
        # Current active version
        self.current_version_id: Optional[str] = None
        
        # Version branch history (for visualizing history)
        self.version_history: Dict[str, List[str]] = {}
        
        # Initialize with a root version if empty
        self._init_if_needed()
    
    def _init_if_needed(self) -> None:
        """Initialize with a root version if no versions exist."""
        if not self.versions:
            timestamp = datetime.utcnow().isoformat()
            version_id = str(uuid.uuid4())
            
            # Create the initial version
            initial_version = WorldVersion(
                version_id=version_id,
                timestamp=timestamp,
                description="Initial version",
                major_version=1,
                minor_version=0,
                patch_version=0,
                parent_version_id=None,
                full_data_id=None,
                changes_since_parent=[],
                metadata={"initial": True}
            )
            
            # Add to versions dictionary
            self.versions[version_id] = initial_version
            self.current_version_id = version_id
            
            # Initialize version history
            self.version_history[version_id] = []
            
            logger.info(f"Initialized version control with root version: {version_id}")
    
    def create_snapshot(
        self,
        world_data: Dict[str, Any],
        description: str,
        is_major_version: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new version snapshot of the world state.
        
        Args:
            world_data: Complete world state data
            description: Description of the version
            is_major_version: Whether this is a major version increment
            metadata: Optional metadata for the version
            
        Returns:
            ID of the created version
        """
        timestamp = datetime.utcnow().isoformat()
        version_id = str(uuid.uuid4())
        
        if metadata is None:
            metadata = {}
        
        # Get the parent version
        parent_version = self._get_current_version()
        
        # Create the new version
        if is_major_version:
            major = parent_version.major_version + 1
            minor = 0
            patch = 0
        else:
            major = parent_version.major_version
            minor = parent_version.minor_version + 1
            patch = 0
        
        # Serialize the full world data
        serialized_data = serialize(
            world_data,
            metadata={
                "version_id": version_id,
                "description": description,
                "timestamp": timestamp
            }
        )
        
        # Create the new version
        new_version = WorldVersion(
            version_id=version_id,
            timestamp=timestamp,
            description=description,
            major_version=major,
            minor_version=minor,
            patch_version=patch,
            parent_version_id=parent_version.version_id,
            full_data_id=version_id,  # Use the same ID for the version and its data
            changes_since_parent=[],  # No incremental changes, this is a full snapshot
            metadata=metadata
        )
        
        # Update our data structures
        self.versions[version_id] = new_version
        self.full_snapshots[version_id] = serialized_data
        self.current_version_id = version_id
        
        # Update version history
        if parent_version.version_id in self.version_history:
            self.version_history[parent_version.version_id].append(version_id)
        self.version_history[version_id] = []
        
        logger.info(f"Created version snapshot: {version_id} ({new_version.get_version_string()})")
        return version_id
    
    def record_change(self, change: ChangeRecord) -> str:
        """
        Record a change to the world state.
        
        Args:
            change: The change record to add
            
        Returns:
            ID of the recorded change
        """
        # Store the change
        self.changes[change.change_id] = change
        
        # Update the current version to include this change
        if self.current_version_id:
            current_version = self.versions[self.current_version_id]
            current_version.changes_since_parent.append(change.change_id)
            
            # Increment patch version
            current_version.patch_version += 1
            
            logger.debug(f"Recorded change {change.change_id} to version {self.current_version_id}")
        else:
            logger.warning("No current version to record change against")
            
        return change.change_id
    
    def create_incremental_version(
        self,
        description: str,
        is_minor_version: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new version based on accumulated changes.
        
        Args:
            description: Description of the version
            is_minor_version: Whether this is a minor version increment
            metadata: Optional metadata for the version
            
        Returns:
            ID of the created version
        """
        timestamp = datetime.utcnow().isoformat()
        version_id = str(uuid.uuid4())
        
        if metadata is None:
            metadata = {}
        
        # Get the parent version
        parent_version = self._get_current_version()
        
        # Get accumulated changes
        changes_since_parent = parent_version.changes_since_parent
        
        # Reset the parent's changes list (they're now part of this version)
        parent_version.changes_since_parent = []
        
        # Determine version numbers
        if is_minor_version:
            major = parent_version.major_version
            minor = parent_version.minor_version + 1
            patch = 0
        else:
            major = parent_version.major_version
            minor = parent_version.minor_version
            patch = parent_version.patch_version
        
        # Create the new version
        new_version = WorldVersion(
            version_id=version_id,
            timestamp=timestamp,
            description=description,
            major_version=major,
            minor_version=minor,
            patch_version=patch,
            parent_version_id=parent_version.version_id,
            full_data_id=parent_version.full_data_id,  # Reuse the parent's full data
            changes_since_parent=changes_since_parent,
            metadata=metadata
        )
        
        # Update our data structures
        self.versions[version_id] = new_version
        self.current_version_id = version_id
        
        # Update version history
        if parent_version.version_id in self.version_history:
            self.version_history[parent_version.version_id].append(version_id)
        self.version_history[version_id] = []
        
        logger.info(f"Created incremental version: {version_id} ({new_version.get_version_string()})")
        return version_id
    
    def rollback_to_version(self, version_id: str) -> bool:
        """
        Roll back to a previous version.
        
        Args:
            version_id: ID of the version to roll back to
            
        Returns:
            True if successful, False otherwise
        """
        if version_id not in self.versions:
            logger.error(f"Version {version_id} not found")
            return False
        
        target_version = self.versions[version_id]
        
        # Create a new branch from the target version
        timestamp = datetime.utcnow().isoformat()
        new_version_id = str(uuid.uuid4())
        
        # Create the new version
        new_version = WorldVersion(
            version_id=new_version_id,
            timestamp=timestamp,
            description=f"Rollback to version {target_version.get_version_string()}",
            major_version=target_version.major_version,
            minor_version=target_version.minor_version,
            patch_version=target_version.patch_version + 1,  # Increment patch version
            parent_version_id=target_version.version_id,
            full_data_id=target_version.full_data_id,
            changes_since_parent=[],  # No changes yet
            metadata={"rollback": True, "from_version": self.current_version_id}
        )
        
        # Update our data structures
        self.versions[new_version_id] = new_version
        self.current_version_id = new_version_id
        
        # Update version history
        if target_version.version_id in self.version_history:
            self.version_history[target_version.version_id].append(new_version_id)
        self.version_history[new_version_id] = []
        
        logger.info(f"Rolled back to version {version_id} (created new version {new_version_id})")
        return True
    
    def get_version_data(self, version_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the complete world data for a version.
        
        Args:
            version_id: ID of the version (uses current version if None)
            
        Returns:
            Complete world data for the version, or None if not found
        """
        version_id = version_id or self.current_version_id
        if not version_id or version_id not in self.versions:
            logger.error(f"Version {version_id} not found")
            return None
        
        version = self.versions[version_id]
        
        # If this version has direct full data, use it
        if version.full_data_id and version.full_data_id in self.full_snapshots:
            serialized_data = self.full_snapshots[version.full_data_id]
            return deserialize(serialized_data)
        
        # Otherwise, we need to reconstruct from the parent and apply changes
        # First, find the closest ancestor with full data
        ancestor_id = version.parent_version_id
        change_chain = []  # List of version IDs to apply changes from
        
        while ancestor_id:
            ancestor = self.versions.get(ancestor_id)
            if not ancestor:
                logger.error(f"Ancestor version {ancestor_id} not found")
                return None
            
            # Add this ancestor to our chain
            change_chain.append(ancestor_id)
            
            # If this ancestor has full data, we can stop
            if ancestor.full_data_id and ancestor.full_data_id in self.full_snapshots:
                break
            
            # Otherwise, continue to the parent
            ancestor_id = ancestor.parent_version_id
        
        # If we didn't find an ancestor with full data, we can't reconstruct
        if not ancestor_id or not ancestor.full_data_id or ancestor.full_data_id not in self.full_snapshots:
            logger.error(f"No ancestor with full data found for version {version_id}")
            return None
        
        # Start with the full data from the ancestor
        serialized_data = self.full_snapshots[ancestor.full_data_id]
        data = deserialize(serialized_data)
        
        # Apply changes from each version in reverse order (oldest first)
        change_chain.reverse()
        for ancestor_id in change_chain:
            ancestor = self.versions.get(ancestor_id)
            if ancestor:
                self._apply_changes_to_data(data, ancestor.changes_since_parent)
        
        # Finally, apply changes from the requested version
        self._apply_changes_to_data(data, version.changes_since_parent)
        
        return data
    
    def _apply_changes_to_data(self, data: Dict[str, Any], change_ids: List[str]) -> None:
        """
        Apply a list of changes to the data.
        
        Args:
            data: Data to modify
            change_ids: List of change IDs to apply
        """
        for change_id in change_ids:
            if change_id not in self.changes:
                logger.warning(f"Change {change_id} not found")
                continue
            
            change = self.changes[change_id]
            
            # Apply the change based on its type
            if change.change_type == "create":
                # Create a new entity or field
                if change.field_name:
                    # Create or update a field
                    if change.entity_type not in data:
                        data[change.entity_type] = {}
                    if change.entity_id not in data[change.entity_type]:
                        data[change.entity_type][change.entity_id] = {}
                    data[change.entity_type][change.entity_id][change.field_name] = change.new_value
                else:
                    # Create a new entity
                    if change.entity_type not in data:
                        data[change.entity_type] = {}
                    data[change.entity_type][change.entity_id] = change.new_value
            elif change.change_type == "update":
                # Update an existing entity or field
                if change.field_name:
                    # Update a field
                    if (change.entity_type in data and 
                        change.entity_id in data[change.entity_type]):
                        data[change.entity_type][change.entity_id][change.field_name] = change.new_value
                else:
                    # Update an entire entity
                    if change.entity_type in data:
                        data[change.entity_type][change.entity_id] = change.new_value
            elif change.change_type == "delete":
                # Delete an entity or field
                if change.field_name:
                    # Delete a field
                    if (change.entity_type in data and 
                        change.entity_id in data[change.entity_type] and
                        change.field_name in data[change.entity_type][change.entity_id]):
                        del data[change.entity_type][change.entity_id][change.field_name]
                else:
                    # Delete an entity
                    if (change.entity_type in data and 
                        change.entity_id in data[change.entity_type]):
                        del data[change.entity_type][change.entity_id]
    
    def _get_current_version(self) -> WorldVersion:
        """Get the current version or create one if none exists."""
        self._init_if_needed()
        
        if not self.current_version_id or self.current_version_id not in self.versions:
            # Something's wrong, re-initialize
            self.versions = {}
            self._init_if_needed()
        
        return self.versions[self.current_version_id]
    
    def get_version_list(self) -> List[Dict[str, Any]]:
        """
        Get a list of all versions.
        
        Returns:
            List of version dictionaries
        """
        return [version.to_dict() for version in self.versions.values()]
    
    def get_version_history(self) -> Dict[str, List[str]]:
        """
        Get the version history graph.
        
        Returns:
            Dictionary mapping parent version IDs to lists of child version IDs
        """
        return self.version_history
    
    def get_change_history(self, version_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the history of changes for a version.
        
        Args:
            version_id: ID of the version (uses current version if None)
            
        Returns:
            List of change dictionaries
        """
        version_id = version_id or self.current_version_id
        if not version_id or version_id not in self.versions:
            return []
        
        version = self.versions[version_id]
        
        # Get changes from this version
        changes = []
        for change_id in version.changes_since_parent:
            if change_id in self.changes:
                changes.append(self.changes[change_id].to_dict())
        
        return changes
    
    def export_version_data(self, version_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Export version data for external storage.
        
        Args:
            version_id: ID of the version (uses current version if None)
            
        Returns:
            Dictionary with version data
        """
        version_id = version_id or self.current_version_id
        if not version_id or version_id not in self.versions:
            return {}
        
        version = self.versions[version_id]
        
        # Get the serialized data
        serialized_data = None
        if version.full_data_id and version.full_data_id in self.full_snapshots:
            serialized_data = self.full_snapshots[version.full_data_id].to_dict()
        
        # Get changes
        changes = {}
        for change_id in version.changes_since_parent:
            if change_id in self.changes:
                changes[change_id] = self.changes[change_id].to_dict()
        
        return {
            "version": version.to_dict(),
            "serialized_data": serialized_data,
            "changes": changes
        }
    
    def import_version_data(self, data: Dict[str, Any]) -> str:
        """
        Import version data from external storage.
        
        Args:
            data: Dictionary with version data
            
        Returns:
            ID of the imported version
        """
        if "version" not in data:
            raise ValueError("Invalid version data: missing 'version' key")
        
        # Create the version
        version_data = data["version"]
        version = WorldVersion.from_dict(version_data)
        version_id = version.version_id
        
        # Add the version to our data structures
        self.versions[version_id] = version
        
        # Import serialized data if present
        if "serialized_data" in data and data["serialized_data"]:
            serialized_data = SerializedData.from_dict(data["serialized_data"])
            self.full_snapshots[version.full_data_id] = serialized_data
        
        # Import changes if present
        if "changes" in data and data["changes"]:
            for change_id, change_data in data["changes"].items():
                self.changes[change_id] = ChangeRecord.from_dict(change_data)
        
        # Update version history
        if version.parent_version_id:
            if version.parent_version_id not in self.version_history:
                self.version_history[version.parent_version_id] = []
            self.version_history[version.parent_version_id].append(version_id)
        if version_id not in self.version_history:
            self.version_history[version_id] = []
        
        return version_id 