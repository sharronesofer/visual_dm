"""
World Generation Utilities for Region System

This module contains utilities for generating regions and their properties.
"""

from typing import Dict, List, Optional, Tuple, Any
import random
import math
from dataclasses import dataclass

from backend.core.utils.error import GenerationError
from backend.data.modding.loaders.game_data_registry import GameDataRegistry

@dataclass
class BiomeConfig:
    """Configuration for biome generation."""
    name: str
    temperature_range: Tuple[float, float]
    humidity_range: Tuple[float, float]
    elevation_range: Tuple[float, float]
    features: List[str]
    resources: Dict[str, float]

class WorldGenerator:
    """Handles world generation with modular components."""
    
    def __init__(self, seed: Optional[int] = None, data_dir: str = "backend/data/modding"):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        self.registry = GameDataRegistry(data_dir)
        self.registry.load_all()
        self.biome_configs = {b['id']: b for b in self.registry.all_biomes}
        
    def _load_biome_configs(self):
        # Deprecated: now loaded from registry
        return self.biome_configs
        
    def generate_region(self, x: int, y: int, size: int) -> Dict:
        """Generate a region with its characteristics."""
        try:
            # Generate base characteristics
            elevation = self._generate_elevation(x, y, size)
            temperature = self._generate_temperature(x, y, elevation)
            humidity = self._generate_humidity(x, y, elevation)
            
            # Determine biome
            biome = self._determine_biome(elevation, temperature, humidity)
            biome_config = self.biome_configs[biome]
            
            # Generate features and resources
            features = self._generate_features(biome_config)
            resources = self._generate_resources(biome_config)
            
            # Generate points of interest
            pois = self._generate_pois(biome, elevation, size)
            
            return {
                'coordinates': {'x': x, 'y': y},
                'size': size,
                'biome': biome,
                'elevation': elevation,
                'temperature': temperature,
                'humidity': humidity,
                'features': features,
                'resources': resources,
                'pois': pois
            }
            
        except Exception as e:
            raise GenerationError(f"Failed to generate region: {str(e)}")
            
    def _generate_elevation(self, x: int, y: int, size: int) -> float:
        """Generate elevation using Perlin noise."""
        try:
            # Simplified elevation generation
            noise = math.sin(x * 0.1) * math.cos(y * 0.1)
            elevation = (noise + 1) / 2  # Normalize to 0-1
            
            # Add some randomness
            elevation += random.uniform(-0.1, 0.1)
            return max(0.0, min(1.0, elevation))
            
        except Exception as e:
            raise GenerationError(f"Failed to generate elevation: {str(e)}")
            
    def _generate_temperature(self, x: int, y: int, elevation: float) -> float:
        """Generate temperature based on coordinates and elevation."""
        try:
            # Base temperature from coordinates
            base_temp = math.sin(x * 0.05) * 0.5 + 0.5
            
            # Adjust for elevation (higher = colder)
            elevation_factor = 1 - (elevation * 0.7)
            
            # Add some randomness
            random_factor = random.uniform(-0.1, 0.1)
            
            return max(0.0, min(1.0, base_temp * elevation_factor + random_factor))
            
        except Exception as e:
            raise GenerationError(f"Failed to generate temperature: {str(e)}")
            
    def _generate_humidity(self, x: int, y: int, elevation: float) -> float:
        """Generate humidity based on coordinates and elevation."""
        try:
            # Base humidity from coordinates
            base_humidity = math.cos(x * 0.05) * 0.5 + 0.5
            
            # Adjust for elevation (higher = more precipitation)
            elevation_factor = elevation * 0.3 + 0.7
            
            # Add some randomness
            random_factor = random.uniform(-0.1, 0.1)
            
            return max(0.0, min(1.0, base_humidity * elevation_factor + random_factor))
            
        except Exception as e:
            raise GenerationError(f"Failed to generate humidity: {str(e)}")
            
    def _determine_biome(self, elevation: float, temperature: float, humidity: float) -> str:
        """Determine the biome based on environmental factors."""
        try:
            # Score each biome based on how well it matches the conditions
            scores = {}
            for biome_id, config in self.biome_configs.items():
                temp_range = config.get('temperature_range', (0.0, 1.0))
                humid_range = config.get('humidity_range', (0.0, 1.0))
                elev_range = config.get('elevation_range', (0.0, 1.0))
                temp_score = self._calculate_factor_score(temperature, temp_range)
                humid_score = self._calculate_factor_score(humidity, humid_range)
                elev_score = self._calculate_factor_score(elevation, elev_range)
                scores[biome_id] = (
                    temp_score * 0.4 +
                    humid_score * 0.3 +
                    elev_score * 0.3
                )
            return max(scores.items(), key=lambda x: x[1])[0]
        except Exception as e:
            raise GenerationError(f"Failed to determine biome: {str(e)}")
            
    def _calculate_factor_score(self, value: float, range_tuple: Tuple[float, float]) -> float:
        """Calculate how well a value fits within a range."""
        min_val, max_val = range_tuple
        if value < min_val:
            return 1 - (min_val - value)
        elif value > max_val:
            return 1 - (value - max_val)
        else:
            return 1.0
            
    def _generate_features(self, biome_config) -> List[str]:
        """Generate features for a biome."""
        try:
            features = []
            for feature in biome_config.get('features', []):
                if random.random() < 0.7:
                    features.append(feature)
            return features
        except Exception as e:
            raise GenerationError(f"Failed to generate features: {str(e)}")
            
    def _generate_resources(self, biome_config) -> Dict[str, float]:
        """Generate resources for a biome."""
        try:
            resources = {}
            for resource, base_chance in biome_config.get('resources', {}).items():
                amount = base_chance * random.uniform(0.8, 1.2)
                resources[resource] = max(0.0, min(1.0, amount))
            return resources
        except Exception as e:
            raise GenerationError(f"Failed to generate resources: {str(e)}")
            
    def _generate_pois(self, biome: str, elevation: float, size: int) -> List[Dict]:
        """Generate points of interest for a region."""
        try:
            pois = []
            num_pois = random.randint(1, 3)  # 1-3 POIs per region
            
            for _ in range(num_pois):
                poi_type = self._select_poi_type(biome, elevation)
                pois.append({
                    'type': poi_type,
                    'coordinates': {
                        'x': random.uniform(-size/2, size/2),
                        'y': random.uniform(-size/2, size/2)
                    },
                    'size': random.uniform(0.1, 0.3) * size
                })
            
            return pois
        except Exception as e:
            raise GenerationError(f"Failed to generate POIs: {str(e)}")
            
    def _select_poi_type(self, biome: str, elevation: float) -> str:
        """Select a POI type based on biome and elevation."""
        try:
            # Higher chance of dungeons in mountains, settlements in plains, etc.
            poi_types = {
                'settlement': 0.4,
                'dungeon': 0.2,
                'landmark': 0.3,
                'resource_node': 0.1
            }
            
            # Adjust based on biome and elevation
            if biome == 'mountain':
                poi_types['dungeon'] += 0.2
                poi_types['settlement'] -= 0.2
            elif biome == 'plains':
                poi_types['settlement'] += 0.2
                poi_types['dungeon'] -= 0.1
                
            if elevation > 0.7:
                poi_types['dungeon'] += 0.1
            elif elevation < 0.3:
                poi_types['settlement'] += 0.1
                
            return random.choices(
                list(poi_types.keys()),
                weights=list(poi_types.values()),
                k=1
            )[0]
        except Exception as e:
            raise GenerationError(f"Failed to select POI type: {str(e)}")

def attempt_rest(region: str, poi: str) -> Dict[str, Any]:
    """
    Utility function for resting in a region/POI.
    
    Args:
        region: The region ID
        poi: The POI ID
        
    Returns:
        Dict with rest result details
    """
    from datetime import datetime
    from uuid import uuid4
    
    # Calculate rest quality based on POI safety
    rest_quality = random.uniform(0.3, 1.0)
    
    # Chance of random encounter during rest
    encounter_chance = 0.2 * (1 - rest_quality)  # Lower quality, higher encounter chance
    
    encounter = None
    if random.random() < encounter_chance:
        encounter_types = ['hostile', 'neutral', 'beneficial']
        encounter_type = random.choice(encounter_types)
        encounter = {
            'type': encounter_type,
            'description': f"A {encounter_type} encounter occurred during rest"
        }
    
    # Calculate recovery based on rest quality
    health_recovery = random.randint(5, 20) * rest_quality
    
    return {
        'rest_id': str(uuid4()),
        'timestamp': datetime.utcnow().isoformat(),
        'region_id': region,
        'poi_id': poi,
        'rest_quality': rest_quality,
        'health_recovery': health_recovery,
        'encounter': encounter,
        'success': True if not encounter or encounter.get('type') != 'hostile' else False
    } 