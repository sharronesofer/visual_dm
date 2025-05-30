"""
World generation utilities with optimized performance.
"""

import logging
import random
import math
from typing import Dict, Any, List, Optional, Tuple
from functools import lru_cache
from dataclasses import dataclass
from app.utils.config_utils import get_config
from backend.data.modding.loaders.game_data_registry import GameDataRegistry

logger = logging.getLogger(__name__)

@dataclass
class BiomeConfig:
    """Immutable biome configuration for efficient lookups."""
    enemy_types: List[str]
    resource_types: List[str]
    terrain: List[str]
    features: List[str]
    resources: Dict[str, float]

class WorldGenerator:
    """Generator for game world elements with optimized performance."""
    
    def __init__(self, data_dir: str = "backend/data/modding") -> None:
        self.config = get_config()
        self.registry = GameDataRegistry(data_dir)
        self.registry.load_all()
        self._biome_data = {b['id']: b for b in self.registry.all_biomes}
        self._biome_cache = {}
        self._elevation_cache = {}
        self._temperature_cache = {}
        self._humidity_cache = {}
    
    def generate_region(self, level: int, biome: str, size: str = 'medium') -> Dict[str, Any]:
        try:
            size_multipliers = {
                'small': 0.5,
                'medium': 1.0,
                'large': 2.0
            }
            biome_info = self._biome_data.get(biome, next(iter(self._biome_data.values())))
            features = {
                'level': level,
                'biome': biome,
                'size': size,
                'enemies': self._generate_enemies(
                    biome_info.get('enemy_types', []),
                    level,
                    size_multipliers[size]
                ),
                'resources': self._generate_resources(
                    biome_info.get('resource_types', []),
                    level,
                    size_multipliers[size]
                ),
                'terrain': self._generate_terrain(
                    biome_info.get('terrain', []),
                    size_multipliers[size]
                ),
                'points_of_interest': self._generate_pois(
                    level,
                    size_multipliers[size]
                )
            }
            logger.debug(f"Generated region: {features}")
            return features
        except Exception as e:
            logger.error(f"Failed to generate region: {str(e)}")
            raise
    
    @lru_cache(maxsize=512)
    def _generate_enemies(
        self,
        enemy_types: List[str],
        level: int,
        size_multiplier: float
    ) -> List[Dict[str, Any]]:
        """Generate enemies with caching."""
        try:
            num_enemies = int(5 * size_multiplier)
            enemies = []
            
            # Pre-compute enemy templates
            enemy_templates = {
                enemy_type: {
                    'health': lambda lvl: 10 * lvl,
                    'damage': lambda lvl: 2 * lvl,
                    'xp_value': lambda lvl: 10 * lvl
                }
                for enemy_type in enemy_types
            }
            
            for _ in range(num_enemies):
                enemy_type = random.choice(enemy_types)
                enemy_level = max(1, level + random.randint(-2, 2))
                template = enemy_templates[enemy_type]
                
                enemy = {
                    'type': enemy_type,
                    'level': enemy_level,
                    'health': template['health'](enemy_level),
                    'damage': template['damage'](enemy_level),
                    'xp_value': template['xp_value'](enemy_level)
                }
                
                enemies.append(enemy)
            
            return enemies
            
        except Exception as e:
            logger.error(f"Failed to generate enemies: {str(e)}")
            return []
    
    @lru_cache(maxsize=512)
    def _generate_resources(
        self,
        resource_types: List[str],
        level: int,
        size_multiplier: float
    ) -> List[Dict[str, Any]]:
        """Generate resources with caching."""
        try:
            num_resources = int(8 * size_multiplier)
            resources = []
            
            # Pre-compute resource templates
            resource_templates = {
                resource_type: {
                    'quantity': lambda lvl: random.randint(1, 5) * lvl,
                    'quality': lambda: random.randint(1, 5)
                }
                for resource_type in resource_types
            }
            
            for _ in range(num_resources):
                resource_type = random.choice(resource_types)
                resource_level = max(1, level + random.randint(-1, 1))
                template = resource_templates[resource_type]
                
                resource = {
                    'type': resource_type,
                    'level': resource_level,
                    'quantity': template['quantity'](resource_level),
                    'quality': template['quality']()
                }
                
                resources.append(resource)
            
            return resources
            
        except Exception as e:
            logger.error(f"Failed to generate resources: {str(e)}")
            return []
    
    @lru_cache(maxsize=512)
    def _generate_terrain(
        self,
        terrain_types: List[str],
        size_multiplier: float
    ) -> List[Dict[str, Any]]:
        """Generate terrain features with caching."""
        try:
            num_features = int(6 * size_multiplier)
            terrain = []
            
            # Pre-compute terrain templates
            terrain_templates = {
                terrain_type: {
                    'size': lambda: random.choice(['small', 'medium', 'large']),
                    'difficulty': lambda: random.randint(1, 5)
                }
                for terrain_type in terrain_types
            }
            
            for _ in range(num_features):
                feature_type = random.choice(terrain_types)
                template = terrain_templates[feature_type]
                
                feature = {
                    'type': feature_type,
                    'size': template['size'](),
                    'difficulty': template['difficulty']()
                }
                
                terrain.append(feature)
            
            return terrain
            
        except Exception as e:
            logger.error(f"Failed to generate terrain: {str(e)}")
            return []
    
    @lru_cache(maxsize=512)
    def _generate_pois(
        self,
        level: int,
        size_multiplier: float
    ) -> List[Dict[str, Any]]:
        """Generate points of interest with caching."""
        try:
            num_pois = int(4 * size_multiplier)
            pois = []
            
            # Pre-compute POI templates
            poi_types = [
                'ruin', 'shrine', 'camp', 'village',
                'tower', 'bridge', 'monument', 'cave'
            ]
            
            poi_templates = {
                poi_type: {
                    'difficulty': lambda: random.randint(1, 5),
                    'rewards': lambda lvl: {
                        'xp': 20 * lvl,
                        'gold': 10 * lvl
                    }
                }
                for poi_type in poi_types
            }
            
            for _ in range(num_pois):
                poi_type = random.choice(poi_types)
                poi_level = max(1, level + random.randint(-1, 1))
                template = poi_templates[poi_type]
                
                poi = {
                    'type': poi_type,
                    'level': poi_level,
                    'difficulty': template['difficulty'](),
                    'rewards': template['rewards'](poi_level)
                }
                
                pois.append(poi)
            
            return pois
            
        except Exception as e:
            logger.error(f"Failed to generate POIs: {str(e)}")
            return []
    
    def generate_dungeon(
        self,
        level: int,
        theme: str,
        size: str = 'medium'
    ) -> Dict[str, Any]:
        """Generate a dungeon"""
        try:
            # Size multipliers
            size_multipliers = {
                'small': 0.5,
                'medium': 1.0,
                'large': 2.0
            }
            
            # Theme characteristics
            theme_data = {
                'crypt': {
                    'enemy_types': ['skeleton', 'ghost', 'zombie'],
                    'trap_types': ['pit', 'arrow', 'poison'],
                    'room_types': ['tomb', 'shrine', 'catacomb']
                },
                'cavern': {
                    'enemy_types': ['spider', 'bat', 'troglodyte'],
                    'trap_types': ['falling rocks', 'web', 'acid'],
                    'room_types': ['cave', 'chamber', 'tunnel']
                },
                'fortress': {
                    'enemy_types': ['guard', 'knight', 'mage'],
                    'trap_types': ['portcullis', 'flame', 'spike'],
                    'room_types': ['hall', 'barracks', 'treasury']
                }
            }
            
            # Get theme data
            theme_info = theme_data.get(theme, theme_data['crypt'])
            
            # Generate dungeon features
            features = {
                'level': level,
                'theme': theme,
                'size': size,
                'enemies': self._generate_enemies(
                    theme_info['enemy_types'],
                    level,
                    size_multipliers[size]
                ),
                'traps': self._generate_traps(
                    theme_info['trap_types'],
                    level,
                    size_multipliers[size]
                ),
                'rooms': self._generate_rooms(
                    theme_info['room_types'],
                    size_multipliers[size]
                ),
                'treasure': self._generate_treasure(
                    level,
                    size_multipliers[size]
                )
            }
            
            logger.debug(f"Generated dungeon: {features}")
            return features
            
        except Exception as e:
            logger.error(f"Failed to generate dungeon: {str(e)}")
            raise
    
    def _generate_traps(
        self,
        trap_types: List[str],
        level: int,
        size_multiplier: float
    ) -> List[Dict[str, Any]]:
        """Generate traps for a dungeon"""
        try:
            num_traps = int(3 * size_multiplier)
            traps = []
            
            for _ in range(num_traps):
                trap_type = random.choice(trap_types)
                trap_level = max(1, level + random.randint(-1, 1))
                
                trap = {
                    'type': trap_type,
                    'level': trap_level,
                    'damage': 5 * trap_level,
                    'difficulty': random.randint(1, 5)
                }
                
                traps.append(trap)
            
            return traps
            
        except Exception as e:
            logger.error(f"Failed to generate traps: {str(e)}")
            return []
    
    def _generate_rooms(
        self,
        room_types: List[str],
        size_multiplier: float
    ) -> List[Dict[str, Any]]:
        """Generate rooms for a dungeon"""
        try:
            num_rooms = int(8 * size_multiplier)
            rooms = []
            
            for _ in range(num_rooms):
                room_type = random.choice(room_types)
                
                room = {
                    'type': room_type,
                    'size': random.choice(['small', 'medium', 'large']),
                    'contents': random.choice(['empty', 'enemies', 'treasure', 'trap'])
                }
                
                rooms.append(room)
            
            return rooms
            
        except Exception as e:
            logger.error(f"Failed to generate rooms: {str(e)}")
            return []
    
    def _generate_treasure(
        self,
        level: int,
        size_multiplier: float
    ) -> List[Dict[str, Any]]:
        """Generate treasure for a dungeon"""
        try:
            num_treasures = int(2 * size_multiplier)
            treasures = []
            
            for _ in range(num_treasures):
                treasure_type = random.choice(['gold', 'item', 'artifact'])
                treasure_level = max(1, level + random.randint(-1, 1))
                
                treasure = {
                    'type': treasure_type,
                    'level': treasure_level,
                    'value': 50 * treasure_level,
                    'rarity': random.randint(1, 5)
                }
                
                treasures.append(treasure)
            
            return treasures
            
        except Exception as e:
            logger.error(f"Failed to generate treasure: {str(e)}")
            return [] 