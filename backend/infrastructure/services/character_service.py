"""Character service for managing character entities."""

from typing import List, Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.systems.character import Character
from backend.infrastructure.services import BaseService
from backend.infrastructure.database import get_db

class CharacterService(BaseService[Character]):
    """Service for managing character entities."""
    
    def __init__(self, db: Session = Depends(get_db)):
        """Initialize the character service.
        
        Args:
            db: Database session
        """
        super().__init__(Character, db)
    
    async def get_characters_by_player(self, player_id: int) -> List[Character]:
        """Get all characters for a specific player.
        
        Args:
            player_id: Player ID
            
        Returns:
            List of characters
        """
        filters = {"player_id": player_id}
        return await self.get_by_filter(filters)
    
    async def get_characters_by_campaign(self, campaign_id: int) -> List[Character]:
        """Get all characters in a specific campaign.
        
        Args:
            campaign_id: Campaign ID
            
        Returns:
            List of characters
        """
        filters = {"campaign_id": campaign_id}
        return await self.get_by_filter(filters)
    
    async def update_character_attributes(self, character_id: int, attributes: Dict[str, Any]) -> Character:
        """Update attributes for a character.
        
        Args:
            character_id: Character ID
            attributes: Updated attributes
            
        Returns:
            Updated character entity
            
        Raises:
            HTTPException: If character not found or update fails
        """
        character = await self.get_by_id(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with ID {character_id} not found"
            )
        
        # Update only attributes-related fields
        update_data = {}
        attributes_fields = [
            "strength", "dexterity", "constitution", 
            "intelligence", "wisdom", "charisma",
            "health", "max_health", "level", "experience"
        ]
        
        for field in attributes_fields:
            if field in attributes:
                update_data[field] = attributes[field]
        
        return await self.update(character_id, update_data)
    
    async def add_item_to_inventory(self, character_id: int, item_data: Dict[str, Any]) -> Character:
        """Add an item to a character's inventory.
        
        Args:
            character_id: Character ID
            item_data: Item data to add
            
        Returns:
            Updated character entity
            
        Raises:
            HTTPException: If character not found or update fails
        """
        character = await self.get_by_id(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with ID {character_id} not found"
            )
        
        # Get current inventory or initialize new list
        inventory = character.inventory or []
        
        # Generate an item ID if not provided
        if "id" not in item_data:
            item_id = 1
            if inventory:
                item_id = max(item.get("id", 0) for item in inventory) + 1
            item_data["id"] = item_id
        
        # Add item to inventory
        inventory.append(item_data)
        
        # Update character with new inventory
        return await self.update(character_id, {"inventory": inventory})
    
    async def remove_item_from_inventory(self, character_id: int, item_id: int) -> Character:
        """Remove an item from a character's inventory.
        
        Args:
            character_id: Character ID
            item_id: Item ID
            
        Returns:
            Updated character entity
            
        Raises:
            HTTPException: If character not found or update fails
        """
        character = await self.get_by_id(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with ID {character_id} not found"
            )
        
        # Get current inventory
        inventory = character.inventory or []
        
        # Remove item from inventory
        filtered_inventory = [item for item in inventory if item.get("id") != item_id]
        
        if len(filtered_inventory) == len(inventory):
            # Item not found, but we'll simply return the unchanged character
            return character
        
        # Update character with new inventory
        return await self.update(character_id, {"inventory": filtered_inventory})
    
    async def update_character_location(self, character_id: int, location_id: int) -> Character:
        """Update a character's location.
        
        Args:
            character_id: Character ID
            location_id: New location ID
            
        Returns:
            Updated character entity
            
        Raises:
            HTTPException: If character not found or update fails
        """
        character = await self.get_by_id(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character with ID {character_id} not found"
            )
        
        # Update location
        return await self.update(character_id, {"location_id": location_id}) 