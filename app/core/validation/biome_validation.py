"""
Biome and Terrain Validation for World Generation.

This module provides specific validation routines for checking biome adjacency,
terrain consistency, and geographically realistic world generation.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict, deque

from app.core.models.world import World
from app.world.world_models import TerrainType, Region
from .world_validation import ValidationResult

logger = logging.getLogger(__name__)

# Biome adjacency rules - define which biomes can be neighbors
# Format: biome -> set of valid adjacent biomes
BIOME_ADJACENCY_RULES = {
    "plains": {"forest", "desert", "mountains", "swamp", "tundra", "coast"},
    "forest": {"plains", "mountains", "swamp", "tundra", "coast"},
    "mountains": {"plains", "forest", "desert", "tundra", "coast"},
    "desert": {"plains", "mountains", "coast"},
    "swamp": {"plains", "forest", "coast", "river", "lake"},
    "tundra": {"plains", "forest", "mountains", "coast"},
    "coast": {"plains", "forest", "mountains", "desert", "swamp", "tundra", "ocean"},
    "ocean": {"coast", "river"},
    "river": {"plains", "forest", "mountains", "swamp", "ocean", "lake"},
    "lake": {"plains", "forest", "mountains", "swamp", "river"}
}

# Additional constraints for thermal zones (latitude-based)
# Limits which biomes can appear at different latitudes
THERMAL_ZONE_CONSTRAINTS = {
    "polar": {"tundra", "mountains", "ocean"},
    "temperate": {"plains", "forest", "mountains", "swamp", "coast", "ocean", "river", "lake"},
    "tropical": {"forest", "plains", "swamp", "desert", "coast", "ocean", "river", "lake"}
}

# Elevation constraints - which biomes are allowed at different elevations
ELEVATION_CONSTRAINTS = {
    "low": {"plains", "desert", "swamp", "coast", "ocean", "river", "lake"},
    "medium": {"plains", "forest", "desert", "river", "lake"},
    "high": {"mountains", "tundra", "forest"}
}

def validate_biome_adjacency(world: World) -> ValidationResult:
    """
    Validate that biome placements follow realistic adjacency rules.
    
    Args:
        world: The world to validate
        
    Returns:
        ValidationResult indicating whether biome adjacency is valid
    """
    if not hasattr(world.state, 'regions') or not world.state.regions:
        return ValidationResult(
            is_valid=False,
            message="World has no regions to validate",
            details={"error": "No regions found in world state"}
        )
    
    # Build a map of regions and their neighbors
    region_neighbors = _build_region_adjacency_map(world)
    
    # Check biome adjacency rules
    violations = []
    
    for region_id, neighbors in region_neighbors.items():
        region = _find_region_by_id(world, region_id)
        if not region:
            continue
        
        # Get the region's biome(s)
        region_biomes = _get_region_biomes(region)
        if not region_biomes:
            continue
        
        # Check each neighbor
        for neighbor_id in neighbors:
            neighbor = _find_region_by_id(world, neighbor_id)
            if not neighbor:
                continue
            
            neighbor_biomes = _get_region_biomes(neighbor)
            if not neighbor_biomes:
                continue
            
            # Check if any biome in the region can be adjacent to any biome in the neighbor
            valid_adjacency = _check_biomes_adjacency(region_biomes, neighbor_biomes)
            
            if not valid_adjacency:
                violations.append({
                    "region_id": region_id,
                    "region_biomes": list(region_biomes),
                    "neighbor_id": neighbor_id,
                    "neighbor_biomes": list(neighbor_biomes)
                })
    
    # Return the validation result
    if violations:
        return ValidationResult(
            is_valid=False,
            message=f"Found {len(violations)} biome adjacency violations",
            details={"violations": violations}
        )
    
    return ValidationResult(
        is_valid=True,
        message="Biome adjacency rules are satisfied",
        details={"regions_checked": len(region_neighbors)}
    )

def validate_thermal_consistency(world: World) -> ValidationResult:
    """
    Validate that biomes are distributed according to thermal zones.
    
    Args:
        world: The world to validate
        
    Returns:
        ValidationResult indicating whether thermal consistency is valid
    """
    if not hasattr(world.state, 'regions') or not world.state.regions:
        return ValidationResult(
            is_valid=False,
            message="World has no regions to validate",
            details={"error": "No regions found in world state"}
        )
    
    # Get the regions
    regions = world.state.regions
    
    # Check thermal zone consistency
    violations = []
    
    for region in regions:
        # Determine thermal zone based on latitude (simplified)
        latitude = _get_region_latitude(region)
        thermal_zone = "temperate"  # Default
        
        if latitude > 0.66:
            thermal_zone = "polar"
        elif latitude < 0.33:
            thermal_zone = "tropical"
        
        # Get the region's biome(s)
        region_biomes = _get_region_biomes(region)
        if not region_biomes:
            continue
        
        # Check if all biomes in the region are allowed in this thermal zone
        allowed_biomes = THERMAL_ZONE_CONSTRAINTS.get(thermal_zone, set())
        invalid_biomes = region_biomes - allowed_biomes
        
        if invalid_biomes:
            violations.append({
                "region_id": region.id,
                "thermal_zone": thermal_zone,
                "latitude": latitude,
                "invalid_biomes": list(invalid_biomes),
                "allowed_biomes": list(allowed_biomes)
            })
    
    # Return the validation result
    if violations:
        return ValidationResult(
            is_valid=False,
            message=f"Found {len(violations)} thermal zone violations",
            details={"violations": violations}
        )
    
    return ValidationResult(
        is_valid=True,
        message="Thermal zone constraints are satisfied",
        details={"regions_checked": len(regions)}
    )

def validate_elevation_consistency(world: World) -> ValidationResult:
    """
    Validate that biomes are appropriate for their elevation.
    
    Args:
        world: The world to validate
        
    Returns:
        ValidationResult indicating whether elevation consistency is valid
    """
    if not hasattr(world.state, 'regions') or not world.state.regions:
        return ValidationResult(
            is_valid=False,
            message="World has no regions to validate",
            details={"error": "No regions found in world state"}
        )
    
    # Get the regions
    regions = world.state.regions
    
    # Check elevation consistency
    violations = []
    
    for region in regions:
        # Determine elevation level (simplified)
        elevation = _get_region_elevation(region)
        elevation_level = "medium"  # Default
        
        if elevation > 0.66:
            elevation_level = "high"
        elif elevation < 0.33:
            elevation_level = "low"
        
        # Get the region's biome(s)
        region_biomes = _get_region_biomes(region)
        if not region_biomes:
            continue
        
        # Check if all biomes in the region are allowed at this elevation
        allowed_biomes = ELEVATION_CONSTRAINTS.get(elevation_level, set())
        invalid_biomes = region_biomes - allowed_biomes
        
        if invalid_biomes:
            violations.append({
                "region_id": region.id,
                "elevation_level": elevation_level,
                "elevation": elevation,
                "invalid_biomes": list(invalid_biomes),
                "allowed_biomes": list(allowed_biomes)
            })
    
    # Return the validation result
    if violations:
        return ValidationResult(
            is_valid=False,
            message=f"Found {len(violations)} elevation consistency violations",
            details={"violations": violations}
        )
    
    return ValidationResult(
        is_valid=True,
        message="Elevation consistency constraints are satisfied",
        details={"regions_checked": len(regions)}
    )

def validate_biome_distribution(world: World) -> ValidationResult:
    """
    Validate that biomes are distributed in a balanced way.
    
    Args:
        world: The world to validate
        
    Returns:
        ValidationResult indicating whether biome distribution is valid
    """
    if not hasattr(world.state, 'regions') or not world.state.regions:
        return ValidationResult(
            is_valid=False,
            message="World has no regions to validate",
            details={"error": "No regions found in world state"}
        )
    
    # Get the regions
    regions = world.state.regions
    
    # Count biome occurrences
    biome_counts = defaultdict(int)
    
    for region in regions:
        region_biomes = _get_region_biomes(region)
        for biome in region_biomes:
            biome_counts[biome] += 1
    
    total_biomes = sum(biome_counts.values())
    
    # Check biome distribution
    # Ensure no single biome takes up more than 40% of the world
    excessive_biomes = []
    for biome, count in biome_counts.items():
        percentage = (count / total_biomes) * 100 if total_biomes > 0 else 0
        if percentage > 40:
            excessive_biomes.append({
                "biome": biome,
                "count": count,
                "percentage": percentage
            })
    
    # Ensure at least 4 different biome types are present
    diverse_enough = len(biome_counts) >= 4
    
    # Return the validation result
    if excessive_biomes or not diverse_enough:
        return ValidationResult(
            is_valid=False,
            message=f"Biome distribution is unbalanced",
            details={
                "excessive_biomes": excessive_biomes,
                "diverse_enough": diverse_enough,
                "biome_counts": dict(biome_counts),
                "total_biomes": total_biomes,
                "unique_biomes": len(biome_counts)
            }
        )
    
    return ValidationResult(
        is_valid=True,
        message="Biome distribution is balanced",
        details={
            "biome_counts": dict(biome_counts),
            "total_biomes": total_biomes,
            "unique_biomes": len(biome_counts)
        }
    )

def validate_river_continuity(world: World) -> ValidationResult:
    """
    Validate that rivers form continuous paths without gaps.
    
    Args:
        world: The world to validate
        
    Returns:
        ValidationResult indicating whether river continuity is valid
    """
    if not hasattr(world.state, 'regions') or not world.state.regions:
        return ValidationResult(
            is_valid=False,
            message="World has no regions to validate",
            details={"error": "No regions found in world state"}
        )
    
    # Build a map of regions and their neighbors
    region_neighbors = _build_region_adjacency_map(world)
    
    # Find river regions
    river_regions = []
    for region in world.state.regions:
        region_biomes = _get_region_biomes(region)
        if "river" in region_biomes:
            river_regions.append(region.id)
    
    # Check river continuity
    discontinuities = []
    
    for river_id in river_regions:
        # Check if the river has at least one neighbor that is either a river, lake, or ocean
        region = _find_region_by_id(world, river_id)
        if not region:
            continue
        
        neighbors = region_neighbors.get(river_id, [])
        valid_continuity = False
        
        for neighbor_id in neighbors:
            neighbor = _find_region_by_id(world, neighbor_id)
            if not neighbor:
                continue
            
            neighbor_biomes = _get_region_biomes(neighbor)
            if any(biome in {"river", "lake", "ocean"} for biome in neighbor_biomes):
                valid_continuity = True
                break
        
        if not valid_continuity:
            discontinuities.append({
                "river_id": river_id,
                "neighbors": neighbors
            })
    
    # Return the validation result
    if discontinuities:
        return ValidationResult(
            is_valid=False,
            message=f"Found {len(discontinuities)} river discontinuities",
            details={"discontinuities": discontinuities}
        )
    
    return ValidationResult(
        is_valid=True,
        message="River continuity is valid",
        details={"river_regions": len(river_regions)}
    )

# Helper functions

def _build_region_adjacency_map(world: World) -> Dict[str, List[str]]:
    """Build a map of regions and their neighboring regions."""
    region_neighbors = defaultdict(list)
    
    # This is a simplified version assuming regions have explicit neighbor relationships
    # In a real implementation, this would use spatial positions to determine adjacency
    
    # Check if the world has a "connections" attribute containing adjacency information
    if hasattr(world.state, 'connections') and world.state.connections:
        for connection in world.state.connections:
            region1 = connection.get("region1")
            region2 = connection.get("region2")
            
            if region1 and region2:
                region_neighbors[region1].append(region2)
                region_neighbors[region2].append(region1)
    else:
        # Fallback to a placeholder implementation
        # In a real implementation, we would use spatial positions to determine adjacency
        logger.warning("World does not have explicit region connections, adjacency validation may be incomplete")
    
    return region_neighbors

def _find_region_by_id(world: World, region_id: str) -> Optional[Any]:
    """Find a region by its ID."""
    if not hasattr(world.state, 'regions'):
        return None
    
    for region in world.state.regions:
        if region.id == region_id:
            return region
    
    return None

def _get_region_biomes(region: Any) -> Set[str]:
    """Get the biomes in a region."""
    biomes = set()
    
    # Handle different region structures
    if hasattr(region, 'biome'):
        biomes.add(region.biome)
    elif hasattr(region, 'biomes'):
        biomes.update(region.biomes)
    elif hasattr(region, 'terrain_types'):
        biomes.update(region.terrain_types)
    
    return biomes

def _check_biomes_adjacency(biomes1: Set[str], biomes2: Set[str]) -> bool:
    """Check if two sets of biomes can be adjacent."""
    # Check if any biome in biomes1 can be adjacent to any biome in biomes2
    for biome1 in biomes1:
        allowed_adjacent = BIOME_ADJACENCY_RULES.get(biome1, set())
        if any(biome2 in allowed_adjacent for biome2 in biomes2):
            return True
    
    return False

def _get_region_latitude(region: Any) -> float:
    """Get the latitude of a region (normalized to 0-1)."""
    # This is a simplified version that extracts latitude from region data
    # In a real implementation, this would use the actual spatial coordinates
    
    if hasattr(region, 'latitude'):
        return region.latitude
    
    if hasattr(region, 'coordinates') and hasattr(region.coordinates, 'y'):
        # Assume y coordinate is latitude
        # Normalize to 0-1 range
        world_height = 100  # Default world height
        return region.coordinates.y / world_height
    
    # Default to middle latitude
    return 0.5

def _get_region_elevation(region: Any) -> float:
    """Get the elevation of a region (normalized to 0-1)."""
    # This is a simplified version that extracts elevation from region data
    # In a real implementation, this would use the actual elevation data
    
    if hasattr(region, 'elevation'):
        return region.elevation
    
    if hasattr(region, 'height'):
        return region.height
    
    # Try to infer from biomes
    biomes = _get_region_biomes(region)
    
    if "mountains" in biomes:
        return 0.8
    elif "forest" in biomes:
        return 0.5
    elif "plains" in biomes:
        return 0.3
    elif "ocean" in biomes:
        return 0.1
    
    # Default to middle elevation
    return 0.5 