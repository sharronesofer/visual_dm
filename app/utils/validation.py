from typing import Dict, Any, List
from flask import jsonify

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that all required fields are present in the data.
    
    Args:
        data: Dictionary containing the data to validate
        required_fields: List of required field names
        
    Raises:
        ValueError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

def validate_poi_type(poi_type: str) -> None:
    """
    Validate that the POI type is valid.
    
    Args:
        poi_type: The POI type to validate
        
    Raises:
        ValueError: If the POI type is invalid
    """
    from app.game.world.pois.types import POIType
    if not POIType.is_valid(poi_type):
        raise ValueError(f"Invalid POI type: {poi_type}")

def validate_coordinates(x: float, y: float, z: float) -> None:
    """
    Validate that coordinates are valid numbers.
    
    Args:
        x: X coordinate
        y: Y coordinate
        z: Z coordinate
        
    Raises:
        ValueError: If any coordinate is not a valid number
    """
    if not isinstance(x, (int, float)) or not isinstance(y, (int, float)) or not isinstance(z, (int, float)):
        raise ValueError("Coordinates must be numbers") 