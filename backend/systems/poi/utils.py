"""
Utility functions for POI operations.
Provides helper functions and calculations related to POIs.
"""

from typing import Optional, Dict, Any, Tuple
import math

from .models import PointOfInterest, POIState

# Function moved to POIStateService, left here for backward compatibility
def get_poi_state(poi: PointOfInterest) -> Dict[str, Any]:
    """
    Get detailed information about a POI's current state.
    Deprecated - use POIStateService.get_state_info instead.
    """
    from .services import POIStateService
    return POIStateService.get_state_info(poi)

def calculate_poi_distance(poi1, poi2):
    """
    Calculate the distance between two POIs or coordinates.
    
    Args:
        poi1: First POI or coordinate string (format: "x_y")
        poi2: Second POI or coordinate string (format: "x_y")
        
    Returns:
        Distance in arbitrary units (grid cells)
    """
    # Handle string coordinates (format: "x_y")
    if isinstance(poi1, str) and isinstance(poi2, str):
        try:
            x1, y1 = map(int, poi1.split("_"))
            x2, y2 = map(int, poi2.split("_"))
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        except (ValueError, AttributeError):
            # If parsing fails, return a large value
            return 9999.0
    
    # Handle POI objects
    if hasattr(poi1, 'region_id') and hasattr(poi2, 'region_id'):
        # If the POIs are in different regions, use their coordinates
        if poi1.region_id != poi2.region_id:
            # Using global coordinates if available
            if hasattr(poi1, 'coordinates') and hasattr(poi2, 'coordinates'):
                x1, y1 = poi1.coordinates
                x2, y2 = poi2.coordinates
                return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            else:
                # If no global coordinates, return a large value indicating "far away"
                return 9999.0
        
        # Same region, use position
        x1, y1 = poi1.position.get('x', 0), poi1.position.get('y', 0)
        x2, y2 = poi2.position.get('x', 0), poi2.position.get('y', 0)
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
    # Mixed types - try to extract coordinates as best we can
    try:
        if isinstance(poi1, str):
            x1, y1 = map(int, poi1.split("_"))
        else:
            x1, y1 = poi1.position.get('x', 0), poi1.position.get('y', 0)
        
        if isinstance(poi2, str):
            x2, y2 = map(int, poi2.split("_"))
        else:
            x2, y2 = poi2.position.get('x', 0), poi2.position.get('y', 0)
        
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    except (ValueError, AttributeError):
        # If all else fails
        return 9999.0

def is_poi_accessible(poi: PointOfInterest, character_level: int = 1) -> bool:
    """
    Check if a POI is accessible to a character of the given level.
    
    Args:
        poi: The POI to check
        character_level: The character level to check against
        
    Returns:
        True if accessible, False otherwise
    """
    # Check level requirements if applicable
    if poi.level > character_level:
        return False
    
    # Check state-based accessibility
    if poi.current_state in [POIState.ABANDONED, POIState.RUINS, POIState.DUNGEON]:
        # These require special handling/challenges to enter
        # Higher level characters might be able to enter dangerous areas
        return character_level >= max(3, poi.level + 2)
    
    # Normal or declining POIs are accessible
    return True

def generate_poi_name(poi_type: str, region_name: Optional[str] = None, tags: Optional[list] = None) -> str:
    """
    Generate a name for a POI based on its type, region, and tags.
    
    Args:
        poi_type: The type of POI
        region_name: Optional name of the region
        tags: Optional list of tags for flavor
        
    Returns:
        Generated name for the POI
    """
    # This is a placeholder implementation
    # In a real implementation, this would use more sophisticated name generation
    # possibly with word lists and combinations based on region themes
    
    prefixes = {
        "city": ["Great", "Royal", "Imperial", "Ancient", "New"],
        "town": ["Upper", "Lower", "East", "West", "Old", "Fair"],
        "village": ["Little", "Sunny", "Green", "Red", "Blue"],
        "dungeon": ["Dark", "Forgotten", "Cursed", "Black", "Lost"],
        "ruins": ["Fallen", "Broken", "Shattered", "Elder", "Crumbling"],
        "temple": ["Sacred", "Holy", "Divine", "Blessed", "Hallowed"],
        "fortress": ["Mighty", "Stone", "Iron", "Guard", "Watch"],
    }
    
    suffixes = {
        "city": ["City", "Metropolis", "Capital", "Haven", "Port"],
        "town": ["Town", "Crossing", "Market", "Landing", "Ford"],
        "village": ["Village", "Hamlet", "Glen", "Hollow", "Vale"],
        "dungeon": ["Dungeon", "Crypt", "Pit", "Lair", "Hold"],
        "ruins": ["Ruins", "Remains", "Wreckage", "Desolation", "Rubble"],
        "temple": ["Temple", "Shrine", "Sanctuary", "Abbey", "Cathedral"],
        "fortress": ["Fortress", "Keep", "Citadel", "Stronghold", "Bastion"],
    }
    
    # Use the provided poi_type or a general default
    poi_key = poi_type.lower() if poi_type.lower() in prefixes else "other"
    
    # Get random elements from the lists (in a real implementation, this would use random)
    # For this example, just use the first element
    prefix = prefixes.get(poi_key, ["Mysterious"])[0]
    base_name = region_name.split()[0] if region_name else "Unknown"
    suffix = suffixes.get(poi_key, ["Place"])[0]
    
    return f"{prefix} {base_name} {suffix}"

def normalize_poi_type(poi_type: str) -> str:
    """
    Normalize a POI type string to match canonical POI types.
    
    Args:
        poi_type: The POI type string to normalize
        
    Returns:
        Normalized POI type string
    """
    # Convert to lowercase
    normalized = poi_type.lower()
    
    # Map variations to canonical types
    type_mapping = {
        # City variations
        "metropolis": "city",
        "capitol": "city",
        "capital": "city",
        "urban": "city",
        
        # Town variations
        "settlement": "town",
        "borough": "town",
        
        # Village variations
        "hamlet": "village",
        "homestead": "village",
        
        # Dungeon variations
        "crypt": "dungeon",
        "tomb": "dungeon",
        "cavern": "dungeon",
        
        # Ruins variations
        "wreckage": "ruins",
        "abandoned": "ruins",
        "rubble": "ruins",
        
        # Temple variations
        "shrine": "temple",
        "sanctuary": "temple",
        "cathedral": "temple",
        
        # Fortress variations
        "castle": "fortress",
        "citadel": "fortress",
        "stronghold": "fortress",
    }
    
    # Return mapped type if it exists, otherwise return the normalized type
    return type_mapping.get(normalized, normalized) 