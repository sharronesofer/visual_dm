"""
Loot System Services - Pure Business Logic

This module provides business logic services for the loot system
according to the Development Bible standards.
"""

from typing import Optional, List, Dict, Any, Tuple, Protocol
from uuid import UUID, uuid4
from datetime import datetime


# Domain Models (business logic types)
class LootData:
    """Business domain loot data structure"""
    def __init__(self, 
                 id: UUID,
                 name: str,
                 description: Optional[str] = None,
                 category: str = "misc",
                 rarity: str = "common",
                 properties: Optional[Dict[str, Any]] = None,
                 effects: Optional[List[Dict[str, Any]]] = None,
                 stats: Optional[Dict[str, Any]] = None,
                 value: int = 0):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.rarity = rarity
        self.properties = properties or {}
        self.effects = effects or []
        self.stats = stats or {}
        self.value = value

    def calculate_power_score(self) -> int:
        """Calculate item power score based on business rules"""
        from backend.systems.loot.utils.loot_core import calculate_item_power_score
        return calculate_item_power_score(self.to_dict())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for calculations"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "rarity": self.rarity,
            "properties": self.properties,
            "effects": self.effects,
            "stats": self.stats,
            "value": self.value
        }


class CreateLootData:
    """Business domain data for loot creation"""
    def __init__(self, 
                 name: str,
                 description: Optional[str] = None,
                 category: str = "misc",
                 rarity: str = "common",
                 properties: Optional[Dict[str, Any]] = None):
        self.name = name
        self.description = description
        self.category = category
        self.rarity = rarity
        self.properties = properties or {}


class UpdateLootData:
    """Business domain data for loot updates"""
    def __init__(self, **update_fields):
        self.update_fields = update_fields

    def get_fields(self) -> Dict[str, Any]:
        return self.update_fields


# Business Logic Protocols (dependency injection)
class LootRepository(Protocol):
    """Protocol for loot data access"""
    
    def get_loot_by_id(self, loot_id: UUID) -> Optional[LootData]:
        """Get loot by ID"""
        ...
    
    def get_loot_by_name(self, name: str) -> Optional[LootData]:
        """Get loot by name"""
        ...
    
    def create_loot(self, loot_data: LootData) -> LootData:
        """Create a new loot"""
        ...
    
    def update_loot(self, loot_data: LootData) -> LootData:
        """Update existing loot"""
        ...
    
    def delete_loot(self, loot_id: UUID) -> bool:
        """Delete loot"""
        ...
    
    def list_loots(self, 
                   page: int = 1, 
                   size: int = 50, 
                   status: Optional[str] = None,
                   search: Optional[str] = None) -> Tuple[List[LootData], int]:
        """List loots with pagination"""
        ...
    
    def get_loot_statistics(self) -> Dict[str, Any]:
        """Get loot statistics"""
        ...


class LootValidationService(Protocol):
    """Protocol for loot validation"""
    
    def validate_loot_data(self, loot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate loot creation/update data"""
        ...
    
    def validate_rarity(self, rarity: str) -> str:
        """Validate rarity value"""
        ...
    
    def validate_category(self, category: str) -> str:
        """Validate category value"""
        ...


class LootBusinessService:
    """Service class for loot business logic - pure business rules"""
    
    def __init__(self, 
                 loot_repository: LootRepository,
                 validation_service: LootValidationService):
        self.loot_repository = loot_repository
        self.validation_service = validation_service

    def create_loot(
        self, 
        create_data: CreateLootData,
        user_id: Optional[UUID] = None
    ) -> LootData:
        """Create a new loot with business validation"""
        # Convert to dict for validation
        loot_data_dict = {
            'name': create_data.name,
            'description': create_data.description,
            'category': create_data.category,
            'rarity': create_data.rarity,
            'properties': create_data.properties
        }
        
        # Comprehensive validation and sanitization
        validated_data = self.validation_service.validate_loot_data(loot_data_dict)
        
        # Business rule: Check for existing loot with same name
        existing_loot = self.loot_repository.get_loot_by_name(validated_data['name'])
        if existing_loot:
            raise ValueError(f"Loot with name '{validated_data['name']}' already exists")
        
        # Business rule: Calculate initial value based on rarity
        rarity_multipliers = {
            "common": 1.0,
            "uncommon": 2.0,
            "rare": 5.0,
            "epic": 15.0,
            "legendary": 50.0
        }
        base_value = 10  # Base value for items
        calculated_value = int(base_value * rarity_multipliers.get(validated_data['rarity'], 1.0))
        
        # Create business entity with validated data
        loot_entity = LootData(
            id=uuid4(),
            name=validated_data['name'],
            description=validated_data.get('description'),
            category=validated_data.get('category', 'misc'),
            rarity=validated_data.get('rarity', 'common'),
            properties=validated_data.get('properties', {}),
            value=calculated_value
        )
        
        # Business rule: Add user tracking if provided
        if user_id:
            loot_entity.properties['created_by'] = str(user_id)
        
        # Persist via repository
        return self.loot_repository.create_loot(loot_entity)

    def get_loot_by_id(self, loot_id: UUID) -> Optional[LootData]:
        """Get loot by ID"""
        return self.loot_repository.get_loot_by_id(loot_id)

    def update_loot(
        self, 
        loot_id: UUID, 
        update_data: UpdateLootData
    ) -> LootData:
        """Update existing loot with business rules"""
        # Business rule: Loot must exist
        entity = self.loot_repository.get_loot_by_id(loot_id)
        if not entity:
            raise ValueError(f"Loot {loot_id} not found")
        
        # Apply updates with business validation
        update_fields = update_data.get_fields()
        if update_fields:
            for field, value in update_fields.items():
                setattr(entity, field, value)
        
        return self.loot_repository.update_loot(entity)

    def delete_loot(self, loot_id: UUID) -> bool:
        """Delete loot with business rules"""
        # Business rule: Loot must exist
        entity = self.loot_repository.get_loot_by_id(loot_id)
        if not entity:
            raise ValueError(f"Loot {loot_id} not found")
        
        return self.loot_repository.delete_loot(loot_id)

    def list_loots(
        self,
        page: int = 1,
        size: int = 50,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[LootData], int]:
        """List loots with pagination and filtering"""
        return self.loot_repository.list_loots(page, size, status, search)

    def get_loot_statistics(self) -> Dict[str, Any]:
        """Get loot statistics"""
        return self.loot_repository.get_loot_statistics()

    def calculate_loot_value(self, loot: LootData, modifiers: Dict[str, float] = None) -> int:
        """Business logic: Calculate adjusted loot value"""
        base_value = loot.value
        
        if modifiers is None:
            modifiers = {}
        
        # Apply rarity modifier
        rarity_modifier = modifiers.get('rarity_modifier', 1.0)
        
        # Apply condition modifier
        condition_modifier = modifiers.get('condition_modifier', 1.0)
        
        # Apply market modifier
        market_modifier = modifiers.get('market_modifier', 1.0)
        
        # Calculate final value
        final_value = int(base_value * rarity_modifier * condition_modifier * market_modifier)
        
        return max(1, final_value)  # Minimum value of 1

    def assess_loot_rarity_impact(self, loot: LootData) -> Dict[str, Any]:
        """Business logic: Assess how rarity affects loot properties"""
        rarity_effects = {
            "common": {"power_multiplier": 1.0, "special_properties": 0, "max_effects": 0},
            "uncommon": {"power_multiplier": 1.2, "special_properties": 1, "max_effects": 1},
            "rare": {"power_multiplier": 1.5, "special_properties": 2, "max_effects": 2},
            "epic": {"power_multiplier": 2.0, "special_properties": 3, "max_effects": 3},
            "legendary": {"power_multiplier": 3.0, "special_properties": 5, "max_effects": 5}
        }
        
        rarity_data = rarity_effects.get(loot.rarity, rarity_effects["common"])
        
        return {
            "rarity": loot.rarity,
            "power_score": loot.calculate_power_score(),
            "suggested_effects": rarity_data["max_effects"],
            "value_multiplier": rarity_data["power_multiplier"],
            "special_properties_count": rarity_data["special_properties"]
        }


def create_loot_business_service(
    loot_repository: LootRepository,
    validation_service: LootValidationService
) -> LootBusinessService:
    """Factory function to create loot business service"""
    return LootBusinessService(loot_repository, validation_service) 