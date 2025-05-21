"""
Magic system schemas.

This module contains Pydantic models for serializing and deserializing
magic system data for API input/output.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# ================ Enums ================

class MagicTypeEnum(str, Enum):
    """Magic types for API schema."""
    ELEMENTAL = "elemental"
    ARCANE = "arcane"
    DIVINE = "divine"
    DARK = "dark"
    LIGHT = "light"

class MagicSchoolEnum(str, Enum):
    """Magic schools for API schema."""
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    AIR = "air"
    ARCANE = "arcane"
    DIVINE = "divine"

class ComponentTypeEnum(str, Enum):
    """Spell component types for API schema."""
    VERBAL = "verbal"
    SOMATIC = "somatic"
    MATERIAL = "material"

class EffectTypeEnum(str, Enum):
    """Spell effect types for API schema."""
    DAMAGE = "damage"
    HEALING = "healing"
    BUFF = "buff"
    DEBUFF = "debuff"
    CONTROL = "control"
    UTILITY = "utility"

# ================ Base Schemas ================

class TimestampMixin(BaseModel):
    """Mixin for timestamps."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ================ Magic Ability Schemas ================

class MagicAbilityBase(BaseModel):
    """Base schema for magic abilities."""
    name: str = Field(..., description="Name of the magic ability")
    description: Optional[str] = Field(None, description="Description of the ability")
    magic_type: MagicTypeEnum = Field(MagicTypeEnum.ARCANE, description="Type of magic")
    power: float = Field(0.0, description="Power of the ability")
    cost: float = Field(0.0, description="Cost to use the ability")
    effects: Dict[str, Any] = Field(default_factory=dict, description="Effects of the ability")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Requirements to use the ability")

class MagicAbilityCreate(MagicAbilityBase):
    """Schema for creating a magic ability."""
    owner_id: Optional[int] = Field(None, description="ID of the owner character")

class MagicAbilityUpdate(BaseModel):
    """Schema for updating a magic ability."""
    name: Optional[str] = Field(None, description="Name of the magic ability")
    description: Optional[str] = Field(None, description="Description of the ability")
    magic_type: Optional[MagicTypeEnum] = Field(None, description="Type of magic")
    power: Optional[float] = Field(None, description="Power of the ability")
    cost: Optional[float] = Field(None, description="Cost to use the ability")
    effects: Optional[Dict[str, Any]] = Field(None, description="Effects of the ability")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Requirements to use the ability")
    owner_id: Optional[int] = Field(None, description="ID of the owner character")

class MagicAbilityResponse(MagicAbilityBase, TimestampMixin):
    """Schema for magic ability response."""
    id: int = Field(..., description="ID of the magic ability")
    owner_id: Optional[int] = Field(None, description="ID of the owner character")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True

# ================ Spell Schemas ================

class SpellBase(BaseModel):
    """Base schema for spells."""
    name: str = Field(..., description="Name of the spell")
    description: Optional[str] = Field(None, description="Description of the spell")
    school: MagicSchoolEnum = Field(MagicSchoolEnum.ARCANE, description="School of magic")
    mana_cost: float = Field(0.0, description="Mana cost to cast the spell")
    power: float = Field(0.0, description="Power of the spell")
    effects: Dict[str, Any] = Field(default_factory=dict, description="Effects of the spell")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Requirements to learn/cast the spell")

class SpellCreate(SpellBase):
    """Schema for creating a spell."""
    owner_id: Optional[int] = Field(None, description="ID of the owner character")

class SpellUpdate(BaseModel):
    """Schema for updating a spell."""
    name: Optional[str] = Field(None, description="Name of the spell")
    description: Optional[str] = Field(None, description="Description of the spell")
    school: Optional[MagicSchoolEnum] = Field(None, description="School of magic")
    mana_cost: Optional[float] = Field(None, description="Mana cost to cast the spell")
    power: Optional[float] = Field(None, description="Power of the spell")
    effects: Optional[Dict[str, Any]] = Field(None, description="Effects of the spell")
    requirements: Optional[Dict[str, Any]] = Field(None, description="Requirements to learn/cast the spell")
    owner_id: Optional[int] = Field(None, description="ID of the owner character")

class SpellResponse(SpellBase, TimestampMixin):
    """Schema for spell response."""
    id: int = Field(..., description="ID of the spell")
    owner_id: Optional[int] = Field(None, description="ID of the owner character")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True

# ================ Spell Component Schemas ================

class SpellComponentBase(BaseModel):
    """Base schema for spell components."""
    spell_id: int = Field(..., description="ID of the spell")
    component_type: ComponentTypeEnum = Field(..., description="Type of component")
    description: Optional[str] = Field(None, description="Description of the component")
    material_cost: Optional[float] = Field(None, description="Cost of material component")

class SpellComponentCreate(SpellComponentBase):
    """Schema for creating a spell component."""
    pass

class SpellComponentUpdate(BaseModel):
    """Schema for updating a spell component."""
    component_type: Optional[ComponentTypeEnum] = Field(None, description="Type of component")
    description: Optional[str] = Field(None, description="Description of the component")
    material_cost: Optional[float] = Field(None, description="Cost of material component")

class SpellComponentResponse(SpellComponentBase, TimestampMixin):
    """Schema for spell component response."""
    id: int = Field(..., description="ID of the spell component")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True

# ================ Spellbook Schemas ================

class SpellbookBase(BaseModel):
    """Base schema for spellbooks."""
    owner_id: int = Field(..., description="ID of the owner")
    owner_type: str = Field(..., description="Type of the owner (character, npc)")
    spells: Dict[str, Any] = Field(default_factory=dict, description="Spells in the spellbook")

class SpellbookCreate(SpellbookBase):
    """Schema for creating a spellbook."""
    pass

class SpellbookUpdate(BaseModel):
    """Schema for updating a spellbook."""
    spells: Optional[Dict[str, Any]] = Field(None, description="Spells in the spellbook")

class SpellbookResponse(SpellbookBase, TimestampMixin):
    """Schema for spellbook response."""
    id: int = Field(..., description="ID of the spellbook")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True

# ================ Spell Effect Schemas ================

class SpellEffectBase(BaseModel):
    """Base schema for spell effects."""
    spell_id: int = Field(..., description="ID of the spell")
    target_id: int = Field(..., description="ID of the target")
    target_type: str = Field(..., description="Type of the target (character, npc)")
    duration: int = Field(..., description="Duration of the effect in rounds")
    remaining_duration: int = Field(..., description="Remaining duration of the effect in rounds")
    effects: Dict[str, Any] = Field(..., description="Effect details")

class SpellEffectCreate(SpellEffectBase):
    """Schema for creating a spell effect."""
    pass

class SpellEffectUpdate(BaseModel):
    """Schema for updating a spell effect."""
    remaining_duration: Optional[int] = Field(None, description="Remaining duration of the effect in rounds")
    effects: Optional[Dict[str, Any]] = Field(None, description="Effect details")

class SpellEffectResponse(SpellEffectBase, TimestampMixin):
    """Schema for spell effect response."""
    id: int = Field(..., description="ID of the spell effect")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True

# ================ SpellSlot Schemas ================

class SpellSlotBase(BaseModel):
    """Base schema for spell slots."""
    character_id: int = Field(..., description="ID of the character")
    level: int = Field(..., description="Level of the spell slot")
    total: int = Field(..., description="Total number of slots")
    used: int = Field(0, description="Number of used slots")

class SpellSlotCreate(SpellSlotBase):
    """Schema for creating a spell slot."""
    pass

class SpellSlotUpdate(BaseModel):
    """Schema for updating a spell slot."""
    total: Optional[int] = Field(None, description="Total number of slots")
    used: Optional[int] = Field(None, description="Number of used slots")

class SpellSlotResponse(SpellSlotBase, TimestampMixin):
    """Schema for spell slot response."""
    id: int = Field(..., description="ID of the spell slot")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True

# ================ Spell Casting Schemas ================

class CastSpellRequest(BaseModel):
    """Schema for casting a spell."""
    spell_id: int = Field(..., description="ID of the spell to cast")
    caster_id: int = Field(..., description="ID of the character casting the spell")
    target_id: int = Field(..., description="ID of the target (character, NPC, etc.)")
    target_type: str = Field(..., description="Type of the target (character, npc, etc.)")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional data for the spell cast") 