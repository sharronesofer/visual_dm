"""
Faction System Validators

Validation utilities for faction data following Development Bible standards.
"""

import re
from typing import Optional, Dict, Any, List
from backend.infrastructure.schemas.faction.faction_types import DiplomaticStance
from backend.infrastructure.utils.faction.faction_utils import (
    generate_faction_hidden_attributes,
    validate_hidden_attributes
)

class FactionValidationError(Exception):
    """Exception raised for faction validation errors."""

def sanitize_string_input(value: str, max_length: int = 255, allow_html: bool = False) -> str:
    """
    Sanitize string input to prevent XSS and other injection attacks.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_html: Whether to allow HTML tags (default: False)
        
    Returns:
        Sanitized string
        
    Raises:
        FactionValidationError: If input is invalid
    """
    if not isinstance(value, str):
        raise FactionValidationError("Input must be a string")
    
    # Strip whitespace
    sanitized = value.strip()
    
    # Check length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    if not allow_html:
        # Remove potential HTML/XML tags
        sanitized = re.sub(r'<[^>]*>', '', sanitized)
        
        # Remove script-like content
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
    
    # Remove null bytes and other control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
    
    return sanitized

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
    
    # Sanitize the name
    sanitized_name = sanitize_string_input(name, max_length=100)
    
    if len(sanitized_name) < 2:
        raise FactionValidationError("Faction name must be at least 2 characters long")
        
    if len(sanitized_name) > 100:
        raise FactionValidationError("Faction name cannot exceed 100 characters")
    
    # Check for valid characters (letters, numbers, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z0-9\s\-']+$", sanitized_name):
        raise FactionValidationError("Faction name contains invalid characters")
    
    return True

def validate_faction_description(description: str) -> bool:
    """
    Validate faction description.
    
    Args:
        description: The faction description to validate
        
    Returns:
        True if description is valid
        
    Raises:
        FactionValidationError: If description is invalid
    """
    if description is None:
        return True  # Optional field
        
    if not isinstance(description, str):
        raise FactionValidationError("Faction description must be a string")
    
    # Sanitize the description
    sanitized_desc = sanitize_string_input(description, max_length=1000)
    
    if len(sanitized_desc) > 1000:
        raise FactionValidationError("Faction description cannot exceed 1000 characters")
    
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

def validate_hidden_attribute(value: Any, attribute_name: str) -> int:
    """
    Validate and sanitize a hidden attribute value.
    
    Args:
        value: The attribute value to validate
        attribute_name: Name of the attribute for error messages
        
    Returns:
        Validated and clamped attribute value
        
    Raises:
        FactionValidationError: If value cannot be converted to valid range
    """
    try:
        # Convert to integer
        int_value = int(float(value)) if value is not None else 5
        
        # Clamp to valid range (1-10) as per Development Bible
        clamped_value = max(1, min(10, int_value))
        
        return clamped_value
        
    except (ValueError, TypeError):
        raise FactionValidationError(f"Invalid {attribute_name} value: must be a number between 1 and 10")

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

def validate_faction_data(faction_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize faction data for creation or update"""
    
    # Required fields validation
    if not faction_data.get("name"):
        raise ValueError("Faction name is required")
    
    if len(faction_data["name"]) > 255:
        raise ValueError("Faction name cannot exceed 255 characters")
    
    # Optional fields with defaults
    validated_data = {
        "name": faction_data["name"].strip(),
        "description": faction_data.get("description", "").strip() if faction_data.get("description") else None,
        "status": faction_data.get("status", "active"),
        "properties": faction_data.get("properties", {})
    }
    
    # Validate status
    valid_statuses = ["active", "inactive", "disbanded"]
    if validated_data["status"] not in valid_statuses:
        raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
    
    # Validate hidden attributes if provided
    hidden_attrs = {}
    for attr_name in ["hidden_ambition", "hidden_integrity", "hidden_discipline", 
                     "hidden_impulsivity", "hidden_pragmatism", "hidden_resilience"]:
        if attr_name in faction_data:
            hidden_attrs[attr_name] = faction_data[attr_name]
    
    if hidden_attrs:
        validated_attrs = validate_hidden_attributes(hidden_attrs)
        validated_data.update(validated_attrs)
    
    return validated_data

def sanitize_properties_dict(properties: Dict[str, Any], max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
    """
    Sanitize a properties dictionary to prevent injection attacks.
    
    Args:
        properties: Dictionary to sanitize
        max_depth: Maximum nesting depth allowed
        current_depth: Current nesting level
        
    Returns:
        Sanitized properties dictionary
        
    Raises:
        FactionValidationError: If structure is too complex or contains unsafe data
    """
    if current_depth > max_depth:
        raise FactionValidationError("Properties dictionary is too deeply nested")
    
    if not isinstance(properties, dict):
        raise FactionValidationError("Properties must be a dictionary")
    
    sanitized = {}
    
    for key, value in properties.items():
        # Sanitize key
        if not isinstance(key, str):
            continue  # Skip non-string keys
        
        clean_key = sanitize_string_input(key, max_length=50)
        if not clean_key:
            continue  # Skip empty keys
        
        # Sanitize value based on type
        if isinstance(value, str):
            sanitized[clean_key] = sanitize_string_input(value, max_length=500)
        elif isinstance(value, (int, float)):
            # Clamp numeric values to reasonable ranges
            if isinstance(value, float):
                sanitized[clean_key] = max(-1000000, min(1000000, value))
            else:
                sanitized[clean_key] = max(-1000000, min(1000000, value))
        elif isinstance(value, bool):
            sanitized[clean_key] = value
        elif isinstance(value, list):
            # Limit list size and sanitize elements
            if len(value) > 100:
                raise FactionValidationError("Lists in properties cannot exceed 100 items")
            sanitized[clean_key] = [sanitize_string_input(str(item), max_length=200) for item in value[:100]]
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[clean_key] = sanitize_properties_dict(value, max_depth, current_depth + 1)
        # Skip other types (None, complex objects, etc.)
    
    return sanitized

def validate_alliance_terms(alliance_terms: Dict[str, Any]) -> Dict[str, Any]:
    """Validate alliance terms data"""
    
    required_fields = ["alliance_type", "duration"]
    for field in required_fields:
        if field not in alliance_terms:
            raise ValueError(f"Alliance terms must include {field}")
    
    # Validate alliance type
    valid_types = ["military", "economic", "temporary_truce", "mutual_defense", 
                   "offensive_pact", "research", "cultural"]
    if alliance_terms["alliance_type"] not in valid_types:
        raise ValueError(f"Alliance type must be one of: {', '.join(valid_types)}")
    
    # Validate duration (in days)
    duration = alliance_terms.get("duration")
    if not isinstance(duration, (int, float)) or duration <= 0:
        raise ValueError("Duration must be a positive number")
    
    return alliance_terms

class DefaultFactionValidationService:
    """Default implementation of FactionValidationService protocol"""
    
    def validate_faction_data(self, faction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate faction creation/update data"""
        return validate_faction_data(faction_data)
    
    def validate_hidden_attributes(self, attributes: Dict[str, int]) -> Dict[str, int]:
        """Validate hidden attributes"""
        return validate_hidden_attributes(attributes)
    
    def generate_hidden_attributes(self) -> Dict[str, int]:
        """Generate random hidden attributes"""
        return generate_faction_hidden_attributes() 