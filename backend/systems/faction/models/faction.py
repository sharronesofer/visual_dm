"""
Faction Business Domain Models

Business logic models for the faction system according to Development Bible standards.
These models represent the pure business concepts and rules.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class FactionStatus(str, Enum):
    """Valid faction status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISBANDED = "disbanded"


class FactionData:
    """
    Core business domain model for faction data.
    
    This represents a faction as a business concept, separate from
    database persistence concerns.
    """
    
    def __init__(
        self,
        id: UUID,
        name: str,
        description: Optional[str] = None,
        status: str = FactionStatus.ACTIVE,
        properties: Optional[Dict[str, Any]] = None,
        hidden_ambition: int = 5,
        hidden_integrity: int = 5,
        hidden_discipline: int = 5,
        hidden_impulsivity: int = 5,
        hidden_pragmatism: int = 5,
        hidden_resilience: int = 5,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_active: bool = True
    ):
        """
        Initialize faction data with validation.
        
        Args:
            id: Unique faction identifier
            name: Faction name (required)
            description: Optional description
            status: Faction status (active, inactive, disbanded)
            properties: Optional properties dictionary
            hidden_ambition: Ambition level (1-10)
            hidden_integrity: Integrity level (1-10)
            hidden_discipline: Discipline level (1-10)
            hidden_impulsivity: Impulsivity level (1-10)
            hidden_pragmatism: Pragmatism level (1-10)
            hidden_resilience: Resilience level (1-10)
            created_at: Creation timestamp
            updated_at: Last update timestamp
            is_active: Whether faction is active
        """
        # Validate required fields
        if not name or not isinstance(name, str):
            raise ValueError("Faction name is required and must be a string")
        
        if len(name.strip()) == 0:
            raise ValueError("Faction name cannot be empty")
        
        # Validate hidden attributes (Development Bible: 1-10 range)
        for attr_name, value in [
            ("hidden_ambition", hidden_ambition),
            ("hidden_integrity", hidden_integrity),
            ("hidden_discipline", hidden_discipline),
            ("hidden_impulsivity", hidden_impulsivity),
            ("hidden_pragmatism", hidden_pragmatism),
            ("hidden_resilience", hidden_resilience)
        ]:
            if not isinstance(value, int) or value < 1 or value > 10:
                raise ValueError(f"{attr_name} must be an integer between 1 and 10")
        
        # Validate status
        if status not in [s.value for s in FactionStatus]:
            valid_statuses = [s.value for s in FactionStatus]
            raise ValueError(f"Status must be one of: {valid_statuses}")
        
        self.id = id
        self.name = name.strip()
        self.description = description.strip() if description else None
        self.status = status
        self.properties = properties or {}
        self.hidden_ambition = hidden_ambition
        self.hidden_integrity = hidden_integrity
        self.hidden_discipline = hidden_discipline
        self.hidden_impulsivity = hidden_impulsivity
        self.hidden_pragmatism = hidden_pragmatism
        self.hidden_resilience = hidden_resilience
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at
        self.is_active = is_active
    
    def get_hidden_attributes(self) -> Dict[str, int]:
        """Get all hidden attributes as a dictionary"""
        return {
            'hidden_ambition': self.hidden_ambition,
            'hidden_integrity': self.hidden_integrity,
            'hidden_discipline': self.hidden_discipline,
            'hidden_impulsivity': self.hidden_impulsivity,
            'hidden_pragmatism': self.hidden_pragmatism,
            'hidden_resilience': self.hidden_resilience
        }
    
    def update_hidden_attributes(self, attributes: Dict[str, int]) -> None:
        """
        Update hidden attributes with validation.
        
        Args:
            attributes: Dictionary of attribute name -> value pairs
            
        Raises:
            ValueError: If any attribute is out of valid range (1-10)
        """
        for attr_name, value in attributes.items():
            if attr_name in self.get_hidden_attributes():
                if not isinstance(value, int) or value < 1 or value > 10:
                    raise ValueError(f"{attr_name} must be an integer between 1 and 10")
                setattr(self, attr_name, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "properties": self.properties,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            **self.get_hidden_attributes()
        }
    
    def __repr__(self) -> str:
        return f"<FactionData(id={self.id}, name='{self.name}', status='{self.status}')>"


class CreateFactionData:
    """Business domain data for faction creation"""
    
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        status: str = FactionStatus.ACTIVE,
        properties: Optional[Dict[str, Any]] = None,
        **hidden_attributes
    ):
        """
        Initialize faction creation data.
        
        Args:
            name: Faction name
            description: Optional description
            status: Faction status
            properties: Optional properties
            **hidden_attributes: Hidden attribute values
        """
        if not name or not isinstance(name, str) or len(name.strip()) == 0:
            raise ValueError("Faction name is required")
            
        self.name = name.strip()
        self.description = description.strip() if description else None
        self.status = status
        self.properties = properties or {}
        self.hidden_attributes = hidden_attributes


class UpdateFactionData:
    """Business domain data for faction updates"""
    
    def __init__(self, **update_fields):
        """
        Initialize faction update data.
        
        Args:
            **update_fields: Fields to update
        """
        # Validate any hidden attributes if present
        for attr_name, value in update_fields.items():
            if attr_name.startswith('hidden_') and value is not None:
                if not isinstance(value, int) or value < 1 or value > 10:
                    raise ValueError(f"{attr_name} must be an integer between 1 and 10")
        
        self.update_fields = update_fields
    
    def get_fields(self) -> Dict[str, Any]:
        """Get update fields"""
        return self.update_fields


# Import infrastructure models for backwards compatibility
from backend.infrastructure.models.faction.models import (
    FactionEntity,
    FactionBaseModel,
    CreateFactionRequest,
    UpdateFactionRequest,
    FactionResponse,
    FactionListResponse
)

# Create legacy aliases
Faction = FactionData
FactionRelationship = FactionEntity  # Placeholder
FactionMembership = FactionEntity    # Placeholder

__all__ = [
    "FactionData",
    "FactionStatus", 
    "CreateFactionData",
    "UpdateFactionData",
    "Faction",  # Legacy alias
    "FactionEntity", 
    "FactionBaseModel",
    "FactionRelationship",
    "FactionMembership",
    "CreateFactionRequest",
    "UpdateFactionRequest", 
    "FactionResponse",
    "FactionListResponse"
]
