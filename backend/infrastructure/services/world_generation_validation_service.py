"""
World Generation Validation Service - Infrastructure Implementation

Provides validation for world generation data structures and business rules.
"""

from typing import Dict, Any, List, Optional, Set
from uuid import UUID

from backend.systems.region.models import RegionMetadata, BiomeType, ClimateType, HexCoordinate
from backend.systems.world_generation.models import WorldGenerationConfig


class DefaultWorldGenerationValidationService:
    """Default implementation of WorldGenerationValidationService protocol"""
    
    def validate_region_data(self, region: RegionMetadata) -> Dict[str, Any]:
        """Validate region data structure and content"""
        issues = []
        warnings = []
        
        # Check required fields
        if not region.id:
            issues.append("Region must have a valid ID")
        
        if not region.name or len(region.name.strip()) == 0:
            issues.append("Region must have a non-empty name")
        
        if not region.hex_coordinates:
            issues.append("Region must have at least one hex coordinate")
        
        # Validate hex coordinates
        for coord in region.hex_coordinates:
            if not self._is_valid_hex_coordinate(coord):
                issues.append(f"Invalid hex coordinate: {coord}")
        
        # Check biome and climate compatibility
        if region.profile:
            if not self._is_biome_climate_compatible(region.profile.dominant_biome, region.profile.climate):
                warnings.append(f"Biome {region.profile.dominant_biome.value} may not be compatible with climate {region.profile.climate.value}")
        
        # Validate population ranges
        if region.estimated_population < 0:
            issues.append("Population cannot be negative")
        elif region.estimated_population > 1000000:
            warnings.append("Very large population for a single region")
        
        # Validate area
        if region.area_square_km <= 0:
            issues.append("Region area must be positive")
        elif region.area_square_km > 100000:
            warnings.append("Very large area for a single region")
        
        # Validate resource nodes
        if region.resource_nodes:
            for resource in region.resource_nodes:
                if resource.quantity < 0:
                    issues.append(f"Resource quantity cannot be negative: {resource.resource_type.value}")
                if resource.quality < 0.0 or resource.quality > 1.0:
                    issues.append(f"Resource quality must be between 0.0 and 1.0: {resource.resource_type.value}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def validate_continent_structure(self, regions: List[RegionMetadata]) -> Dict[str, Any]:
        """Validate continent structure and region relationships"""
        issues = []
        warnings = []
        
        if not regions:
            issues.append("Continent must contain at least one region")
            return {'valid': False, 'issues': issues, 'warnings': warnings}
        
        # Check for duplicate IDs
        region_ids = [region.id for region in regions]
        if len(region_ids) != len(set(region_ids)):
            issues.append("Duplicate region IDs found in continent")
        
        # Check for duplicate names
        region_names = [region.name for region in regions]
        if len(region_names) != len(set(region_names)):
            warnings.append("Duplicate region names found in continent")
        
        # Validate hex coordinate coverage (no overlaps)
        all_coords = []
        for region in regions:
            all_coords.extend(region.hex_coordinates)
        
        if len(all_coords) != len(set(all_coords)):
            issues.append("Overlapping hex coordinates found between regions")
        
        # Check biome distribution
        biome_counts = {}
        for region in regions:
            if region.profile and region.profile.dominant_biome:
                biome = region.profile.dominant_biome.value
                biome_counts[biome] = biome_counts.get(biome, 0) + 1
        
        total_regions = len(regions)
        for biome, count in biome_counts.items():
            proportion = count / total_regions
            if proportion > 0.5:
                warnings.append(f"Biome {biome} dominates continent ({proportion:.1%} of regions)")
        
        # Check for isolated regions (regions with no adjacent regions)
        adjacency_map = self._build_adjacency_map(regions)
        isolated_regions = [region.id for region in regions if len(adjacency_map.get(region.id, [])) == 0]
        
        if isolated_regions and len(regions) > 1:
            warnings.append(f"Found {len(isolated_regions)} isolated regions with no adjacent regions")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'stats': {
                'total_regions': total_regions,
                'biome_distribution': biome_counts,
                'isolated_regions': len(isolated_regions)
            }
        }
    
    def validate_world_generation_config(self, config: WorldGenerationConfig) -> Dict[str, Any]:
        """Validate world generation configuration"""
        issues = []
        warnings = []
        
        # Validate continent size
        if hasattr(config, 'main_continent_size'):
            width, height = config.main_continent_size
            if width < 10 or height < 10:
                issues.append("Continent size too small (minimum 10x10 regions)")
            elif width > 300 or height > 300:
                warnings.append("Very large continent size may impact performance")
        
        # Validate island parameters
        if hasattr(config, 'island_count') and config.island_count < 0:
            issues.append("Island count cannot be negative")
        
        if hasattr(config, 'island_size_range'):
            min_size, max_size = config.island_size_range
            if min_size < 1:
                issues.append("Minimum island size must be at least 1")
            if max_size < min_size:
                issues.append("Maximum island size cannot be less than minimum")
        
        # Validate density values (should be 0.0 to 1.0)
        density_fields = ['biome_diversity', 'resource_abundance', 'poi_density',
                         'settlement_density', 'npc_density', 'faction_density', 
                         'trade_route_density']
        
        for field in density_fields:
            if hasattr(config, field):
                value = getattr(config, field)
                if value < 0.0 or value > 1.0:
                    issues.append(f"{field} must be between 0.0 and 1.0")
        
        # Validate count fields
        if hasattr(config, 'starting_factions') and config.starting_factions < 0:
            issues.append("Starting factions count cannot be negative")
        
        if hasattr(config, 'region_size') and config.region_size < 1:
            issues.append("Region size must be at least 1")
        
        # Check for reasonable combinations
        if (hasattr(config, 'npc_density') and hasattr(config, 'settlement_density') and 
            config.npc_density > 0.8 and config.settlement_density < 0.2):
            warnings.append("High NPC density with low settlement density may create unrealistic population distribution")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def validate_biome_adjacency(self, biome_map: Dict[HexCoordinate, BiomeType]) -> Dict[str, Any]:
        """Validate biome adjacency rules"""
        issues = []
        warnings = []
        
        # Define incompatible biome pairs
        incompatible_pairs = [
            (BiomeType.DESERT, BiomeType.ARCTIC),
            (BiomeType.TROPICAL_RAINFOREST, BiomeType.TUNDRA),
            (BiomeType.SWAMP, BiomeType.DESERT),
        ]
        
        for coord, biome in biome_map.items():
            neighbors = self._get_hex_neighbors(coord, list(biome_map.keys()))
            
            for neighbor_coord in neighbors:
                if neighbor_coord in biome_map:
                    neighbor_biome = biome_map[neighbor_coord]
                    
                    # Check for incompatible adjacencies
                    for pair in incompatible_pairs:
                        if (biome, neighbor_biome) in [pair, pair[::-1]]:
                            issues.append(f"Incompatible biomes adjacent: {biome.value} next to {neighbor_biome.value} at {coord}")
        
        # Check for biome clustering (natural formations)
        isolated_biomes = self._find_isolated_biomes(biome_map)
        if isolated_biomes:
            warnings.append(f"Found {len(isolated_biomes)} isolated biome hexes that may look unnatural")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'stats': {
                'total_hexes': len(biome_map),
                'isolated_biomes': len(isolated_biomes)
            }
        }
    
    def _is_valid_hex_coordinate(self, coord: HexCoordinate) -> bool:
        """Check if hex coordinate is valid (q + r + s = 0)"""
        return coord.q + coord.r + coord.s == 0
    
    def _is_biome_climate_compatible(self, biome: BiomeType, climate: ClimateType) -> bool:
        """Check if biome and climate types are compatible"""
        # Define compatible combinations
        compatible_combinations = {
            BiomeType.TROPICAL_RAINFOREST: [ClimateType.TROPICAL],
            BiomeType.DESERT: [ClimateType.ARID, ClimateType.SEMI_ARID],
            BiomeType.ARCTIC: [ClimateType.POLAR],
            BiomeType.TUNDRA: [ClimateType.POLAR, ClimateType.SUBARCTIC],
            BiomeType.TEMPERATE_FOREST: [ClimateType.TEMPERATE, ClimateType.OCEANIC],
            BiomeType.GRASSLAND: [ClimateType.TEMPERATE, ClimateType.CONTINENTAL],
            BiomeType.MOUNTAINS: [ClimateType.TEMPERATE, ClimateType.CONTINENTAL, ClimateType.POLAR],
            BiomeType.COASTAL: [ClimateType.OCEANIC, ClimateType.MEDITERRANEAN],
            BiomeType.SWAMP: [ClimateType.SUBTROPICAL, ClimateType.TROPICAL]
        }
        
        compatible_climates = compatible_combinations.get(biome, [])
        return climate in compatible_climates
    
    def _build_adjacency_map(self, regions: List[RegionMetadata]) -> Dict[UUID, List[UUID]]:
        """Build adjacency map between regions based on hex coordinates"""
        adjacency_map = {}
        
        # Create coordinate to region mapping
        coord_to_region = {}
        for region in regions:
            for coord in region.hex_coordinates:
                coord_to_region[coord] = region.id
        
        # Build adjacency relationships
        for region in regions:
            adjacency_map[region.id] = []
            
            for coord in region.hex_coordinates:
                neighbors = self._get_hex_neighbors(coord, list(coord_to_region.keys()))
                
                for neighbor_coord in neighbors:
                    neighbor_region_id = coord_to_region[neighbor_coord]
                    if neighbor_region_id != region.id and neighbor_region_id not in adjacency_map[region.id]:
                        adjacency_map[region.id].append(neighbor_region_id)
        
        return adjacency_map
    
    def _get_hex_neighbors(self, coord: HexCoordinate, all_coords: List[HexCoordinate]) -> List[HexCoordinate]:
        """Get neighboring hex coordinates"""
        possible_neighbors = [
            HexCoordinate(coord.q + 1, coord.r - 1, coord.s),
            HexCoordinate(coord.q + 1, coord.r, coord.s - 1),
            HexCoordinate(coord.q, coord.r + 1, coord.s - 1),
            HexCoordinate(coord.q - 1, coord.r + 1, coord.s),
            HexCoordinate(coord.q - 1, coord.r, coord.s + 1),
            HexCoordinate(coord.q, coord.r - 1, coord.s + 1),
        ]
        
        return [n for n in possible_neighbors if n in all_coords]
    
    def _find_isolated_biomes(self, biome_map: Dict[HexCoordinate, BiomeType]) -> List[HexCoordinate]:
        """Find biome hexes that are isolated (surrounded by different biomes)"""
        isolated = []
        
        for coord, biome in biome_map.items():
            neighbors = self._get_hex_neighbors(coord, list(biome_map.keys()))
            neighbor_biomes = [biome_map[n] for n in neighbors if n in biome_map]
            
            # If all neighbors are different biomes, this hex is isolated
            if neighbor_biomes and all(nb != biome for nb in neighbor_biomes):
                isolated.append(coord)
        
        return isolated 