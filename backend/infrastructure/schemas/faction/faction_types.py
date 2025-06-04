"""
Faction system - Faction Types.
Updated to use JSON-based configurations instead of hard-coded enums.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from backend.infrastructure.data.json_config_loader import (
    get_config_loader, 
    FactionType, 
    FactionAlignment, 
    DiplomaticStance,
    ConfigurationType,
    validate_config_id
)

# Get the configuration loader
config_loader = get_config_loader()

def get_valid_faction_types() -> List[str]:
    """Get list of valid faction type IDs"""
    return config_loader.get_faction_type_ids()

def get_valid_faction_alignments() -> List[str]:
    """Get list of valid faction alignment IDs"""
    return config_loader.get_alignment_ids()

def get_valid_diplomatic_stances() -> List[str]:
    """Get list of valid diplomatic stance IDs"""
    return config_loader.get_diplomatic_stance_ids()

def get_faction_type_data(faction_type_id: str) -> Optional[Dict[str, Any]]:
    """Get faction type configuration data"""
    return config_loader.get_faction_type(faction_type_id)

def get_faction_alignment_data(alignment_id: str) -> Optional[Dict[str, Any]]:
    """Get faction alignment configuration data"""
    return config_loader.get_faction_alignment(alignment_id)

def get_diplomatic_stance_data(stance_id: str) -> Optional[Dict[str, Any]]:
    """Get diplomatic stance configuration data"""
    return config_loader.get_diplomatic_stance(stance_id)

def validate_faction_type(faction_type_id: str) -> bool:
    """Validate a faction type ID"""
    return validate_config_id(faction_type_id, ConfigurationType.FACTION_TYPE)

def validate_faction_alignment(alignment_id: str) -> bool:
    """Validate a faction alignment ID"""
    return validate_config_id(alignment_id, ConfigurationType.FACTION_ALIGNMENT)

def validate_diplomatic_stance(stance_id: str) -> bool:
    """Validate a diplomatic stance ID"""
    return validate_config_id(stance_id, ConfigurationType.DIPLOMATIC_STANCE)

class FactionSchema(BaseModel):
    """Pydantic schema for faction data validation"""
    id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    faction_type: str = Field(..., description="Faction type ID from JSON configuration")
    alignment: Optional[str] = Field(default="true_neutral", description="Faction alignment ID from JSON configuration")
    description: Optional[str] = None
    leader: Optional[str] = None
    headquarters: Optional[str] = None
    influence: Optional[int] = Field(default=1, ge=1, le=10)
    resources: Optional[Dict[str, Any]] = None
    diplomatic_relations: Optional[Dict[str, str]] = None
    
    def model_validate(cls, values):
        """Custom validation for faction data"""
        if isinstance(values, dict):
            faction_type = values.get('faction_type')
            if faction_type and not validate_faction_type(faction_type):
                raise ValueError(f"Invalid faction type: {faction_type}")
            
            alignment = values.get('alignment')
            if alignment and not validate_faction_alignment(alignment):
                raise ValueError(f"Invalid faction alignment: {alignment}")
            
            diplomatic_relations = values.get('diplomatic_relations', {})
            for relation_faction, stance in diplomatic_relations.items():
                if not validate_diplomatic_stance(stance):
                    raise ValueError(f"Invalid diplomatic stance: {stance}")
        
        return values
    
    class Config:
        json_encoders = {
            # Custom encoders if needed
        }
        schema_extra = {
            "example": {
                "name": "The Silver Merchants",
                "faction_type": "merchant",
                "alignment": "lawful_neutral",
                "description": "A powerful merchant consortium controlling trade routes",
                "leader": "Merchant Prince Aldric",
                "headquarters": "Port Merchants' Hall",
                "influence": 7,
                "resources": {
                    "gold": 50000,
                    "trade_routes": 12,
                    "ships": 8
                },
                "diplomatic_relations": {
                    "royal_guard": "friendly",
                    "thieves_guild": "hostile"
                }
            }
        }

class CreateFactionRequest(BaseModel):
    """Request schema for creating a new faction"""
    name: str = Field(..., min_length=1, max_length=200)
    faction_type: str = Field(..., description="Must be a valid faction type ID")
    alignment: str = Field(default="true_neutral", description="Must be a valid alignment ID")
    description: Optional[str] = Field(None, max_length=1000)
    leader: Optional[str] = Field(None, max_length=200)
    headquarters: Optional[str] = Field(None, max_length=200)
    influence: int = Field(default=1, ge=1, le=10)
    
    def model_validate(cls, values):
        """Validate faction type and alignment against JSON configurations"""
        if isinstance(values, dict):
            faction_type = values.get('faction_type')
            if faction_type and not validate_faction_type(faction_type):
                valid_types = get_valid_faction_types()
                raise ValueError(f"Invalid faction type '{faction_type}'. Valid types: {valid_types}")
            
            alignment = values.get('alignment')
            if alignment and not validate_faction_alignment(alignment):
                valid_alignments = get_valid_faction_alignments()
                raise ValueError(f"Invalid alignment '{alignment}'. Valid alignments: {valid_alignments}")
        
        return values

class UpdateFactionRequest(BaseModel):
    """Request schema for updating a faction"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    faction_type: Optional[str] = Field(None, description="Must be a valid faction type ID")
    alignment: Optional[str] = Field(None, description="Must be a valid alignment ID")
    description: Optional[str] = Field(None, max_length=1000)
    leader: Optional[str] = Field(None, max_length=200)
    headquarters: Optional[str] = Field(None, max_length=200)
    influence: Optional[int] = Field(None, ge=1, le=10)
    
    def model_validate(cls, values):
        """Validate faction type and alignment against JSON configurations"""
        if isinstance(values, dict):
            faction_type = values.get('faction_type')
            if faction_type and not validate_faction_type(faction_type):
                valid_types = get_valid_faction_types()
                raise ValueError(f"Invalid faction type '{faction_type}'. Valid types: {valid_types}")
            
            alignment = values.get('alignment')
            if alignment and not validate_faction_alignment(alignment):
                valid_alignments = get_valid_faction_alignments()
                raise ValueError(f"Invalid alignment '{alignment}'. Valid alignments: {valid_alignments}")
        
        return values

class FactionRelationshipRequest(BaseModel):
    """Request schema for updating faction relationships"""
    target_faction_id: str = Field(..., description="ID of the faction to establish relationship with")
    diplomatic_stance: str = Field(..., description="Must be a valid diplomatic stance ID")
    
    def model_validate(cls, values):
        """Validate diplomatic stance against JSON configurations"""
        if isinstance(values, dict):
            stance = values.get('diplomatic_stance')
            if stance and not validate_diplomatic_stance(stance):
                valid_stances = get_valid_diplomatic_stances()
                raise ValueError(f"Invalid diplomatic stance '{stance}'. Valid stances: {valid_stances}")
        
        return values

# Helper functions for getting configuration details
def get_faction_type_attributes(faction_type_id: str) -> Optional[Dict[str, Any]]:
    """Get the attributes for a faction type (hierarchy, territoriality, etc.)"""
    faction_data = get_faction_type_data(faction_type_id)
    return faction_data.get('attributes') if faction_data else None

def get_faction_type_goals(faction_type_id: str) -> Optional[List[str]]:
    """Get typical goals for a faction type"""
    faction_data = get_faction_type_data(faction_type_id)
    return faction_data.get('typical_goals') if faction_data else None

def get_alignment_modifiers(alignment_id: str) -> Optional[Dict[str, float]]:
    """Get diplomatic modifiers for an alignment"""
    alignment_data = get_faction_alignment_data(alignment_id)
    return alignment_data.get('diplomatic_modifiers') if alignment_data else None

def get_stance_trade_modifier(stance_id: str) -> Optional[float]:
    """Get trade modifier for a diplomatic stance"""
    stance_data = get_diplomatic_stance_data(stance_id)
    return stance_data.get('trade_modifier') if stance_data else None

def get_compatible_faction_types(alignment_id: str) -> Optional[List[str]]:
    """Get faction types compatible with an alignment"""
    alignment_data = get_faction_alignment_data(alignment_id)
    return alignment_data.get('faction_compatibility') if alignment_data else None

# Backwards compatibility exports
__all__ = [
    "FactionType", "FactionAlignment", "DiplomaticStance", "FactionSchema",
    "CreateFactionRequest", "UpdateFactionRequest", "FactionRelationshipRequest",
    "get_valid_faction_types", "get_valid_faction_alignments", "get_valid_diplomatic_stances",
    "get_faction_type_data", "get_faction_alignment_data", "get_diplomatic_stance_data",
    "validate_faction_type", "validate_faction_alignment", "validate_diplomatic_stance",
    "get_faction_type_attributes", "get_faction_type_goals", "get_alignment_modifiers",
    "get_stance_trade_modifier", "get_compatible_faction_types"
]
