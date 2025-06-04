"""
Pydantic schemas for enchanting system data validation.

Provides schemas for API requests, responses, and data validation
for the learn-by-disenchanting enchanting system.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set
from uuid import UUID

from pydantic import BaseModel, Field, validator

class EnchantmentSchema(BaseModel):
    """Schema for enchantment definition data."""
    id: str = Field(..., description="Unique identifier for the enchantment")
    name: str = Field(..., description="Display name of the enchantment")
    description: str = Field(..., description="Description of what the enchantment does")
    school: str = Field(..., description="School of magic (elemental, protective, etc.)")
    rarity: str = Field(..., description="Rarity level (basic, military, noble, legendary)")
    min_arcane_manipulation: int = Field(ge=0, le=10, description="Minimum Arcane Manipulation ability required")
    base_cost: int = Field(ge=0, description="Base gold cost to apply this enchantment")
    min_item_quality: str = Field(..., description="Minimum item quality required")
    compatible_item_types: Set[str] = Field(..., description="Item types this enchantment can be applied to")
    thematic_tags: Set[str] = Field(default_factory=set, description="Thematic tags for set detection")
    power_scaling: Dict[str, float] = Field(default_factory=dict, description="How power scales with mastery")
    
    @validator('school')
    def validate_school(cls, v):
        valid_schools = {'elemental', 'protective', 'enhancement', 'utility', 'combat', 'mystical'}
        if v not in valid_schools:
            raise ValueError(f"School must be one of: {valid_schools}")
        return v
    
    @validator('rarity')
    def validate_rarity(cls, v):
        valid_rarities = {'basic', 'military', 'noble', 'legendary'}
        if v not in valid_rarities:
            raise ValueError(f"Rarity must be one of: {valid_rarities}")
        return v
    
    @validator('min_item_quality')
    def validate_quality(cls, v):
        valid_qualities = {'basic', 'military', 'noble'}
        if v not in valid_qualities:
            raise ValueError(f"Quality must be one of: {valid_qualities}")
        return v

class LearnedEnchantmentSchema(BaseModel):
    """Schema for a character's learned enchantment."""
    enchantment_id: str = Field(..., description="ID of the learned enchantment")
    learned_at: datetime = Field(..., description="When the enchantment was learned")
    learned_from_item: str = Field(..., description="Name of the item it was learned from")
    mastery_level: int = Field(ge=0, le=10, description="Current mastery level (0-10)")
    times_applied: int = Field(ge=0, description="Number of times successfully applied")
    last_applied: Optional[datetime] = Field(None, description="When last successfully applied")

class CharacterEnchantingProfileSchema(BaseModel):
    """Schema for a character's complete enchanting profile."""
    character_id: UUID = Field(..., description="Character UUID")
    learned_enchantments: Dict[str, LearnedEnchantmentSchema] = Field(
        default_factory=dict, 
        description="Dictionary of learned enchantments by ID"
    )
    total_items_disenchanted: int = Field(ge=0, description="Total items disenchanted")
    successful_disenchantments: int = Field(ge=0, description="Successful disenchantment attempts")
    successful_applications: int = Field(ge=0, description="Successful enchantment applications")
    failed_applications: int = Field(ge=0, description="Failed enchantment applications")
    preferred_school: Optional[str] = Field(None, description="Character's preferred enchantment school")
    notes: List[str] = Field(default_factory=list, description="Character enchanting notes")
    
    @validator('preferred_school')
    def validate_preferred_school(cls, v):
        if v is not None:
            valid_schools = {'elemental', 'protective', 'enhancement', 'utility', 'combat', 'mystical'}
            if v not in valid_schools:
                raise ValueError(f"Preferred school must be one of: {valid_schools}")
        return v

class DisenchantmentRequestSchema(BaseModel):
    """Schema for disenchantment API requests."""
    character_id: UUID = Field(..., description="Character performing the disenchantment")
    item_id: UUID = Field(..., description="UUID of the item to disenchant")
    item_data: Dict = Field(..., description="Complete item data including enchantments")
    arcane_manipulation_level: int = Field(ge=0, le=10, description="Character's Arcane Manipulation level")
    character_level: int = Field(ge=1, le=20, description="Character's overall level")
    target_enchantment: Optional[str] = Field(None, description="Specific enchantment to try to learn")
    
    @validator('item_data')
    def validate_item_data(cls, v):
        required_fields = {'name', 'quality', 'enchantments'}
        if not all(field in v for field in required_fields):
            raise ValueError(f"Item data must contain: {required_fields}")
        
        if not isinstance(v['enchantments'], list):
            raise ValueError("Enchantments must be a list")
        
        if len(v['enchantments']) == 0:
            raise ValueError("Item must have at least one enchantment to disenchant")
        
        return v

class EnchantmentApplicationSchema(BaseModel):
    """Schema for enchantment application API requests."""
    character_id: UUID = Field(..., description="Character applying the enchantment")
    item_id: UUID = Field(..., description="UUID of the item to enchant")
    item_data: Dict = Field(..., description="Complete item data")
    enchantment_id: str = Field(..., description="ID of the enchantment to apply")
    gold_available: int = Field(ge=0, description="Gold available for the enchantment")
    
    @validator('item_data')
    def validate_item_data_for_enchanting(cls, v):
        required_fields = {'name', 'quality', 'type'}
        if not all(field in v for field in required_fields):
            raise ValueError(f"Item data must contain: {required_fields}")
        return v

class DisenchantmentResultSchema(BaseModel):
    """Schema for disenchantment results."""
    success: bool = Field(..., description="Whether the disenchantment was successful")
    outcome: str = Field(..., description="Detailed outcome description")
    enchantment_learned: Optional[str] = Field(None, description="ID of enchantment learned, if any")
    item_destroyed: bool = Field(..., description="Whether the item was destroyed")
    experience_gained: int = Field(ge=0, description="Experience points gained")
    additional_consequences: List[str] = Field(default_factory=list, description="Additional effects")
    attempt_id: UUID = Field(..., description="Unique ID for this attempt")

class EnchantmentApplicationResultSchema(BaseModel):
    """Schema for enchantment application results."""
    success: bool = Field(..., description="Whether the enchantment was successfully applied")
    cost_paid: int = Field(ge=0, description="Gold cost paid")
    final_power_level: Optional[int] = Field(None, description="Final power level if successful")
    mastery_increased: bool = Field(default=False, description="Whether mastery level increased")
    failure_reason: Optional[str] = Field(None, description="Reason for failure, if applicable")
    materials_lost: bool = Field(default=False, description="Whether materials were lost on failure")
    application_id: UUID = Field(..., description="Unique ID for this application")

class EnchantmentAvailabilitySchema(BaseModel):
    """Schema for checking enchantment availability for an item."""
    enchantment_id: str = Field(..., description="Enchantment ID")
    name: str = Field(..., description="Enchantment name")
    description: str = Field(..., description="What the enchantment does")
    school: str = Field(..., description="School of magic")
    rarity: str = Field(..., description="Rarity level")
    cost: int = Field(ge=0, description="Gold cost to apply")
    mastery_level: int = Field(ge=0, le=10, description="Character's mastery level")
    times_applied: int = Field(ge=0, description="Times character has applied this")
    success_rate: float = Field(ge=0.0, le=100.0, description="Estimated success rate percentage")

class CharacterEnchantingStatsSchema(BaseModel):
    """Schema for character enchanting statistics."""
    character_id: UUID = Field(..., description="Character UUID")
    total_enchantments_learned: int = Field(ge=0, description="Total unique enchantments learned")
    total_items_disenchanted: int = Field(ge=0, description="Total items disenchanted")
    successful_disenchantments: int = Field(ge=0, description="Successful disenchantment attempts")
    successful_applications: int = Field(ge=0, description="Successful enchantment applications")
    failed_applications: int = Field(ge=0, description="Failed enchantment applications")
    disenchantment_success_rate: float = Field(ge=0.0, le=100.0, description="Disenchantment success rate %")
    application_success_rate: float = Field(ge=0.0, le=100.0, description="Application success rate %")
    preferred_school: Optional[str] = Field(None, description="Most used enchantment school")
    schools_learned: Dict[str, int] = Field(default_factory=dict, description="Enchantments learned per school")
    recent_disenchantments_week: int = Field(ge=0, description="Disenchantments in last 7 days")
    recent_applications_week: int = Field(ge=0, description="Applications in last 7 days")
    most_experienced_school: Optional[str] = Field(None, description="School with most enchantments learned")

class EnchantmentHistoryEntrySchema(BaseModel):
    """Schema for enchantment history entries."""
    id: UUID = Field(..., description="Unique entry ID")
    timestamp: datetime = Field(..., description="When the action occurred")
    action_type: str = Field(..., description="Type of action (disenchant, apply)")
    item_name: str = Field(..., description="Name of the item involved")
    enchantment_id: Optional[str] = Field(None, description="Enchantment involved")
    enchantment_name: Optional[str] = Field(None, description="Enchantment name")
    success: bool = Field(..., description="Whether the action succeeded")
    details: Dict = Field(default_factory=dict, description="Additional action details")
    
    @validator('action_type')
    def validate_action_type(cls, v):
        valid_actions = {'disenchant', 'apply'}
        if v not in valid_actions:
            raise ValueError(f"Action type must be one of: {valid_actions}")
        return v 