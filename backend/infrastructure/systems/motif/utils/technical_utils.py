"""
Technical utilities for motif system.
Contains geometric calculations, data validation, and other technical functions.
"""

from typing import List, Dict, Any, Optional, Tuple
import math
from dataclasses import dataclass

from backend.infrastructure.systems.motif.models import (
    Motif, MotifCategory, MotifScope, MotifEffectTarget
)

# ===== Geometric Calculation Utilities =====

@dataclass
class Point:
    """Represents a 2D point with x, y coordinates."""
    x: float
    y: float

def calculate_distance(point1: Point, point2: Point) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((point2.x - point1.x)**2 + (point2.y - point1.y)**2)

def point_in_circle(point: Point, center: Point, radius: float) -> bool:
    """Check if a point is within a circular area."""
    return calculate_distance(point, center) <= radius

def calculate_influence_area(motif: Motif) -> float:
    """Calculate the total area of influence for a motif."""
    if not motif.location:
        return float('inf') if motif.scope == MotifScope.GLOBAL else 0.0
    
    # Base radius from location, modified by intensity and scope
    base_radius = motif.location.radius or 1.0
    
    # Scope multipliers
    scope_multipliers = {
        MotifScope.LOCAL: 1.0,
        MotifScope.REGIONAL: 5.0,
        MotifScope.GLOBAL: float('inf')
    }
    
    if motif.scope == MotifScope.GLOBAL:
        return float('inf')
    
    effective_radius = base_radius * scope_multipliers[motif.scope] * (motif.intensity / 5.0)
    return math.pi * (effective_radius ** 2)

def find_motifs_in_radius(motifs: List[Motif], center: Point, radius: float) -> List[Motif]:
    """Find all motifs within a given radius of a point."""
    result = []
    for motif in motifs:
        if not motif.location:
            continue
        motif_center = Point(motif.location.x or 0, motif.location.y or 0)
        if calculate_distance(center, motif_center) <= radius:
            result.append(motif)
    return result

def calculate_motif_overlap(motif1: Motif, motif2: Motif) -> float:
    """Calculate the overlap percentage between two motifs' areas of influence."""
    if not motif1.location or not motif2.location:
        return 1.0 if motif1.scope == MotifScope.GLOBAL or motif2.scope == MotifScope.GLOBAL else 0.0
    
    center1 = Point(motif1.location.x or 0, motif1.location.y or 0)
    center2 = Point(motif2.location.x or 0, motif2.location.y or 0)
    
    radius1 = (motif1.location.radius or 1.0) * (motif1.intensity / 5.0)
    radius2 = (motif2.location.radius or 1.0) * (motif2.intensity / 5.0)
    
    distance = calculate_distance(center1, center2)
    
    # No overlap if too far apart
    if distance >= radius1 + radius2:
        return 0.0
    
    # Complete overlap if one circle is inside the other
    if distance <= abs(radius1 - radius2):
        smaller_area = math.pi * min(radius1, radius2) ** 2
        larger_area = math.pi * max(radius1, radius2) ** 2
        return smaller_area / larger_area
    
    # Partial overlap calculation using circle intersection formula
    # This is a simplified approximation
    overlap_distance = radius1 + radius2 - distance
    max_overlap = min(radius1, radius2) * 2
    overlap_ratio = overlap_distance / max_overlap
    
    return min(1.0, max(0.0, overlap_ratio))

# ===== Data Validation Utilities =====

def validate_motif_data(motif_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate motif data for completeness and correctness.
    Returns (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'description', 'category', 'scope']
    for field in required_fields:
        if field not in motif_data or not motif_data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate intensity range
    if 'intensity' in motif_data:
        intensity = motif_data['intensity']
        if not isinstance(intensity, (int, float)) or intensity < 1 or intensity > 10:
            errors.append("Intensity must be a number between 1 and 10")
    
    # Validate category
    if 'category' in motif_data:
        try:
            MotifCategory(motif_data['category'])
        except ValueError:
            errors.append(f"Invalid category: {motif_data['category']}")
    
    # Validate scope
    if 'scope' in motif_data:
        try:
            MotifScope(motif_data['scope'])
        except ValueError:
            errors.append(f"Invalid scope: {motif_data['scope']}")
    
    # Validate location data if present
    if 'location' in motif_data and motif_data['location']:
        location = motif_data['location']
        if isinstance(location, dict):
            if 'x' in location and not isinstance(location['x'], (int, float, type(None))):
                errors.append("Location x coordinate must be a number or null")
            if 'y' in location and not isinstance(location['y'], (int, float, type(None))):
                errors.append("Location y coordinate must be a number or null")
            if 'radius' in location and (not isinstance(location['radius'], (int, float)) or location['radius'] < 0):
                errors.append("Location radius must be a non-negative number")
    
    # Validate effects if present
    if 'effects' in motif_data and isinstance(motif_data['effects'], list):
        for i, effect in enumerate(motif_data['effects']):
            if not isinstance(effect, dict):
                errors.append(f"Effect {i} must be an object")
                continue
            
            if 'target' not in effect:
                errors.append(f"Effect {i} missing required field: target")
            else:
                try:
                    MotifEffectTarget(effect['target'])
                except ValueError:
                    errors.append(f"Effect {i} has invalid target: {effect['target']}")
            
            if 'intensity' in effect:
                eff_intensity = effect['intensity']
                if not isinstance(eff_intensity, (int, float)) or eff_intensity < 1 or eff_intensity > 10:
                    errors.append(f"Effect {i} intensity must be between 1 and 10")
    
    return len(errors) == 0, errors

def sanitize_motif_name(name: str) -> str:
    """Sanitize and normalize a motif name."""
    if not name:
        return "Unnamed Motif"
    
    # Remove excessive whitespace and normalize
    name = ' '.join(name.strip().split())
    
    # Capitalize first letter of each word
    name = ' '.join(word.capitalize() for word in name.split())
    
    # Limit length
    if len(name) > 100:
        name = name[:97] + "..."
    
    return name

def normalize_motif_description(description: str) -> str:
    """Normalize and clean up a motif description."""
    if not description:
        return "No description provided."
    
    # Remove excessive whitespace
    description = ' '.join(description.strip().split())
    
    # Ensure it ends with proper punctuation
    if not description.endswith(('.', '!', '?')):
        description += '.'
    
    # Capitalize first letter
    if description:
        description = description[0].upper() + description[1:]
    
    # Limit length
    if len(description) > 500:
        description = description[:497] + "..."
    
    return description 