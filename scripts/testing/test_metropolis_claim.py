"""
Test script for the improved metropolis region claim function.
This script creates a simple mock region with a grid of tiles and tests the claim_region_hexes_for_city function.
"""

import random
from typing import Dict, Any, List, Tuple

def mock_region_data(size: int = 15) -> Dict[str, Any]:
    """Create a mock region data structure with a grid of tiles."""
    region_data = {
        "tiles": {}
    }
    
    # Create a grid of tiles
    for x in range(size):
        for y in range(size):
            coord_key = f"{x}_{y}"
            region_data["tiles"][coord_key] = {
                "x": x,
                "y": y,
                "terrain": random.choice(["plains", "forest", "hills", "mountains"]),
                "elevation": random.randint(1, 10)
            }
    
    return region_data

def claim_region_hexes_for_city(region_data: Dict[str, Any], 
                              city_tile: Tuple[int, int], 
                              is_metropolis: bool = False) -> List[str]:
    """
    Mark region hexes as claimed by a city/metropolis. For metropolises, claim 2-3 adjacent hexes if available.
    
    Args:
        region_data: Region data dictionary with tiles
        city_tile: Tuple of (x, y) for the city
        is_metropolis: Whether this is a metropolis (claims more hexes)
        
    Returns:
        List of claimed hex coordinates as strings
    """
    x, y = city_tile
    coord_key = f"{x}_{y}"
    claimed_hexes = [coord_key]
    region_data["tiles"][coord_key]["claimed_by_city"] = coord_key
    
    if is_metropolis:
        # Per Development Bible: Metropolises MUST claim 2-3 adjacent region hexes
        required_claims = random.randint(2, 3)  # Always claim 2-3 additional hexes
        
        # Directions for hex grid, ordered for better contiguity
        # We'll try adjacent hexes first, then try to ensure they're connected
        directions = [
            (-1, 0),  # West
            (1, 0),   # East
            (0, -1),  # South
            (0, 1),   # North
            (-1, 1),  # Northwest
            (1, -1),  # Southeast
        ]
        
        # Prioritize directions by grouping adjacent ones together
        # This improves contiguity by ensuring claimed hexes form a better visual pattern
        # Rather than just random shuffling, we'll create "clusters" of directions
        if random.random() < 0.5:
            # Favor east-west axis for metropolis sprawl
            direction_groups = [
                [(-1, 0), (-1, 1)],  # West + Northwest
                [(1, 0), (1, -1)],   # East + Southeast
                [(0, 1), (0, -1)]    # North + South
            ]
        else:
            # Favor north-south axis for metropolis sprawl
            direction_groups = [
                [(0, 1), (-1, 1)],   # North + Northwest
                [(0, -1), (1, -1)],  # South + Southeast
                [(-1, 0), (1, 0)]    # West + East
            ]
        
        # Shuffle the groups to add some randomness, but keep directions in groups together
        random.shuffle(direction_groups)
        directions = [dir for group in direction_groups for dir in group]
        
        # Create a set of all potential hex coordinates for efficiency
        all_potential_hexes = set()
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            nkey = f"{nx}_{ny}"
            if nkey in region_data["tiles"] and "claimed_by_city" not in region_data["tiles"][nkey]:
                all_potential_hexes.add(nkey)
        
        # Extended search for larger spread if needed
        for dx in [-2, 2]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                nkey = f"{nx}_{ny}"
                if nkey in region_data["tiles"] and "claimed_by_city" not in region_data["tiles"][nkey]:
                    all_potential_hexes.add(nkey)
        
        for dy in [-2, 2]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                nkey = f"{nx}_{ny}"
                if nkey in region_data["tiles"] and "claimed_by_city" not in region_data["tiles"][nkey]:
                    all_potential_hexes.add(nkey)
        
        # Ensure we have enough potential hexes
        if len(all_potential_hexes) < required_claims:
            print(f"WARNING: Not enough potential hexes around {coord_key}. Need {required_claims}, found {len(all_potential_hexes)}")
            # Add more hex candidates in a larger radius
            for radius in range(3, 6):
                for dx in range(-radius, radius + 1):
                    for dy in range(-radius, radius + 1):
                        if abs(dx) + abs(dy) <= radius + 1:  # Roughly circular search
                            nx, ny = x + dx, y + dy
                            nkey = f"{nx}_{ny}"
                            if nkey in region_data["tiles"] and "claimed_by_city" not in region_data["tiles"][nkey]:
                                all_potential_hexes.add(nkey)
                if len(all_potential_hexes) >= required_claims:
                    break
        
        # First pass: Try to claim adjacent hexes with preference for contiguity
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            nkey = f"{nx}_{ny}"
            if nkey in region_data["tiles"] and "claimed_by_city" not in region_data["tiles"][nkey]:
                region_data["tiles"][nkey]["claimed_by_city"] = coord_key
                claimed_hexes.append(nkey)
                if len(claimed_hexes) - 1 >= required_claims:  # -1 because we started with 1 claim
                    break
        
        # Second pass: If we couldn't get enough adjacent hexes, ensure we find some that are adjacent to our existing claims
        if len(claimed_hexes) - 1 < required_claims:
            # Create a priority queue of candidate hexes - we'll prioritize hexes that are adjacent to multiple claimed hexes
            candidates = []
            for claimed_hex in claimed_hexes:
                cx, cy = map(int, claimed_hex.split('_'))
                for dx, dy in directions:
                    nx, ny = cx + dx, cy + dy
                    nkey = f"{nx}_{ny}"
                    if (nkey in region_data["tiles"] and 
                        "claimed_by_city" not in region_data["tiles"][nkey] and 
                        nkey not in claimed_hexes):
                        
                        # Calculate how many claimed hexes this candidate is adjacent to
                        adjacent_to_claimed = 0
                        for cdx, cdy in directions:
                            adj_x, adj_y = nx + cdx, ny + cdy
                            adj_key = f"{adj_x}_{adj_y}"
                            if adj_key in claimed_hexes:
                                adjacent_to_claimed += 1
                        
                        # Add to candidates list with priority based on adjacency
                        candidates.append((adjacent_to_claimed, nkey))
            
            # Sort candidates by adjacency count (higher is better for contiguity)
            candidates.sort(reverse=True)
            
            # Claim the best candidates first
            for _, nkey in candidates:
                if nkey not in claimed_hexes:
                    region_data["tiles"][nkey]["claimed_by_city"] = coord_key
                    claimed_hexes.append(nkey)
                    if len(claimed_hexes) - 1 >= required_claims:
                        break
        
        # If we still don't have enough, try a third pass with expanded search radius
        if len(claimed_hexes) - 1 < required_claims:
            # Expanded search: look for hexes that are two steps away but adjacent to claimed hexes
            expanded_directions = [
                (-2, 0), (2, 0),    # 2 West, 2 East
                (0, -2), (0, 2),    # 2 South, 2 North
                (-1, 2), (1, -2),   # Expanded NW, SE
                (-2, 1), (2, -1),   # Expanded NW, SE
                (-2, 2), (2, -2),   # Diagonal 2 steps
                (1, 1), (-1, -1)    # Additional diagonals
            ]
            
            for claimed_hex in claimed_hexes:
                if len(claimed_hexes) - 1 >= required_claims:
                    break
                    
                cx, cy = map(int, claimed_hex.split('_'))
                for dx, dy in expanded_directions:
                    if len(claimed_hexes) - 1 >= required_claims:
                        break
                        
                    nx, ny = cx + dx, cy + dy
                    nkey = f"{nx}_{ny}"
                    if nkey in region_data["tiles"] and "claimed_by_city" not in region_data["tiles"][nkey] and nkey not in claimed_hexes:
                        # Check if it's adjacent to any claimed hex for contiguity
                        is_adjacent = False
                        for other_hex in claimed_hexes:
                            ox, oy = map(int, other_hex.split('_'))
                            if (abs(nx - ox) <= 1 and abs(ny - oy) <= 1):
                                is_adjacent = True
                                break
                        
                        if is_adjacent:
                            region_data["tiles"][nkey]["claimed_by_city"] = coord_key
                            claimed_hexes.append(nkey)
        
        # If we still don't have enough, this is truly an edge case - force claim any valid adjacent hexes
        if len(claimed_hexes) - 1 < required_claims:
            all_coords = list(all_potential_hexes)
            random.shuffle(all_coords)
            
            for coord in all_coords:
                if coord not in claimed_hexes and "claimed_by_city" not in region_data["tiles"][coord]:
                    # Only claim if adjacent to an existing claimed hex
                    cx, cy = map(int, coord.split('_'))
                    is_adjacent = False
                    for claimed_hex in claimed_hexes:
                        hx, hy = map(int, claimed_hex.split('_'))
                        # Check if this coord is adjacent to a claimed hex
                        if ((abs(cx - hx) <= 1 and abs(cy - hy) <= 1) or 
                            (cx == hx and abs(cy - hy) == 1)):
                            is_adjacent = True
                            break
                    
                    if is_adjacent:
                        region_data["tiles"][coord]["claimed_by_city"] = coord_key
                        claimed_hexes.append(coord)
                        if len(claimed_hexes) - 1 >= required_claims:
                            break
        
        # Last resort: if we still don't have enough hexes, claim ANY available hexes
        if len(claimed_hexes) - 1 < required_claims:
            all_keys = list(region_data["tiles"].keys())
            random.shuffle(all_keys)
            for key in all_keys:
                if key not in claimed_hexes and "claimed_by_city" not in region_data["tiles"][key]:
                    region_data["tiles"][key]["claimed_by_city"] = coord_key
                    claimed_hexes.append(key)
                    if len(claimed_hexes) - 1 >= required_claims:
                        break
            
        # Log warning only if we still couldn't get enough
        if len(claimed_hexes) - 1 < required_claims:
            print(f"WARNING: Metropolis at {coord_key} could only claim {len(claimed_hexes)} hexes, needed {1+required_claims}")
                    
    # Store claimed hexes in the city/metropolis POI data
    region_data["tiles"][coord_key]["region_hexes"] = claimed_hexes
    region_data["tiles"][coord_key]["is_sprawling"] = is_metropolis
    region_data["tiles"][coord_key]["claimed_hex_count"] = len(claimed_hexes)
    
    # Log the hex claims for debugging/analytics
    print(f"City/Metropolis at {coord_key} claimed {len(claimed_hexes)} hexes: {claimed_hexes}")
    
    return claimed_hexes

def visualize_claims(region_data: Dict[str, Any], size: int) -> None:
    """Visualize the claimed hexes in ASCII."""
    print("\nMetropolis Claim Visualization:")
    print("-" * (size * 3 + 2))
    
    for y in range(size):
        line = "| "
        for x in range(size):
            coord_key = f"{x}_{y}"
            if coord_key in region_data["tiles"]:
                if "claimed_by_city" in region_data["tiles"][coord_key]:
                    line += "M "
                else:
                    line += ". "
            else:
                line += "  "
        line += "|"
        print(line)
    
    print("-" * (size * 3 + 2))

def test_metropolis_claim() -> None:
    """Test the metropolis region claim function."""
    # Create a mock region
    size = 15
    region_data = mock_region_data(size)
    
    # Test multiple metropolises to ensure consistency
    num_tests = 10
    success_count = 0
    total_claimed = 0
    
    for i in range(num_tests):
        # Place a metropolis in the center area of the map
        x = random.randint(size // 4, size - (size // 4) - 1)
        y = random.randint(size // 4, size - (size // 4) - 1)
        city_tile = (x, y)
        
        # Get the required number of claims for this metropolis
        required_claims = random.randint(2, 3)
        print(f"\nTest {i+1}: Metropolis at {city_tile} requires {required_claims} additional claims")
        
        # Test claim function
        claimed_hexes = claim_region_hexes_for_city(region_data, city_tile, is_metropolis=True)
        
        # Check results
        if len(claimed_hexes) - 1 >= required_claims:
            success_count += 1
            print(f"SUCCESS: Claimed {len(claimed_hexes) - 1} additional hexes, needed {required_claims}")
        else:
            print(f"FAILURE: Only claimed {len(claimed_hexes) - 1} additional hexes, needed {required_claims}")
        
        total_claimed += len(claimed_hexes) - 1
        
        # Visualize the result
        visualize_claims(region_data, size)
        
        # Reset for next test
        for coord_key in claimed_hexes:
            if "claimed_by_city" in region_data["tiles"][coord_key]:
                del region_data["tiles"][coord_key]["claimed_by_city"]
            if "region_hexes" in region_data["tiles"][coord_key]:
                del region_data["tiles"][coord_key]["region_hexes"]
            if "is_sprawling" in region_data["tiles"][coord_key]:
                del region_data["tiles"][coord_key]["is_sprawling"]
            if "claimed_hex_count" in region_data["tiles"][coord_key]:
                del region_data["tiles"][coord_key]["claimed_hex_count"]
    
    # Report overall results
    print(f"\nOverall Results:")
    print(f"Success Rate: {success_count}/{num_tests} = {success_count/num_tests*100:.1f}%")
    print(f"Average Additional Claims: {total_claimed/num_tests:.1f}")

if __name__ == "__main__":
    print("Testing improved metropolis region claim function...")
    test_metropolis_claim() 