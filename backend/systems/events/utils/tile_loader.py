import pygame
import os
import random
import json
from pathlib import Path
from typing import Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for tile dimensions
TILE_WIDTH = 32
TILE_HEIGHT = 32
Y_OFFSET = 0

# Load land types from JSON
def load_land_types():
    try:
        json_path = Path(__file__).resolve().parents[1] / "rules_json" / "land_types.json"
        with open(json_path, 'r') as f:
            land_types = json.load(f)
        print(f"✅ Loaded {len(land_types)} land types from JSON")
        return land_types
    except Exception as e:
        print(f"❌ Error loading land types: {e}")
        return {}

# Map terrain types to tile coordinates
terrain_to_tile = {
    "forest": (0, 0),
    "plains": (1, 0),
    "mountain": (2, 0),
    "desert": (3, 0),
    "swamp": (4, 0),
    "tundra": (5, 0),
    "ocean": (6, 0),
    "river": (7, 0),
    "lake": (8, 0),
    "city": (9, 0),
    "village": (10, 0),
    "ruins": (11, 0),
    "cave": (12, 0),
    "volcano": (13, 0),
    "glacier": (14, 0),
    "unknown": (15, 0)
}

def validate_surface(surface: pygame.Surface) -> bool:
    """Validate that a surface is valid and has the correct dimensions."""
    if not isinstance(surface, pygame.Surface):
        return False
    if surface.get_width() < TILE_WIDTH or surface.get_height() < TILE_HEIGHT:
        return False
    return True

def load_tileset(tileset_path: str) -> Optional[pygame.Surface]:
    """Load the tileset image and validate it."""
    try:
        tileset = pygame.image.load(tileset_path)
        if not validate_surface(tileset):
            logger.error(f"Invalid tileset dimensions: {tileset.get_width()}x{tileset.get_height()}")
            return None
        return tileset
    except Exception as e:
        logger.error(f"Error loading tileset: {e}")
        return None

def slice_tile(tileset: pygame.Surface, x: int, y: int) -> Optional[pygame.Surface]:
    """Slice a tile from the tileset at the given coordinates."""
    try:
        if not validate_surface(tileset):
            return None
            
        # Calculate source rectangle
        src_x = x * TILE_WIDTH
        src_y = y * TILE_HEIGHT + Y_OFFSET
        
        # Validate coordinates
        if src_x + TILE_WIDTH > tileset.get_width() or src_y + TILE_HEIGHT > tileset.get_height():
            logger.error(f"Invalid tile coordinates: ({x}, {y})")
            return None
            
        # Create new surface and blit the tile
        tile = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
        tile.blit(tileset, (0, 0), (src_x, src_y, TILE_WIDTH, TILE_HEIGHT))
        return tile
    except Exception as e:
        logger.error(f"Error slicing tile: {e}")
        return None

def build_terrain_tile_map() -> Dict[str, pygame.Surface]:
    """Build a mapping of terrain types to their corresponding tile surfaces."""
    terrain_tiles = {}
    
    # Load tileset
    tileset_path = Path(__file__).resolve().parent.parent / "assets" / "tiles" / "fantasyhextiles_v3.png"
    if not tileset_path.exists():
        logger.error(f"Tileset not found at {tileset_path}")
        return terrain_tiles
        
    tileset = load_tileset(str(tileset_path))
    
    if not tileset:
        logger.error("Failed to load tileset")
        return terrain_tiles
        
    # Create tiles for each terrain type
    for terrain, (x, y) in terrain_to_tile.items():
        tile = slice_tile(tileset, x, y)
        if tile:
            terrain_tiles[terrain] = tile
            logger.debug(f"Created tile for terrain: {terrain}")
        else:
            logger.warning(f"Failed to create tile for terrain: {terrain}")
            
    return terrain_tiles

def random_color_for_terrain(terrain):
    """Generate a stable pseudo-random color for each terrain based on hash."""
    land_types = load_land_types()
    if terrain in land_types:
        # Use danger range to influence color
        danger_range = land_types[terrain].get("danger_range", [0, 5])
        danger_level = sum(danger_range) / 2
        # More dangerous = more red
        r = min(255, int(danger_level * 25))
        # More populated = more green
        pop_mod = land_types[terrain].get("population_modifier", 1.0)
        g = min(255, int(pop_mod * 100))
        # Rarity influences blue
        rarity = land_types[terrain].get("rarity", 5)
        b = min(255, int((10 - rarity) * 25))
        return (r, g, b)
    else:
        # Fallback to random color
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class TileLoader:
    def __init__(self):
        self.terrain_tiles = {}
        self.tileset = None
        self._load_tileset()
        
    def _load_tileset(self):
        """Load the tileset image and validate it."""
        try:
            tileset_path = Path(__file__).resolve().parent.parent / "assets" / "tiles" / "fantasyhextiles_v3.png"
            if not tileset_path.exists():
                logger.error(f"Tileset not found at {tileset_path}")
                return
                
            self.tileset = pygame.image.load(str(tileset_path))
            if not validate_surface(self.tileset):
                logger.error(f"Invalid tileset dimensions: {self.tileset.get_width()}x{self.tileset.get_height()}")
                return
                
            self.terrain_tiles = build_terrain_tile_map()
            logger.info(f"Loaded {len(self.terrain_tiles)} terrain tiles")
        except Exception as e:
            logger.error(f"Error loading tileset: {e}")
            
    def get_tile(self, terrain_type: str) -> Optional[pygame.Surface]:
        """Get a tile surface for the given terrain type."""
        return self.terrain_tiles.get(terrain_type)
        
    def get_random_color(self, terrain_type: str) -> tuple:
        """Get a random color for the given terrain type."""
        return random_color_for_terrain(terrain_type)

# Example usage
# tileset = load_tileset("assets/terrain/my_tilesheet.png")
# terrain_tiles = build_terrain_tile_map(tileset)
# surface = terrain_tiles["forest"]
# screen.blit(surface, (x, y))
