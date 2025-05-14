"""
Terrain management utilities for the visual client.
Handles terrain loading and viewport management.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import requests
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class TerrainManager:
    """
    Manages terrain data and viewport for the visual client.
    Handles loading and caching of terrain data.
    """
    
    def __init__(self, region_id: Optional[str] = None, character_id: Optional[str] = None):
        """Initialize the terrain manager with optional region and character IDs."""
        self.region_id = region_id
        self.character_id = character_id
        self.terrain_cache: Dict[str, dict] = {}
        self.loading_queue: set = set()
        self.base_url = "https://visual-dm-default-rtdb.firebaseio.com"
        
        # Load terrain types
        self._load_terrain_types()
        
    def _load_terrain_types(self) -> None:
        """Load terrain types from the JSON file."""
        try:
            terrain_types_path = Path(__file__).parent.parent / 'data' / 'terrain_types.json'
            if terrain_types_path.exists():
                with open(terrain_types_path, 'r') as f:
                    self.terrain_types = json.load(f)
            else:
                logger.warning("Terrain types file not found")
                self.terrain_types = {}
        except Exception as e:
            logger.error(f"Error loading terrain types: {e}")
            self.terrain_types = {}

    def get_terrain(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Get terrain data for coordinates."""
        try:
            key = f"{x},{y}"
            if key in self.terrain_cache:
                return self.terrain_cache[key]
            
            if key in self.loading_queue:
                return None
                
            self.loading_queue.add(key)
            terrain_data = self._fetch_terrain(x, y)
            self.loading_queue.remove(key)
            
            if terrain_data:
                self.terrain_cache[key] = terrain_data
                return terrain_data
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting terrain: {e}")
            return None

    def _fetch_terrain(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """Fetch terrain data from Firebase."""
        try:
            coord_key = f"{x}_{y}"
            response = requests.get(
                f"{self.base_url}/locations/{coord_key}.json",
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if data:
                # Map terrain type to our internal format
                terrain_type = data.get("terrain_type", "unknown")
                if terrain_type in self.terrain_types:
                    data.update(self.terrain_types[terrain_type])
                    
                return {
                    "tags": [terrain_type],
                    "properties": data
                }
            return None
            
        except Exception as e:
            logger.error(f"Error fetching terrain: {e}")
            return None

    def get_viewport_terrain(self, x: int, y: int, radius: int) -> Dict[str, dict]:
        """
        Get terrain data for a viewport centered at (x, y) with given radius.
        Used by the client for rendering the map.
        """
        viewport_terrain = {}
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = x + dx, y + dy
                terrain = self.get_terrain(nx, ny)
                if terrain:
                    viewport_terrain[f"{nx}_{ny}"] = terrain
        return viewport_terrain

    def _update_character_knowledge(self, x: int, y: int, terrain_data: dict) -> None:
        """Update character's knowledge of terrain."""
        if not self.character_id:
            return
            
        try:
            # Update character's known tiles in Firebase
            known_tiles_path = f"/characters/{self.character_id}/known_tiles"
            response = requests.get(f"{self.base_url}{known_tiles_path}.json")
            known_tiles = response.json() or []
            
            if f"{x}_{y}" not in known_tiles:
                known_tiles.append(f"{x}_{y}")
                requests.put(f"{self.base_url}{known_tiles_path}.json", json=known_tiles)
                logger.debug(f"Updated character {self.character_id} knowledge with tile {x}_{y}")
        except Exception as e:
            logger.error(f"Error updating character knowledge: {e}") 