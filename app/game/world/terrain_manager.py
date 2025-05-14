"""Utility functions for managing terrain generation and manipulation."""

import random
from typing import Dict, List, Tuple
from app.models.region import Region
from app.core.database import db

class TerrainManager:
    def __init__(self):
        self.terrain_types = {
            'plains': {
                'movement_cost': 1,
                'features': ['grass', 'flowers', 'small trees'],
                'resources': ['herbs', 'small game']
            },
            'forest': {
                'movement_cost': 2,
                'features': ['trees', 'undergrowth', 'streams'],
                'resources': ['wood', 'berries', 'game']
            },
            'mountains': {
                'movement_cost': 3,
                'features': ['rocks', 'cliffs', 'caves'],
                'resources': ['ore', 'gems', 'herbs']
            },
            'desert': {
                'movement_cost': 2,
                'features': ['dunes', 'cacti', 'oases'],
                'resources': ['water', 'minerals']
            },
            'swamp': {
                'movement_cost': 3,
                'features': ['mud', 'reeds', 'pools'],
                'resources': ['herbs', 'fish']
            }
        }

    def generate_terrain(self, width: int, height: int) -> List[List[Dict]]:
        """Generate a terrain grid of given dimensions."""
        terrain = []
        for y in range(height):
            row = []
            for x in range(width):
                tile = self.generate_tile(x, y)
                row.append(tile)
            terrain.append(row)
        return terrain

    def generate_tile(self, x: int, y: int) -> Dict:
        """Generate a single terrain tile."""
        terrain_type = random.choice(list(self.terrain_types.keys()))
        base_info = self.terrain_types[terrain_type].copy()
        
        tile = {
            'x': x,
            'y': y,
            'type': terrain_type,
            'elevation': random.randint(0, 100),
            'features': random.sample(base_info['features'], k=random.randint(1, len(base_info['features']))),
            'resources': random.sample(base_info['resources'], k=random.randint(0, len(base_info['resources']))),
            'movement_cost': base_info['movement_cost']
        }
        return tile

    def get_movement_cost(self, terrain_type: str) -> int:
        """Get the movement cost for a terrain type."""
        return self.terrain_types.get(terrain_type, {'movement_cost': 1})['movement_cost']

    def get_available_resources(self, terrain_type: str) -> List[str]:
        """Get available resources for a terrain type."""
        return self.terrain_types.get(terrain_type, {'resources': []})['resources']

    def modify_terrain(self, region_id: int, x: int, y: int, modifications: Dict) -> bool:
        """Modify terrain at specific coordinates."""
        try:
            region = Region.query.get(region_id)
            if not region or not region.terrain:
                return False

            if 0 <= y < len(region.terrain) and 0 <= x < len(region.terrain[0]):
                for key, value in modifications.items():
                    region.terrain[y][x][key] = value
                
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            db.session.rollback()
            print(f"Error modifying terrain: {str(e)}")
            return False

    def get_surrounding_tiles(self, terrain: List[List[Dict]], x: int, y: int) -> List[Dict]:
        """Get all adjacent tiles for a given position."""
        surrounding = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                new_x = x + dx
                new_y = y + dy
                
                if (0 <= new_y < len(terrain) and 
                    0 <= new_x < len(terrain[0])):
                    surrounding.append(terrain[new_y][new_x])
                    
        return surrounding

    def calculate_path_cost(self, terrain: List[List[Dict]], start: Tuple[int, int], end: Tuple[int, int]) -> int:
        """Calculate movement cost between two points."""
        if not self._is_valid_position(terrain, start) or not self._is_valid_position(terrain, end):
            return -1
            
        start_x, start_y = start
        end_x, end_y = end
        
        # Simple Manhattan distance * average movement cost
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        distance = dx + dy
        
        avg_cost = (
            self.get_movement_cost(terrain[start_y][start_x]['type']) +
            self.get_movement_cost(terrain[end_y][end_x]['type'])
        ) / 2
        
        return int(distance * avg_cost)

    def _is_valid_position(self, terrain: List[List[Dict]], pos: Tuple[int, int]) -> bool:
        """Check if a position is valid within the terrain."""
        x, y = pos
        return (0 <= y < len(terrain) and 
                0 <= x < len(terrain[0])) 