"""
Character API Schemas

This module defines the Pydantic schemas for character resources in the API.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime
from ..models.base import BaseEntity, TimestampMixin

# Enums for character attributes
class CharacterClass(str, Enum):
    BARBARIAN = "barbarian"
    BARD = "bard"
    CLERIC = "cleric"
    DRUID = "druid"
    FIGHTER = "fighter"
    MONK = "monk"
    PALADIN = "paladin"
    RANGER = "ranger"
    ROGUE = "rogue"
    SORCERER = "sorcerer"
    WARLOCK = "warlock"
    WIZARD = "wizard"
    
class CharacterRace(str, Enum):
    HUMAN = "human"
    ELF = "elf"
    DWARF = "dwarf"
    HALFLING = "halfling"
    GNOME = "gnome"
    HALF_ELF = "half-elf"
    HALF_ORC = "half-orc"
    TIEFLING = "tiefling"
    DRAGONBORN = "dragonborn"

class Alignment(str, Enum):
    LAWFUL_GOOD = "lawful-good"
    NEUTRAL_GOOD = "neutral-good"
    CHAOTIC_GOOD = "chaotic-good"
    LAWFUL_NEUTRAL = "lawful-neutral"
    TRUE_NEUTRAL = "true-neutral"
    CHAOTIC_NEUTRAL = "chaotic-neutral"
    LAWFUL_EVIL = "lawful-evil"
    NEUTRAL_EVIL = "neutral-evil"
    CHAOTIC_EVIL = "chaotic-evil"
    
# Base classes for character attributes
class Ability(BaseModel):
    """Character ability scores"""
    strength: int = Field(10, ge=1, le=30)
    dexterity: int = Field(10, ge=1, le=30)
    constitution: int = Field(10, ge=1, le=30)
    intelligence: int = Field(10, ge=1, le=30)
    wisdom: int = Field(10, ge=1, le=30)
    charisma: int = Field(10, ge=1, le=30)
    
    @validator('*')
    def validate_ability_score(cls, v):
        """Validate ability scores are within proper D&D range"""
        if v < 1 or v > 30:
            raise ValueError('Ability scores must be between 1 and 30')
        return v

class ClassLevel(BaseModel):
    """Character class and level"""
    class_type: CharacterClass
    level: int = Field(1, ge=1, le=20)
    
    @validator('level')
    def validate_level(cls, v):
        """Validate levels are within proper D&D range"""
        if v < 1 or v > 20:
            raise ValueError('Level must be between 1 and 20')
        return v

class Item(BaseModel):
    """Basic item model"""
    id: str = Field(..., description="Item ID")
    name: str = Field(..., description="Item name")
    quantity: int = Field(1, ge=0, description="Number of items")
    description: Optional[str] = None

class Spell(BaseModel):
    """Basic spell model"""
    id: str = Field(..., description="Spell ID")
    name: str = Field(..., description="Spell name")
    level: int = Field(..., ge=0, le=9, description="Spell level (0 for cantrips)")
    description: Optional[str] = None
    
# Character schemas
class CharacterBase(BaseModel):
    """Base fields for character creation and updates"""
    name: str = Field(..., min_length=1, max_length=100, description="Character name")
    race: CharacterRace = Field(..., description="Character race")
    classes: List[ClassLevel] = Field(..., description="Character classes and levels")
    abilities: Ability = Field(..., description="Ability scores")
    background: Optional[str] = Field(None, description="Character background")
    alignment: Optional[Alignment] = Field(None, description="Character alignment")
    experience: Optional[int] = Field(0, ge=0, description="Experience points")
    hit_points: Optional[int] = Field(None, description="Current hit points")
    max_hit_points: Optional[int] = Field(None, description="Maximum hit points")
    armor_class: Optional[int] = Field(None, description="Armor class")
    initiative: Optional[int] = Field(None, description="Initiative modifier")
    speed: Optional[int] = Field(None, description="Walking speed in feet")
    personality_traits: Optional[str] = Field(None, description="Personality traits")
    ideals: Optional[str] = Field(None, description="Character ideals")
    bonds: Optional[str] = Field(None, description="Character bonds")
    flaws: Optional[str] = Field(None, description="Character flaws")
    
    @validator('classes')
    def validate_classes(cls, classes):
        """Validate that at least one class is provided"""
        if not classes or len(classes) == 0:
            raise ValueError('At least one class must be provided')
        
        # Calculate total level across all classes
        total_level = sum(c.level for c in classes)
        if total_level > 20:
            raise ValueError('Total character level cannot exceed 20')
            
        return classes

class CharacterCreate(CharacterBase):
    """Schema for creating a new character"""
    campaign_id: Optional[str] = Field(None, description="ID of the campaign this character belongs to")
    user_id: Optional[str] = Field(None, description="ID of the user who owns this character")
    inventory: Optional[List[Item]] = Field([], description="Character inventory")
    spells: Optional[List[Spell]] = Field([], description="Character spell list")

class CharacterUpdate(BaseModel):
    """Schema for updating a character"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Character name")
    race: Optional[CharacterRace] = Field(None, description="Character race")
    classes: Optional[List[ClassLevel]] = Field(None, description="Character classes and levels")
    abilities: Optional[Ability] = Field(None, description="Ability scores")
    background: Optional[str] = Field(None, description="Character background")
    alignment: Optional[Alignment] = Field(None, description="Character alignment")
    experience: Optional[int] = Field(None, ge=0, description="Experience points")
    hit_points: Optional[int] = Field(None, description="Current hit points")
    max_hit_points: Optional[int] = Field(None, description="Maximum hit points")
    armor_class: Optional[int] = Field(None, description="Armor class")
    initiative: Optional[int] = Field(None, description="Initiative modifier")
    speed: Optional[int] = Field(None, description="Walking speed in feet")
    personality_traits: Optional[str] = Field(None, description="Personality traits")
    ideals: Optional[str] = Field(None, description="Character ideals")
    bonds: Optional[str] = Field(None, description="Character bonds")
    flaws: Optional[str] = Field(None, description="Character flaws")
    campaign_id: Optional[str] = Field(None, description="ID of the campaign this character belongs to")
    inventory: Optional[List[Item]] = Field(None, description="Character inventory")
    spells: Optional[List[Spell]] = Field(None, description="Character spell list")
    
    @validator('classes')
    def validate_classes(cls, classes):
        """Validate class levels for an update"""
        if classes is None or len(classes) == 0:
            return classes
            
        # Calculate total level across all classes
        total_level = sum(c.level for c in classes)
        if total_level > 20:
            raise ValueError('Total character level cannot exceed 20')
            
        return classes

class Character(BaseEntity, CharacterBase):
    """Complete character model with all fields"""
    campaign_id: Optional[str] = Field(None, description="ID of the campaign this character belongs to")
    user_id: str = Field(..., description="ID of the user who owns this character")
    inventory: List[Item] = Field([], description="Character inventory")
    spells: List[Spell] = Field([], description="Character spell list")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Tordek",
                "race": "dwarf",
                "classes": [
                    {"class_type": "fighter", "level": 5}
                ],
                "abilities": {
                    "strength": 16,
                    "dexterity": 12,
                    "constitution": 16,
                    "intelligence": 10,
                    "wisdom": 12,
                    "charisma": 8
                },
                "background": "Soldier",
                "alignment": "lawful-good",
                "experience": 5600,
                "hit_points": 45,
                "max_hit_points": 48,
                "armor_class": 18,
                "initiative": 1,
                "speed": 25,
                "created_at": "2023-09-15T12:00:00Z",
                "updated_at": "2023-09-15T12:00:00Z",
                "campaign_id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440002",
                "inventory": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440003",
                        "name": "Battleaxe",
                        "quantity": 1,
                        "description": "Martial melee weapon"
                    }
                ],
                "spells": []
            }
        } 