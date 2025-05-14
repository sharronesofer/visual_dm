"""
Combat-related calculations for tactical hex grids.
"""

from typing import List, Optional, Tuple, Dict
from math import sqrt
from .tactical_hex_grid import TacticalHexGrid, HexCell

def lineOfSight(grid: TacticalHexGrid, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
    """
    Calculate if there is a clear line of sight between two points on the grid
    """
    x1, y1 = start
    x2, y2 = end
    
    # Get cells along the line
    line_cells = get_line(grid, x1, y1, x2, y2)
    
    # Check if any cell blocks vision
    for cell in line_cells:
        if cell and cell.elevation > max(
            grid.get_cell(x1, y1).elevation,
            grid.get_cell(x2, y2).elevation
        ):
            return False
    
    return True

def get_line(grid: TacticalHexGrid, x1: int, y1: int, x2: int, y2: int) -> List[Optional[HexCell]]:
    """
    Get all cells along a line between two points using Bresenham's line algorithm adapted for hexagonal grids
    """
    cells = []
    dx = x2 - x1
    dy = y2 - y1
    
    # Handle vertical lines
    if dx == 0:
        step = 1 if dy > 0 else -1
        for y in range(y1, y2 + step, step):
            cells.append(grid.get_cell(x1, y))
        return cells
    
    # Calculate slope and intercept
    slope = dy / dx
    intercept = y1 - slope * x1
    
    # Determine x step direction
    step = 1 if dx > 0 else -1
    
    # Walk along x-axis
    for x in range(x1, x2 + step, step):
        # Calculate corresponding y value
        y = round(slope * x + intercept)
        if grid.is_valid_position(x, y):
            cells.append(grid.get_cell(x, y))
    
    return cells

def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """
    Calculate the Euclidean distance between two points
    """
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def get_range_cells(grid: TacticalHexGrid, center: Tuple[int, int], range_: int) -> List[HexCell]:
    """
    Get all cells within a certain range of a center point
    """
    x, y = center
    cells = []
    
    for dx in range(-range_, range_ + 1):
        for dy in range(-range_, range_ + 1):
            if calculate_distance(0, 0, dx, dy) <= range_:
                new_x, new_y = x + dx, y + dy
                if grid.is_valid_position(new_x, new_y):
                    cell = grid.get_cell(new_x, new_y)
                    if cell:
                        cells.append(cell)
    
    return cells

def find_path(grid: TacticalHexGrid, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Find a path between two points using A* pathfinding
    """
    from heapq import heappush, heappop
    
    def heuristic(pos: Tuple[int, int]) -> float:
        return calculate_distance(pos[0], pos[1], end[0], end[1])
    
    # Priority queue for open nodes
    open_set = []
    heappush(open_set, (0, start))
    
    # Track where we came from
    came_from = {start: None}
    
    # Cost to reach each node
    g_score = {start: 0}
    
    while open_set:
        current = heappop(open_set)[1]
        
        if current == end:
            # Reconstruct path
            path = []
            while current:
                path.append(current)
                current = came_from[current]
            return list(reversed(path))
        
        # Check neighbors
        for neighbor in grid.get_neighbors(*current):
            x, y = neighbor.x, neighbor.y
            neighbor_pos = (x, y)
            
            # Calculate tentative g score
            tentative_g = g_score[current] + 1
            
            if neighbor_pos not in g_score or tentative_g < g_score[neighbor_pos]:
                came_from[neighbor_pos] = current
                g_score[neighbor_pos] = tentative_g
                f_score = tentative_g + heuristic(neighbor_pos)
                heappush(open_set, (f_score, neighbor_pos))
    
    return []  # No path found

def range_between(
    grid: TacticalHexGrid,
    from_q: int,
    from_r: int,
    to_q: int,
    to_r: int
) -> int:
    """
    Calculate the hex distance between two points.
    
    Args:
        grid: The tactical grid
        from_q: Starting q coordinate
        from_r: Starting r coordinate
        to_q: Target q coordinate
        to_r: Target r coordinate
        
    Returns:
        The distance in hex cells
    """
    return (abs(from_q - to_q) + abs(from_q + from_r - to_q - to_r) + abs(from_r - to_r)) // 2

def tactical_pathfind(
    grid: TacticalHexGrid,
    from_q: int,
    from_r: int,
    to_q: int,
    to_r: int,
    max_ap: int
) -> Optional[Tuple[List[Tuple[int, int]], int]]:
    """
    Find the optimal path between two points using A* pathfinding.
    Takes into account movement costs and action points.
    
    Args:
        grid: The tactical grid
        from_q: Starting q coordinate
        from_r: Starting r coordinate
        to_q: Target q coordinate
        to_r: Target r coordinate
        max_ap: Maximum action points available for movement
        
    Returns:
        Tuple of (path as list of coordinates, total cost) or None if no path found
    """
    # A* pathfinding implementation
    open_list: List[Dict] = [{
        'q': from_q,
        'r': from_r,
        'cost': 0,
        'est': range_between(grid, from_q, from_r, to_q, to_r),
        'path': [(from_q, from_r)]
    }]
    closed = set()
    
    while open_list:
        # Sort by f = g + h (cost + estimate)
        open_list.sort(key=lambda x: x['cost'] + x['est'])
        current = open_list.pop(0)
        
        if current['q'] == to_q and current['r'] == to_r:
            return current['path'], current['cost']
            
        pos_key = f"{current['q']},{current['r']}"
        closed.add(pos_key)
        
        # Check all neighbors
        for neighbor in grid.neighbors(current['q'], current['r']):
            key = f"{neighbor.q},{neighbor.r}"
            if key in closed:
                continue
                
            if neighbor.terrain_effect == 'impassable':
                continue
                
            new_cost = current['cost'] + neighbor.movement_cost
            if new_cost > max_ap:
                continue
                
            # Add to open list
            open_list.append({
                'q': neighbor.q,
                'r': neighbor.r,
                'cost': new_cost,
                'est': range_between(grid, neighbor.q, neighbor.r, to_q, to_r),
                'path': current['path'] + [(neighbor.q, neighbor.r)]
            })
    
    return None

def area_of_effect(
    grid: TacticalHexGrid,
    center_q: int,
    center_r: int,
    radius: int
) -> List[Tuple[int, int]]:
    """
    Get all cells within a certain radius of a center point.
    
    Args:
        grid: The tactical grid
        center_q: Center q coordinate
        center_r: Center r coordinate
        radius: Radius in hex cells
        
    Returns:
        List of (q, r) coordinates within the area
    """
    affected = []
    for dq in range(-radius, radius + 1):
        for dr in range(-radius, radius + 1):
            # Calculate hex distance
            dist = abs(dq) + abs(dr) + abs(dq + dr)
            if dist // 2 <= radius:
                q = center_q + dq
                r = center_r + dr
                if grid.get(q, r):
                    affected.append((q, r))
    return affected

def range_between(grid: TacticalHexGrid, start: Tuple[int, int], end: Tuple[int, int]) -> int:
    """
    Calculate the range (in grid cells) between two points
    """
    x1, y1 = start
    x2, y2 = end
    return grid.get_distance(x1, y1, x2, y2) 