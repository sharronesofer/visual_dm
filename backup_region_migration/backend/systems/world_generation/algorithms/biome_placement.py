"""
Biome Placement Engine

Handles intelligent biome placement based on environmental factors,
adjacency rules, and configuration-driven constraints.
"""

import random
from typing import Dict, List, Set, Tuple
from backend.systems.region.models import BiomeType, HexCoordinate
from backend.systems.world_generation.config.biome_config import BiomeConfigManager


class BiomePlacementEngine:
    """Engine for placing biomes according to environmental and adjacency rules."""
    
    def __init__(self, biome_config: BiomeConfigManager):
        self.biome_config = biome_config
        self.biome_adjacency_cache = {}
    
    def generate_biome_map(self,
                          hex_grid: List[HexCoordinate],
                          height_map: Dict[HexCoordinate, float],
                          climate_map: Dict[HexCoordinate, Tuple[float, float]],
                          config) -> Dict[HexCoordinate, BiomeType]:
        """Generate biome assignments for all hexes in the grid."""
        
        biome_map = {}
        
        # First pass: assign biomes based on environmental factors
        for coord in hex_grid:
            elevation = height_map.get(coord, 0.5)
            temperature, humidity = climate_map.get(coord, (0.5, 0.5))
            
            biome = self._select_biome_by_environment(elevation, temperature, humidity)
            biome_map[coord] = biome
        
        # Second pass: apply biome clustering for more natural formations
        if hasattr(config, 'biome_diversity') and config.biome_diversity > 0:
            biome_map = self._apply_biome_clustering(biome_map, hex_grid, config.biome_diversity)
        
        # Third pass: validate and fix adjacency rules
        biome_map = self._validate_biome_adjacency(biome_map, hex_grid)
        
        return biome_map
    
    def _select_biome_by_environment(self, 
                                   elevation: float, 
                                   temperature: float, 
                                   humidity: float) -> BiomeType:
        """Select the most appropriate biome based on environmental factors."""
        
        best_biome = BiomeType.TEMPERATE_FOREST  # Default
        best_score = 0.0
        
        # Check all available biomes
        for biome_type in BiomeType:
            score = self._calculate_biome_suitability(biome_type, elevation, temperature, humidity)
            
            # Apply rarity factor
            rarity = self.biome_config.get_biome_rarity(biome_type)
            adjusted_score = score * rarity
            
            if adjusted_score > best_score:
                best_score = adjusted_score
                best_biome = biome_type
        
        return best_biome
    
    def _calculate_biome_suitability(self,
                                   biome_type: BiomeType,
                                   elevation: float,
                                   temperature: float,
                                   humidity: float) -> float:
        """Calculate how suitable environmental conditions are for a biome."""
        
        # Get biome requirements
        temp_range = self.biome_config.get_biome_temperature_range(biome_type)
        humidity_range = self.biome_config.get_biome_humidity_range(biome_type)
        
        # Calculate fit scores for each environmental factor
        temp_score = self._calculate_range_score(temperature, temp_range)
        humidity_score = self._calculate_range_score(humidity, humidity_range)
        
        # Elevation scoring (simplified - could be made configurable)
        elevation_score = 1.0  # Default: elevation doesn't matter much
        
        # Special elevation requirements for certain biomes
        if biome_type == BiomeType.MOUNTAINS and elevation > 0.6:
            elevation_score = 1.5  # Boost mountains at high elevation
        elif biome_type == BiomeType.COASTAL and elevation < 0.3:
            elevation_score = 1.2  # Boost coastal at low elevation
        elif biome_type == BiomeType.SWAMP and elevation < 0.2:
            elevation_score = 1.3  # Boost swamps at very low elevation
        
        # Combine scores (weighted average)
        overall_score = (temp_score * 0.4 + humidity_score * 0.4 + elevation_score * 0.2)
        
        return overall_score
    
    def _calculate_range_score(self, value: float, range_tuple: Tuple[float, float]) -> float:
        """Calculate how well a value fits within a range (0.0 to 1.0+)."""
        min_val, max_val = range_tuple
        
        if min_val <= value <= max_val:
            # Perfect fit - score based on distance from center
            center = (min_val + max_val) / 2
            distance_from_center = abs(value - center) / ((max_val - min_val) / 2)
            return 1.0 - distance_from_center * 0.2  # Small penalty for being off-center
        else:
            # Outside range - score based on distance from nearest edge
            if value < min_val:
                distance = min_val - value
            else:
                distance = value - max_val
            
            # Exponential decay outside the range
            return max(0.0, 0.8 ** (distance * 10))
    
    def _apply_biome_clustering(self,
                               biome_map: Dict[HexCoordinate, BiomeType],
                               hex_grid: List[HexCoordinate],
                               clustering_factor: float) -> Dict[HexCoordinate, BiomeType]:
        """Apply clustering to make biomes form more natural groupings."""
        
        clustered_map = biome_map.copy()
        
        # Multiple passes for better clustering
        for _ in range(3):
            for coord in hex_grid:
                neighbors = self._get_hex_neighbors(coord, hex_grid)
                neighbor_biomes = [biome_map.get(n) for n in neighbors if n in biome_map]
                
                if not neighbor_biomes:
                    continue
                
                # Count neighboring biomes
                biome_counts = {}
                for biome in neighbor_biomes:
                    if biome:
                        biome_counts[biome] = biome_counts.get(biome, 0) + 1
                
                # Find most common neighboring biome
                if biome_counts:
                    most_common_biome = max(biome_counts, key=biome_counts.get)
                    most_common_count = biome_counts[most_common_biome]
                    
                    # Apply clustering based on neighbor influence
                    influence_strength = (most_common_count / len(neighbor_biomes)) * clustering_factor
                    
                    if random.random() < influence_strength:
                        # Check if transition is valid
                        current_biome = clustered_map[coord]
                        if self._is_valid_biome_transition(current_biome, most_common_biome):
                            clustered_map[coord] = most_common_biome
        
        return clustered_map
    
    def _validate_biome_adjacency(self,
                                 biome_map: Dict[HexCoordinate, BiomeType],
                                 hex_grid: List[HexCoordinate]) -> Dict[HexCoordinate, BiomeType]:
        """Validate and fix biome adjacency rules."""
        
        validated_map = biome_map.copy()
        changes_made = True
        iterations = 0
        max_iterations = 5
        
        while changes_made and iterations < max_iterations:
            changes_made = False
            iterations += 1
            
            for coord in hex_grid:
                current_biome = validated_map[coord]
                neighbors = self._get_hex_neighbors(coord, hex_grid)
                
                for neighbor_coord in neighbors:
                    if neighbor_coord in validated_map:
                        neighbor_biome = validated_map[neighbor_coord]
                        
                        if not self._is_valid_biome_transition(current_biome, neighbor_biome):
                            # Find a suitable replacement biome
                            replacement = self._find_suitable_replacement_biome(
                                current_biome, neighbor_biome, coord, validated_map, hex_grid
                            )
                            
                            if replacement and replacement != current_biome:
                                validated_map[coord] = replacement
                                changes_made = True
                                break  # Move to next coordinate
        
        return validated_map
    
    def _is_valid_biome_transition(self, biome1: BiomeType, biome2: BiomeType) -> bool:
        """Check if two biomes can be adjacent to each other."""
        if biome1 == biome2:
            return True
        
        # Use cached adjacency if available
        cache_key = (biome1, biome2)
        if cache_key in self.biome_adjacency_cache:
            return self.biome_adjacency_cache[cache_key]
        
        # Check if biome2 is in biome1's allowed adjacent list
        adjacent_biomes = self.biome_config.get_adjacent_biomes(biome1)
        is_valid = biome2 in adjacent_biomes
        
        # Also check the reverse
        if not is_valid:
            reverse_adjacent = self.biome_config.get_adjacent_biomes(biome2)
            is_valid = biome1 in reverse_adjacent
        
        # Cache the result
        self.biome_adjacency_cache[cache_key] = is_valid
        self.biome_adjacency_cache[(biome2, biome1)] = is_valid
        
        return is_valid
    
    def _find_suitable_replacement_biome(self,
                                       current_biome: BiomeType,
                                       conflicting_neighbor: BiomeType,
                                       coord: HexCoordinate,
                                       biome_map: Dict[HexCoordinate, BiomeType],
                                       hex_grid: List[HexCoordinate]) -> BiomeType:
        """Find a biome that can be adjacent to all neighbors."""
        
        neighbors = self._get_hex_neighbors(coord, hex_grid)
        neighbor_biomes = set()
        
        for neighbor_coord in neighbors:
            if neighbor_coord in biome_map:
                neighbor_biomes.add(biome_map[neighbor_coord])
        
        # Try each possible biome
        for candidate_biome in BiomeType:
            is_compatible = True
            
            for neighbor_biome in neighbor_biomes:
                if not self._is_valid_biome_transition(candidate_biome, neighbor_biome):
                    is_compatible = False
                    break
            
            if is_compatible:
                return candidate_biome
        
        # If no perfect match, return the original biome
        return current_biome
    
    def _get_hex_neighbors(self, coord: HexCoordinate, hex_grid: List[HexCoordinate]) -> List[HexCoordinate]:
        """Get the neighboring hexes for a given coordinate."""
        # Hex grid neighbors in axial coordinates
        neighbor_offsets = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        
        neighbors = []
        for dq, dr in neighbor_offsets:
            neighbor = HexCoordinate(coord.q + dq, coord.r + dr)
            if neighbor in hex_grid:
                neighbors.append(neighbor)
        
        return neighbors 