"""
World generation utilities with improved maintainability.
"""

from typing import Dict, List, Optional, Tuple, Any
import random
import math
from dataclasses import dataclass
from app.core.utils.error_utils import GenerationError
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
        """Select an appropriate POI type based on biome and elevation."""
        poi_types = {
            'forest': ['clearing', 'ruins', 'cave', 'lake'],
            'desert': ['oasis', 'ruins', 'cave', 'dune'],
            'mountain': ['peak', 'cave', 'ruins', 'valley']
        }
        
        # Adjust probabilities based on elevation
        if elevation > 0.8:
            return 'peak' if biome == 'mountain' else 'cave'
        elif elevation < 0.2:
            return 'lake' if biome == 'forest' else 'oasis'
            
        return random.choice(poi_types.get(biome, ['ruins']))

def attempt_rest(region: str, poi: str) -> Dict[str, Any]:
    """
    Attempt to rest in a given region and point of interest.
    Returns success/failure and any relevant effects.
    
    Args:
        region (str): The region ID where the rest is attempted
        poi (str): The point of interest ID where the rest is attempted
        
    Returns:
        Dict[str, Any]: Result of the rest attempt containing:
            - success: bool indicating if rest was successful
            - message: str describing what happened
            - effects: list of effects that occurred
            - interruption: dict with interruption details if rest was interrupted
    """
    # Default safe rest chance - could be modified based on region/POI data
    rest_chance = 0.8
    
    # Random roll to determine if rest is successful
    if random.random() < rest_chance:
        return {
            "success": True,
            "message": "Rest completed successfully.",
            "effects": [
                "health_restored",
                "spells_recovered",
                "abilities_refreshed"
            ],
            "interruption": None
        }
    else:
        # Generate a random interruption
        interruptions = [
            {
                "type": "combat",
                "message": "Rest was interrupted by hostile creatures!",
                "encounter": "random_combat"
            },
            {
                "type": "environmental",
                "message": "A sudden storm forced you to seek shelter.",
                "effect": "fatigue"
            },
            {
                "type": "event",
                "message": "Strange noises kept you from getting proper rest.",
                "effect": "partial_recovery"
            }
        ]
        
        interruption = random.choice(interruptions)
        
        return {
            "success": False,
            "message": "Rest was interrupted!",
            "effects": ["partial_recovery"] if interruption["type"] == "event" else [],
            "interruption": interruption
        } 
