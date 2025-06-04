"""
Character System Integration for Inventory

This module provides integration between the inventory system and character system
for strength attributes, ownership, and character-specific inventory behaviors.
"""

from typing import Optional, Dict, Any
from uuid import UUID
import asyncio

from backend.systems.inventory.protocols import CharacterServiceInterface


class MockCharacterService:
    """Mock character service for testing and development"""
    
    def __init__(self):
        # Mock character data for testing
        self.mock_characters = {
            # Example character data - in real implementation this would come from database
        }
        self.mock_players = {
            # Example player data
        }
    
    async def get_character_strength(self, character_id: UUID) -> int:
        """Get character strength attribute (mock implementation)"""
        # Mock implementation - would connect to actual character system
        character = self.mock_characters.get(str(character_id))
        if character:
            return character.get("strength", 10)  # Default strength of 10
        
        # Default strength for unknown characters
        return 10
    
    async def get_character_player_id(self, character_id: UUID) -> Optional[UUID]:
        """Get player ID for character (mock implementation)"""
        character = self.mock_characters.get(str(character_id))
        if character:
            player_id_str = character.get("player_id")
            if player_id_str:
                return UUID(player_id_str)
        
        return None
    
    async def get_character_info(self, character_id: UUID) -> Optional[Dict[str, Any]]:
        """Get full character information (mock implementation)"""
        character = self.mock_characters.get(str(character_id))
        if character:
            return {
                "id": character_id,
                "name": character.get("name", "Unknown"),
                "strength": character.get("strength", 10),
                "player_id": character.get("player_id"),
                "level": character.get("level", 1),
                "class": character.get("class", "warrior")
            }
        
        return None
    
    def add_mock_character(
        self,
        character_id: UUID,
        player_id: UUID,
        name: str = "Test Character",
        strength: int = 10,
        level: int = 1,
        character_class: str = "warrior"
    ):
        """Add mock character for testing"""
        self.mock_characters[str(character_id)] = {
            "name": name,
            "strength": strength,
            "player_id": str(player_id),
            "level": level,
            "class": character_class
        }
    
    def clear_mock_data(self):
        """Clear all mock data"""
        self.mock_characters.clear()
        self.mock_players.clear()


class DatabaseCharacterService:
    """Character service that connects to the actual character database"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def get_character_strength(self, character_id: UUID) -> int:
        """Get character strength attribute from database"""
        try:
            # Import here to avoid circular dependencies
            # from backend.infrastructure.models.character.models import CharacterEntity
            
            # TODO: Replace with actual character model query
            # character = self.db.query(CharacterEntity).filter(
            #     CharacterEntity.id == character_id,
            #     CharacterEntity.is_active == True
            # ).first()
            
            # if character:
            #     return character.strength or 10
            
            # For now, return default until character system is implemented
            return 10
            
        except Exception as e:
            # Log error and return default
            print(f"Error fetching character strength: {e}")
            return 10
    
    async def get_character_player_id(self, character_id: UUID) -> Optional[UUID]:
        """Get player ID for character from database"""
        try:
            # TODO: Replace with actual character model query
            # character = self.db.query(CharacterEntity).filter(
            #     CharacterEntity.id == character_id,
            #     CharacterEntity.is_active == True
            # ).first()
            
            # if character:
            #     return character.player_id
            
            # For now, return None until character system is implemented
            return None
            
        except Exception as e:
            # Log error and return None
            print(f"Error fetching character player ID: {e}")
            return None
    
    async def get_character_info(self, character_id: UUID) -> Optional[Dict[str, Any]]:
        """Get full character information from database"""
        try:
            # TODO: Replace with actual character model query
            # character = self.db.query(CharacterEntity).filter(
            #     CharacterEntity.id == character_id,
            #     CharacterEntity.is_active == True
            # ).first()
            
            # if character:
            #     return {
            #         "id": character.id,
            #         "name": character.name,
            #         "strength": character.strength,
            #         "player_id": character.player_id,
            #         "level": character.level,
            #         "class": character.character_class
            #     }
            
            # For now, return minimal data until character system is implemented
            return {
                "id": character_id,
                "name": "Unknown Character",
                "strength": 10,
                "player_id": None,
                "level": 1,
                "class": "warrior"
            }
            
        except Exception as e:
            # Log error and return None
            print(f"Error fetching character info: {e}")
            return None


class CharacterInventoryIntegration:
    """Integration service for character-inventory relationships"""
    
    def __init__(self, character_service: CharacterServiceInterface):
        self.character_service = character_service
    
    async def calculate_character_inventory_capacity(self, character_id: UUID) -> Dict[str, Any]:
        """Calculate inventory capacity settings for a character"""
        character_info = await self.character_service.get_character_info(character_id) if hasattr(self.character_service, 'get_character_info') else None
        strength = await self.character_service.get_character_strength(character_id)
        
        # Base calculations
        base_capacity = 50  # Default item slots
        weight_multiplier = 10.0  # Strength * 10 = max weight
        max_weight = strength * weight_multiplier
        
        # Level-based bonuses (if character info available)
        if character_info:
            level = character_info.get("level", 1)
            character_class = character_info.get("class", "warrior")
            
            # Class-based capacity modifiers
            class_modifiers = {
                "warrior": {"capacity": 1.1, "weight": 1.2},
                "ranger": {"capacity": 1.0, "weight": 1.1},
                "mage": {"capacity": 0.9, "weight": 0.8},
                "thief": {"capacity": 1.0, "weight": 0.9},
                "cleric": {"capacity": 1.0, "weight": 1.0}
            }
            
            modifier = class_modifiers.get(character_class, {"capacity": 1.0, "weight": 1.0})
            
            # Apply class modifiers
            base_capacity = int(base_capacity * modifier["capacity"])
            max_weight = max_weight * modifier["weight"]
            
            # Level bonuses (small increase per level)
            level_capacity_bonus = (level - 1) * 2  # +2 capacity per level
            level_weight_bonus = (level - 1) * 5.0  # +5 weight per level
            
            base_capacity += level_capacity_bonus
            max_weight += level_weight_bonus
        
        return {
            "character_id": character_id,
            "strength": strength,
            "base_capacity": base_capacity,
            "max_weight": max_weight,
            "character_info": character_info,
            "calculations": {
                "strength_multiplier": weight_multiplier,
                "class_modifier": character_info.get("class", "unknown") if character_info else "unknown",
                "level_bonus": character_info.get("level", 1) if character_info else 1
            }
        }
    
    async def validate_character_ownership(self, character_id: UUID, player_id: UUID) -> bool:
        """Validate that a player owns a character"""
        character_player_id = await self.character_service.get_character_player_id(character_id)
        return character_player_id == player_id
    
    async def get_encumbrance_impact_for_character(self, character_id: UUID, current_weight: float) -> Dict[str, Any]:
        """Get encumbrance impact specific to a character"""
        capacity_info = await self.calculate_character_inventory_capacity(character_id)
        max_weight = capacity_info["max_weight"]
        
        if max_weight <= 0:
            return {
                "encumbrance_level": "normal",
                "weight_ratio": 0.0,
                "movement_penalty": 1.0,
                "warnings": []
            }
        
        weight_ratio = current_weight / max_weight
        warnings = []
        
        # Determine encumbrance level
        if weight_ratio <= 0.75:
            encumbrance_level = "normal"
            movement_penalty = 1.0
        elif weight_ratio <= 1.0:
            encumbrance_level = "heavy"
            movement_penalty = 1.2
            warnings.append("You are carrying a heavy load")
        elif weight_ratio <= 1.25:
            encumbrance_level = "encumbered"
            movement_penalty = 1.5
            warnings.append("You are encumbered and moving slowly")
        else:
            encumbrance_level = "overloaded"
            movement_penalty = 2.0
            warnings.append("You are severely overloaded!")
        
        return {
            "character_id": character_id,
            "encumbrance_level": encumbrance_level,
            "weight_ratio": weight_ratio,
            "current_weight": current_weight,
            "max_weight": max_weight,
            "movement_penalty": movement_penalty,
            "warnings": warnings,
            "character_strength": capacity_info["strength"]
        }


def create_character_service(db_session=None, use_mock: bool = False) -> CharacterServiceInterface:
    """Factory function to create appropriate character service"""
    if use_mock or db_session is None:
        return MockCharacterService()
    else:
        return DatabaseCharacterService(db_session)


def create_character_integration(character_service: CharacterServiceInterface) -> CharacterInventoryIntegration:
    """Factory function to create character-inventory integration"""
    return CharacterInventoryIntegration(character_service) 