"""
Functions for transitioning between region and tactical maps.
"""

from typing import Optional, Tuple, List, Dict
from .hex_grid import HexGrid
from .tactical_hex_grid import TacticalHexGrid
from app.core.models.region import Region

def region_to_tactical(
    region_grid: HexGrid,
    center_q: int,
    center_r: int,
    size: int
) -> TacticalHexGrid:
    """
    Extract a square area from the region grid and return a tactical grid.
    
    Args:
        region_grid: The full region HexGrid
        center_q: Center q coordinate
        center_r: Center r coordinate
        size: Side length of the square area (odd number recommended)
        
    Returns:
        A new TacticalHexGrid representing the extracted area
    """
    half = size // 2
    tactical_grid = TacticalHexGrid(size, size)
    
    for dq in range(-half, half + 1):
        for dr in range(-half, half + 1):
            q = center_q + dq
            r = center_r + dr
            region_cell = region_grid.get(q, r)
            
            tq = dq + half
            tr = dr + half
            tactical_cell = tactical_grid.get(tq, tr)
            
            if region_cell and tactical_cell:
                tactical_cell.terrain = region_cell.terrain
                tactical_cell.elevation = region_cell.elevation
                tactical_cell.weather = region_cell.weather
                
                # Set combat props based on terrain
                props = {
                    'forest': {
                        'cover': 0.7,
                        'movement_cost': 2,
                        'terrain_effect': 'concealment'
                    },
                    'mountain': {
                        'cover': 0.5,
                        'movement_cost': 3,
                        'terrain_effect': 'highground'
                    },
                    'urban': {
                        'cover': 0.9,
                        'movement_cost': 1,
                        'terrain_effect': 'hardcover'
                    },
                    'water': {
                        'cover': 0.0,
                        'movement_cost': 99,
                        'terrain_effect': 'impassable'
                    },
                    'desert': {
                        'cover': 0.1,
                        'movement_cost': 2,
                        'terrain_effect': 'exposure'
                    }
                }
                
                terrain_props = props.get(region_cell.terrain, {
                    'cover': 0.2,
                    'movement_cost': 1,
                    'terrain_effect': ''
                })
                
                tactical_grid.set_combat_props(tq, tr, terrain_props)
    
    return tactical_grid

def tactical_to_region(
    region_grid: HexGrid,
    tactical_grid: TacticalHexGrid,
    center_q: int,
    center_r: int
) -> None:
    """
    Sync tactical grid state back to the region grid.
    
    Args:
        region_grid: The full region HexGrid to update
        tactical_grid: The tactical grid containing changes
        center_q: Center q coordinate where tactical grid was extracted
        center_r: Center r coordinate where tactical grid was extracted
    """
    half = tactical_grid.width // 2
    
    for dq in range(-half, half + 1):
        for dr in range(-half, half + 1):
            tq = dq + half
            tr = dr + half
            tactical_cell = tactical_grid.get(tq, tr)
            
            q = center_q + dq
            r = center_r + dr
            region_cell = region_grid.get(q, r)
            
            if tactical_cell and region_cell:
                # For now, only sync terrain changes
                # TODO: Implement state sync for other properties
                region_cell.terrain = tactical_cell.terrain 

def regionToTactical(region: Region) -> TacticalHexGrid:
    """
    Convert a region map to a tactical hex grid
    """
    # TODO: Implement region to tactical conversion
    tactical_grid = TacticalHexGrid()
    return tactical_grid

def tacticalToRegion(tactical: TacticalHexGrid, region: Region) -> Region:
    """
    Convert a tactical hex grid back to a region map
    """
    # TODO: Implement tactical to region conversion
    return region 