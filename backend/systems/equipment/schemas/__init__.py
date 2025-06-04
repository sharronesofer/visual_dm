"""
Equipment system schemas for API request/response validation.

This module defines Pydantic models for:
- Equipment creation and modification requests
- Equipment repair requests and responses
- Equipment identification requests and responses  
- Equipment enchanting/disenchanting requests and responses
- Equipment query filters and responses
- Set bonus information responses
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class EquipmentRarity(str, Enum):
    """Equipment rarity levels."""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class EquipmentQuality(str, Enum):
    """Equipment quality tiers."""
    BASIC = "basic"
    MILITARY = "military"
    NOBLE = "noble"

class DurabilityStatus(str, Enum):
    """Equipment durability status categories."""
    EXCELLENT = "excellent"
    GOOD = "good"
    WORN = "worn"
    DAMAGED = "damaged"
    BROKEN = "broken"

class EquipmentType(str, Enum):
    """Types of equipment."""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    TOOL = "tool"

# Base Schemas
class AbilitySchema(BaseModel):
    """Schema for equipment abilities."""
    id: str
    name: str
    description: str
    is_revealed: bool = False
    level_required: int = 1
    effect_data: Dict[str, Any] = Field(default_factory=dict)

class SetBonusSchema(BaseModel):
    """Schema for equipment set bonus information."""
    set_name: str
    pieces_equipped: int
    total_pieces: int
    bonus_level: int
    bonuses: Dict[str, Any]
    conflicts: List[str] = Field(default_factory=list)
    is_active: bool

class EquipmentBaseSchema(BaseModel):
    """Base schema for equipment with common fields."""
    id: str
    name: str
    description: str
    equipment_type: EquipmentType
    rarity: EquipmentRarity
    quality: EquipmentQuality
    durability: float = Field(ge=0, le=100)
    durability_status: DurabilityStatus
    base_value: int = Field(gt=0)
    current_value: int = Field(gt=0)
    abilities: List[AbilitySchema] = Field(default_factory=list)
    set_name: Optional[str] = None
    set_piece_number: Optional[int] = None
    is_equipped: bool = False
    created_at: datetime
    last_repair: Optional[datetime] = None

# Request Schemas
class CreateEquipmentRequest(BaseModel):
    """Request schema for creating new equipment."""
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=500)
    equipment_type: EquipmentType
    rarity: EquipmentRarity
    quality: EquipmentQuality
    base_value: int = Field(gt=0)
    set_name: Optional[str] = None
    set_piece_number: Optional[int] = None
    ability_count: Optional[int] = None  # Override auto-generation
    specific_abilities: Optional[List[str]] = None  # Force specific abilities

class RepairEquipmentRequest(BaseModel):
    """Request to repair equipment."""
    equipment_id: str = Field(..., description="ID of equipment to repair")
    repair_type: str = Field(pattern="^(player|professional)$")  # player = at repair station, professional = guaranteed
    materials: Optional[Dict[str, int]] = Field(default_factory=dict, description="Materials to use for repair")

class IdentifyEquipmentRequest(BaseModel):
    """Request schema for identifying equipment."""
    equipment_id: str
    target_level: int = Field(ge=1, le=100)
    character_level: int = Field(ge=1, le=100)
    
    @field_validator('target_level')
    @classmethod
    def validate_target_level(cls, v, info):
        values = info.data
        if 'character_level' in values and v > values['character_level']:
            raise ValueError('target_level cannot exceed character_level')
        return v

class EnchantEquipmentRequest(BaseModel):
    """Request schema for enchanting equipment."""
    equipment_id: str
    enchantment_id: str
    enchantment_type: str = Field(pattern="^(player|professional)$")
    materials: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class DisenchantEquipmentRequest(BaseModel):
    """Request schema for disenchanting equipment."""
    equipment_id: str
    character_skill_level: int = Field(ge=0, le=100)
    abilities_to_learn: Optional[List[str]] = None  # Specific abilities to target

class EquipmentQueryRequest(BaseModel):
    """Request schema for querying equipment."""
    character_id: Optional[str] = None
    equipment_type: Optional[EquipmentType] = None
    rarity: Optional[EquipmentRarity] = None
    quality: Optional[EquipmentQuality] = None
    is_equipped: Optional[bool] = None
    min_durability: Optional[float] = Field(ge=0, le=100)
    max_durability: Optional[float] = Field(ge=0, le=100)
    set_name: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

# Response Schemas
class EquipmentResponse(EquipmentBaseSchema):
    """Response schema for equipment information."""
    identification_level: int = 0
    revealed_abilities: List[AbilitySchema] = Field(default_factory=list)
    hidden_ability_count: int = 0
    set_bonus: Optional[SetBonusSchema] = None
    can_repair: bool = True
    repair_cost: Optional[int] = None
    next_identification_cost: Optional[int] = None

class RepairEquipmentResponse(BaseModel):
    """Response model for equipment repair operations."""
    success: bool
    equipment_id: str
    durability_before: float
    durability_after: float
    gold_cost: int
    new_condition: str

class IdentifyEquipmentResponse(BaseModel):
    """Response schema for equipment identification."""
    success: bool
    equipment_id: str
    identification_cost: int
    new_identification_level: int
    abilities_revealed: List[AbilitySchema]
    total_abilities_known: int
    total_abilities_hidden: int

class EnchantEquipmentResponse(BaseModel):
    """Response schema for equipment enchanting."""
    success: bool
    equipment_id: str
    enchantment_applied: Optional[str] = None
    enchantment_name: Optional[str] = None
    cost: int
    failure_reason: Optional[str] = None

class DisenchantEquipmentResponse(BaseModel):
    """Response schema for equipment disenchanting."""
    success: bool
    equipment_id: str
    enchantments_learned: List[str]
    enchantment_names: List[str]
    item_destroyed: bool = False
    failure_reason: Optional[str] = None

# Add new schema models for hybrid equipment system - order matters for forward references
class CreateEquipmentRequest(BaseModel):
    """Request model for creating equipment instances."""
    template_id: str = Field(..., description="Equipment template ID")
    owner_id: str = Field(..., description="Character ID who will own this equipment")
    quality_override: Optional[str] = Field(None, description="Override template quality tier")
    custom_name: Optional[str] = Field(None, description="Custom name for the equipment")

class EquipmentInstanceResponse(BaseModel):
    """Response model for equipment instance data."""
    id: str
    template_id: str
    owner_id: str
    is_equipped: bool = False
    equipment_slot: Optional[str] = None
    location: str = "inventory"
    durability: float
    custom_name: Optional[str] = None
    current_value: Optional[int] = None
    identification_level: int = 0
    created_at: datetime
    last_updated: datetime
    
    @classmethod
    def from_orm(cls, instance):
        """Create response from ORM instance."""
        return cls(
            id=instance.id,
            template_id=instance.template_id,
            owner_id=instance.owner_id,
            is_equipped=instance.is_equipped,
            equipment_slot=instance.equipment_slot,
            location=instance.location,
            durability=instance.durability,
            custom_name=instance.custom_name,
            current_value=instance.current_value,
            identification_level=instance.identification_level,
            created_at=instance.created_at,
            last_updated=instance.last_updated
        )

class EquipmentTemplateResponse(BaseModel):
    """Response model for equipment template information."""
    id: str
    name: str
    description: str
    item_type: str
    quality_tier: str
    rarity: str
    base_value: int
    equipment_slots: List[str]
    stat_modifiers: Dict[str, int]
    abilities: List[Dict[str, Any]]
    material: str
    weight: float
    compatible_enchantments: List[str]
    thematic_tags: List[str]
    restrictions: Dict[str, Any]
    
    @classmethod
    def from_template(cls, template):
        """Create response from template object."""
        return cls(
            id=template.id,
            name=template.name,
            description=template.description,
            item_type=template.item_type,
            quality_tier=template.quality_tier,
            rarity=template.rarity,
            base_value=template.base_value,
            equipment_slots=template.equipment_slots,
            stat_modifiers=template.stat_modifiers,
            abilities=template.abilities,
            material=template.material,
            weight=template.weight,
            compatible_enchantments=template.compatible_enchantments,
            thematic_tags=template.thematic_tags,
            restrictions=template.restrictions
        )
    
    @classmethod
    def from_template_info(cls, template_info):
        """Create response from template info dict."""
        template = template_info["template"]
        return cls.from_template(template)
    
    @classmethod
    def from_dict(cls, template_dict):
        """Create response from dictionary (for mock data)."""
        return cls(
            id=template_dict["id"],
            name=template_dict["name"],
            description=template_dict["description"],
            item_type=template_dict["item_type"],
            quality_tier=template_dict.get("quality_tiers", ["basic"])[0],  # Use first quality tier
            rarity="common",  # Default for mock data
            base_value=template_dict["base_value"],
            equipment_slots=["main_hand"] if template_dict["item_type"] == "weapon" else ["chest"],
            stat_modifiers={},
            abilities=[],
            material="unknown",
            weight=1.0,
            compatible_enchantments=[],
            thematic_tags=[],
            restrictions={}
        )

class EquipmentDetailsResponse(BaseModel):
    """Response model for detailed equipment information."""
    instance: EquipmentInstanceResponse
    template: EquipmentTemplateResponse
    condition_status: str
    condition_penalty: float
    current_stats: Dict[str, int]
    active_enchantments: List[Dict[str, Any]]
    estimated_repair_cost: int
    can_be_enchanted: bool
    
    @classmethod
    def from_details(cls, details):
        """Create response from service details dict."""
        return cls(
            instance=EquipmentInstanceResponse.from_orm(details["instance"]),
            template=EquipmentTemplateResponse.from_template(details["template"]),
            condition_status=details["condition_status"],
            condition_penalty=details["condition_penalty"],
            current_stats=details["current_stats"],
            active_enchantments=details["active_enchantments"],
            estimated_repair_cost=details["estimated_repair_cost"],
            can_be_enchanted=details["can_be_enchanted"]
        )

class EquipmentListResponse(BaseModel):
    """Response model for equipment lists."""
    equipment: List[EquipmentInstanceResponse]
    total_count: int
    limit: int
    offset: int
    filters: Dict[str, Any]

class SetBonusListResponse(BaseModel):
    """Response schema for set bonus information."""
    character_id: str
    active_sets: List[SetBonusSchema]
    available_sets: List[str]
    conflicts: List[str]
    total_bonus_value: Dict[str, Any]

# Error Schemas
class EquipmentErrorResponse(BaseModel):
    """Response schema for equipment operation errors."""
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    equipment_id: Optional[str] = None

# Utility Schemas
class EquipmentStatsResponse(BaseModel):
    """Response schema for equipment statistics."""
    total_equipment: int
    by_rarity: Dict[str, int]
    by_quality: Dict[str, int]
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    average_durability: float
    total_value: int
    repair_needed_count: int

class EquipmentOperationResponse(BaseModel):
    """Response model for equipment operations."""
    success: bool
    message: str
    equipment_id: str
    operation: str

class CharacterEquipmentResponse(BaseModel):
    """Response model for character equipment listings."""
    character_id: str
    equipment: List[EquipmentInstanceResponse]
    equipped_only: bool
    total_count: int

class EquipmentQueryFilters(BaseModel):
    """Query filters for equipment searches."""
    owner_id: Optional[str] = None
    template_id: Optional[str] = None
    is_equipped: Optional[bool] = None
    equipment_slot: Optional[str] = None
    min_durability: Optional[float] = None
    max_durability: Optional[float] = None

class TemplateQueryFilters(BaseModel):
    """Query filters for template searches."""
    item_type: Optional[str] = None
    quality_tier: Optional[str] = None
    max_level: Optional[int] = None

class TemplateListResponse(BaseModel):
    """Response model for template lists."""
    templates: List[EquipmentTemplateResponse]
    total_count: int
    filters: Dict[str, Any]

class TimeProcessingResponse(BaseModel):
    """Response model for time processing operations."""
    equipment_processed: int
    equipment_degraded: int
    character_id: Optional[str]
    message: str

__all__ = [
    'EquipmentRarity',
    'EquipmentQuality',
    'EquipmentType',
    'DurabilityStatus',
    'CreateEquipmentRequest',
    'RepairEquipmentRequest',
    'IdentifyEquipmentRequest',
    'EnchantEquipmentRequest',
    'DisenchantEquipmentRequest',
    'EquipmentQueryRequest',
    'EquipmentResponse',
    'RepairEquipmentResponse',
    'IdentifyEquipmentResponse',
    'EnchantEquipmentResponse',
    'DisenchantEquipmentResponse',
    'EquipmentListResponse',
    'SetBonusListResponse',
    'EquipmentErrorResponse',
    'EquipmentStatsResponse',
    'EquipmentInstanceResponse',
    'EquipmentTemplateResponse',
    'EquipmentDetailsResponse',
    'EquipmentOperationResponse',
    'CharacterEquipmentResponse',
    'EquipmentQueryFilters',
    'TemplateQueryFilters',
    'TemplateListResponse',
    'TimeProcessingResponse'
]

