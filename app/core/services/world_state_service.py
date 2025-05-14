"""
Service layer for managing world state operations.
"""

from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy import desc
from app.core.models.world_state import WorldState
from app.core.models.version_control import VersionControl
from app.core.database import db
from app.core.exceptions import WorldStateError

class WorldStateManager:
    """Service for managing world state operations."""
    
    @staticmethod
    def create_world(
        name: str,
        description: str = None,
        initial_data: Dict = None
    ) -> WorldState:
        """
        Create a new world state.
        
        Args:
            name: Name of the world
            description: Optional description
            initial_data: Optional initial world data
            
        Returns:
            WorldState: The newly created world state
        """
        world = WorldState(
            name=name,
            description=description,
            world_data=initial_data or {}
        )
        
        # Initialize version control
        world.version = VersionControl(
            major=0,
            minor=1,
            description="Initial world creation"
        )
        
        db.session.add(world)
        db.session.commit()
        return world

    @staticmethod
    def get_world(world_id: int) -> Optional[WorldState]:
        """
        Retrieve a world state by ID.
        
        Args:
            world_id: ID of the world to retrieve
            
        Returns:
            WorldState or None: The requested world state if found
        """
        return WorldState.query.get(world_id)

    @staticmethod
    def get_worlds(
        limit: int = None,
        offset: int = None
    ) -> List[WorldState]:
        """
        Retrieve all world states with pagination.
        
        Args:
            limit: Maximum number of worlds to return
            offset: Number of worlds to skip
            
        Returns:
            List[WorldState]: List of world states
        """
        query = WorldState.query.order_by(desc(WorldState.created_at))
        
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
            
        return query.all()

    @staticmethod
    def save_world(world_id: int) -> WorldState:
        """
        Save changes to a world state.
        
        Args:
            world_id: ID of the world to save
            
        Returns:
            WorldState: The updated world state
            
        Raises:
            WorldStateError: If world not found
        """
        world = WorldStateManager.get_world(world_id)
        if not world:
            raise WorldStateError(f"World with ID {world_id} not found")
        
        # Update version and save time
        world.version.minor += 1
        world.last_saved_at = datetime.utcnow()
        
        db.session.commit()
        return world

    @staticmethod
    def create_snapshot(
        world_id: int,
        description: str = None
    ) -> WorldState:
        """
        Create a major version snapshot of the world state.
        
        Args:
            world_id: ID of the world to snapshot
            description: Optional description of the snapshot
            
        Returns:
            WorldState: The updated world state
            
        Raises:
            WorldStateError: If world not found
        """
        world = WorldStateManager.get_world(world_id)
        if not world:
            raise WorldStateError(f"World with ID {world_id} not found")
        
        # Create new version
        world.version.major += 1
        world.version.minor = 0
        world.version.description = description or f"Snapshot at {datetime.utcnow()}"
        world.last_saved_at = datetime.utcnow()
        
        db.session.commit()
        return world

    @staticmethod
    def restore_snapshot(
        world_id: int,
        version_id: int
    ) -> WorldState:
        """
        Restore a world state to a previous version.
        
        Args:
            world_id: ID of the world to restore
            version_id: ID of the version to restore to
            
        Returns:
            WorldState: The restored world state
            
        Raises:
            WorldStateError: If world or version not found
        """
        world = WorldStateManager.get_world(world_id)
        if not world:
            raise WorldStateError(f"World with ID {world_id} not found")
        
        version = VersionControl.query.get(version_id)
        if not version:
            raise WorldStateError(f"Version with ID {version_id} not found")
        
        # Create new version for the restoration
        world.version = VersionControl(
            major=version.major,
            minor=0,
            description=f"Restored from version {version_id}"
        )
        world.last_saved_at = datetime.utcnow()
        
        db.session.commit()
        return world

    @staticmethod
    def delete_world(world_id: int) -> bool:
        """
        Delete a world state.
        
        Args:
            world_id: ID of the world to delete
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            WorldStateError: If world not found
        """
        world = WorldStateManager.get_world(world_id)
        if not world:
            raise WorldStateError(f"World with ID {world_id} not found")
        
        db.session.delete(world)
        db.session.commit()
        return True

    @staticmethod
    def update_world_data(
        world_id: int,
        data_updates: Dict
    ) -> WorldState:
        """
        Update specific fields in the world data.
        
        Args:
            world_id: ID of the world to update
            data_updates: Dictionary of fields to update
            
        Returns:
            WorldState: The updated world state
            
        Raises:
            WorldStateError: If world not found
        """
        world = WorldStateManager.get_world(world_id)
        if not world:
            raise WorldStateError(f"World with ID {world_id} not found")
        
        # Update world data
        world.world_data.update(data_updates)
        
        # Increment version and save
        world.version.minor += 1
        world.last_saved_at = datetime.utcnow()
        
        db.session.commit()
        return world 