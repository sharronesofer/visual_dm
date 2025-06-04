"""
Biome Placement Engine

Handles intelligent biome placement based on environmental factors,
adjacency rules, and configuration-driven constraints.

Refactored to use dependency injection pattern for better separation of concerns.
"""

import random
from typing import Dict, List, Set, Tuple, Any
from backend.systems.region.models import BiomeType, HexCoordinate


class BiomePlacementEngine:
    """Engine for placing biomes according to environmental and adjacency rules."""
    
    def __init__(self, placement_rules: Dict[str, Any]):
        """Initialize with placement rules configuration data"""
        self.placement_rules = placement_rules
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
        clustering_factor = self.placement_rules.get('default_clustering_factor', 0.5)
        if hasattr(config, 'biome_diversity') and config.biome_diversity > 0:
            clustering_factor = config.biome_diversity
            
        if clustering_factor > 0:
            biome_map = self._apply_biome_clustering(biome_map, hex_grid, clustering_factor)
        
        # Third pass: validate and fix adjacency rules
        if self.placement_rules.get('validation_enabled', True):
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
            biome_data = self.placement_rules.get('biomes', {}).get(biome_type.value, {})
            rarity = biome_data.get('rarity', 1.0)
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
        
        # Get biome requirements from configuration
        biome_data = self.placement_rules.get('biomes', {}).get(biome_type.value, {})
        temp_range = biome_data.get('temperature_range', (0.0, 1.0))
        humidity_range = biome_data.get('humidity_range', (0.0, 1.0))
        
        # Get environmental weights from configuration
        weights = self.placement_rules.get('environmental_weights', {
            'temperature': 0.4,
            'humidity': 0.4,
            'elevation': 0.2
        })
        
        # Calculate fit scores for each environmental factor
        temp_score = self._calculate_range_score(temperature, temp_range)
        humidity_score = self._calculate_range_score(humidity, humidity_range)
        
        # Elevation scoring
        elevation_score = 1.0  # Default: elevation doesn't matter much
        
        # Check for elevation bonuses from configuration
        elevation_bonus = biome_data.get('elevation_bonus', {})
        if elevation_bonus:
            if 'min_elevation' in elevation_bonus and elevation > elevation_bonus['min_elevation']:
                elevation_score = elevation_bonus.get('bonus_multiplier', 1.5)
            elif 'max_elevation' in elevation_bonus and elevation < elevation_bonus['max_elevation']:
                elevation_score = elevation_bonus.get('bonus_multiplier', 1.2)
        
        # Combine scores using configured weights
        overall_score = (
            temp_score * weights.get('temperature', 0.4) + 
            humidity_score * weights.get('humidity', 0.4) + 
            elevation_score * weights.get('elevation', 0.2)
        )
        
        return overall_score
    
    def _calculate_range_score(self, value: float, range_tuple: Tuple[float, float]) -> float:
        """Calculate how well a value fits within a range (0.0 to 1.0+)."""
        min_val, max_val = range_tuple
        
        # Get range scoring configuration
        range_config = self.placement_rules.get('range_scoring', {})
        center_penalty = range_config.get('perfect_fit_center_penalty', 0.2)
        decay_base = range_config.get('outside_range_decay_base', 0.8)
        decay_multiplier = range_config.get('outside_range_decay_multiplier', 10)
        
        if min_val <= value <= max_val:
            # Perfect fit - score based on distance from center
            center = (min_val + max_val) / 2
            distance_from_center = abs(value - center) / ((max_val - min_val) / 2)
            return 1.0 - distance_from_center * center_penalty
        else:
            # Outside range - score based on distance from nearest edge
            if value < min_val:
                distance = min_val - value
            else:
                distance = value - max_val
            
            # Exponential decay outside the range
            return max(0.0, decay_base ** (distance * decay_multiplier))
    
    def _apply_biome_clustering(self,
                               biome_map: Dict[HexCoordinate, BiomeType],
                               hex_grid: List[HexCoordinate],
                               clustering_factor: float) -> Dict[HexCoordinate, BiomeType]:
        """Apply clustering to make biomes form more natural groupings."""
        
        clustered_map = biome_map.copy()
        
        # Get clustering configuration
        max_iterations = self.placement_rules.get('max_clustering_iterations', 3)
        
        # Multiple passes for better clustering
        for _ in range(max_iterations):
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
        max_iterations = self.placement_rules.get('max_validation_iterations', 5)
        
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
                            # Invalid adjacency found - fix it
                            replacement_biome = self._find_suitable_replacement_biome(
                                current_biome, neighbor_biome, coord, validated_map, hex_grid
                            )
                            if replacement_biome != current_biome:
                                validated_map[coord] = replacement_biome
                                changes_made = True
                                break
        
        return validated_map
    
    def _is_valid_biome_transition(self, biome1: BiomeType, biome2: BiomeType) -> bool:
        """Check if two biomes can be adjacent to each other."""
        
        # Get transition rules from configuration
        transitions = self.placement_rules.get('biome_transitions', {})
        biome1_transitions = transitions.get(biome1.value, {})
        
        # Check if transition is explicitly allowed or forbidden
        if biome2.value in biome1_transitions:
            return biome1_transitions[biome2.value]
        
        # Default rules if not configured
        incompatible_pairs = [
            (BiomeType.DESERT, BiomeType.ARCTIC),
            (BiomeType.TROPICAL_RAINFOREST, BiomeType.TUNDRA),
            (BiomeType.SWAMP, BiomeType.DESERT),
        ]
        
        for pair in incompatible_pairs:
            if (biome1, biome2) in [pair, pair[::-1]]:
                return False
        
        return True  # Allow by default
    
    def _find_suitable_replacement_biome(self,
                                       current_biome: BiomeType,
                                       conflicting_neighbor: BiomeType,
                                       coord: HexCoordinate,
                                       biome_map: Dict[HexCoordinate, BiomeType],
                                       hex_grid: List[HexCoordinate]) -> BiomeType:
        """Find a suitable replacement biome that doesn't conflict with neighbors."""
        
        neighbors = self._get_hex_neighbors(coord, hex_grid)
        neighbor_biomes = [biome_map.get(n) for n in neighbors if n in biome_map]
        
        # Try to find a biome that works with all neighbors
        for biome_type in BiomeType:
            compatible = True
            for neighbor_biome in neighbor_biomes:
                if neighbor_biome and not self._is_valid_biome_transition(biome_type, neighbor_biome):
                    compatible = False
                    break
            
            if compatible:
                return biome_type
        
        # If no perfect match, return a neutral biome
        return BiomeType.TEMPERATE_FOREST
    
    def _get_hex_neighbors(self, coord: HexCoordinate, hex_grid: List[HexCoordinate]) -> List[HexCoordinate]:
        """Get valid neighboring hexes for a coordinate."""
        possible_neighbors = [
            HexCoordinate(coord.q + 1, coord.r - 1, coord.s),
            HexCoordinate(coord.q + 1, coord.r, coord.s - 1),
            HexCoordinate(coord.q, coord.r + 1, coord.s - 1),
            HexCoordinate(coord.q - 1, coord.r + 1, coord.s),
            HexCoordinate(coord.q - 1, coord.r, coord.s + 1),
            HexCoordinate(coord.q, coord.r - 1, coord.s + 1),
        ]
        
        return [n for n in possible_neighbors if n in hex_grid] 