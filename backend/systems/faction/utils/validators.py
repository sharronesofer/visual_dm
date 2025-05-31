"""
Faction validation utility functions.

This module provides utility functions for validating faction data.
"""

from typing import Optional
from backend.systems.faction.schemas.faction_types import DiplomaticStance

class FactionValidationError(Exception):
    """Exception raised for faction validation errors."""

def validate_faction_name(name: str) -> bool:
    """
    Validate faction name.
    
    Args:
        name: The faction name to validate
        
    Returns:
        True if name is valid
        
    Raises:
        FactionValidationError: If name is invalid
    """
    if not name or not isinstance(name, str):
        raise FactionValidationError("Faction name must be a non-empty string")
    
    if len(name) < 2:
        raise FactionValidationError("Faction name must be at least 2 characters long")
        
    if len(name) > 100:
        raise FactionValidationError("Faction name cannot exceed 100 characters")
    
    return True

def validate_faction_influence(influence: float) -> bool:
    """
    Validate faction influence value.
    
    Args:
        influence: The influence value to validate
        
    Returns:
        True if influence is valid
        
    Raises:
        FactionValidationError: If influence is invalid
    """
    if not isinstance(influence, (int, float)):
        raise FactionValidationError("Influence must be a number")
    
    if influence < 0.0 or influence > 100.0:
        raise FactionValidationError("Influence must be between 0 and 100")
    
    return True

def validate_diplomatic_stance(stance: str, allow_none: bool = False) -> bool:
    """
    Validate diplomatic stance value.
    
    Args:
        stance: The diplomatic stance to validate
        allow_none: Whether None is allowed
        
    Returns:
        True if stance is valid
        
    Raises:
        FactionValidationError: If stance is invalid
    """
    if stance is None:
        if allow_none:
            return True
        raise FactionValidationError("Diplomatic stance cannot be None")
    
    try:
        valid_stances = [s.value for s in DiplomaticStance]
        if stance not in valid_stances:
            valid_options = ", ".join(valid_stances)
            raise FactionValidationError(
                f"Invalid diplomatic stance '{stance}'. "
                f"Must be one of: {valid_options}"
            )
    except (AttributeError, TypeError):
        raise FactionValidationError(
            "Invalid diplomatic stance format. Must be a string value."
        )
    
    return True 