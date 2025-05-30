"""NPC service for managing NPC entities."""

from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..models.npc import NPC
from .base_service import BaseService
from ..database import get_db

class NPCService(BaseService[NPC]):
    """Service for managing NPC entities."""
    
    def __init__(self, db: Session = Depends(get_db)):
        """Initialize the NPC service.
        
        Args:
            db: Database session
        """
        super().__init__(NPC, db)
    
    async def get_npcs_by_world(self, world_id: int) -> List[NPC]:
        """Get all NPCs for a specific world.
        
        Args:
            world_id: World ID
            
        Returns:
            List of NPCs
        """
        filters = {"world_id": world_id}
        return await self.get_by_filter(filters)
    
    async def get_npcs_by_location(self, location_id: int) -> List[NPC]:
        """Get all NPCs at a specific location.
        
        Args:
            location_id: Location ID
            
        Returns:
            List of NPCs
        """
        filters = {"location_id": location_id}
        return await self.get_by_filter(filters)
    
    async def update_npc_state(self, npc_id: int, state_data: Dict[str, Any]) -> NPC:
        """Update the state of an NPC.
        
        Args:
            npc_id: NPC ID
            state_data: Updated state data
            
        Returns:
            Updated NPC entity
            
        Raises:
            HTTPException: If NPC not found or update fails
        """
        npc = await self.get_by_id(npc_id)
        if not npc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"NPC with ID {npc_id} not found"
            )
        
        # Update only state-related fields
        update_data = {}
        state_fields = [
            "location_id", "status", "health", "mood", "inventory", 
            "relations", "dialogue_state", "goals", "current_activity"
        ]
        
        for field in state_fields:
            if field in state_data:
                update_data[field] = state_data[field]
        
        return await self.update(npc_id, update_data)
    
    async def move_npc(self, npc_id: int, location_id: int) -> NPC:
        """Move an NPC to a new location.
        
        Args:
            npc_id: NPC ID
            location_id: New location ID
            
        Returns:
            Updated NPC entity
            
        Raises:
            HTTPException: If NPC not found or update fails
        """
        npc = await self.get_by_id(npc_id)
        if not npc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"NPC with ID {npc_id} not found"
            )
        
        # Update location
        return await self.update(npc_id, {"location_id": location_id})
    
    async def update_npc_relations(self, npc_id: int, relations: Dict[str, int]) -> NPC:
        """Update an NPC's relationships with other entities.
        
        Args:
            npc_id: NPC ID
            relations: Dictionary of entity IDs to relationship scores
            
        Returns:
            Updated NPC entity
            
        Raises:
            HTTPException: If NPC not found or update fails
        """
        npc = await self.get_by_id(npc_id)
        if not npc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"NPC with ID {npc_id} not found"
            )
        
        # Get current relations or initialize new dictionary
        current_relations = npc.relations or {}
        
        # Update with new relation values
        for entity_id, score in relations.items():
            current_relations[entity_id] = score
        
        # Update NPC with new relations
        return await self.update(npc_id, {"relations": current_relations})
    
    async def add_item_to_inventory(self, npc_id: int, item_data: Dict[str, Any]) -> NPC:
        """Add an item to an NPC's inventory.
        
        Args:
            npc_id: NPC ID
            item_data: Item data to add
            
        Returns:
            Updated NPC entity
            
        Raises:
            HTTPException: If NPC not found or update fails
        """
        npc = await self.get_by_id(npc_id)
        if not npc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"NPC with ID {npc_id} not found"
            )
        
        # Get current inventory or initialize new list
        inventory = npc.inventory or []
        
        # Generate an item ID if not provided
        if "id" not in item_data:
            item_id = 1
            if inventory:
                item_id = max(item.get("id", 0) for item in inventory) + 1
            item_data["id"] = item_id
        
        # Add item to inventory
        inventory.append(item_data)
        
        # Update NPC with new inventory
        return await self.update(npc_id, {"inventory": inventory}) 