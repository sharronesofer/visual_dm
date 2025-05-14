#!/usr/bin/env python3

"""
Demo script to demonstrate the converted TypeScript to Python code.
This script creates a region map, adds some cells and POIs, and prints information about them.
"""

from HexCell import HexCell, TerrainType, WeatherType
from RegionMap import RegionMap, RegionType, POI

def main():
    print("TypeScript to Python Conversion Demo")
    print("===================================\n")
    
    # Create a HexCell
    print("Creating a HexCell...")
    cell = HexCell(3, 5, 'forest', 'rain', 0.8, 0.6, 0.4)
    print(f"Cell created: {cell}")
    print(f"Coordinates: ({cell.q}, {cell.r})")
    print(f"Terrain: {cell.terrain}")
    print(f"Weather: {cell.weather}")
    print(f"Cost to traverse: {cell.get_cost()}")
    
    # Add a feature
    cell.add_feature("ancient_tree")
    print(f"Added feature: {cell.feature_type}")
    print(f"Has feature: {cell.has_feature}")
    
    # Create another cell for demonstration
    neighbor_cell = HexCell(4, 5)
    print(f"\nCreated neighbor cell: {neighbor_cell}")
    print(f"Are cells adjacent? {cell.is_adjacent(neighbor_cell)}")
    
    # Create a region map
    print("\nCreating a region map...")
    region = RegionMap("Demo Region", RegionType.WILDERNESS, 10, 10)
    
    # Generate random terrain
    print("Generating random terrain...")
    region.generate_random_terrain()
    
    # Add cells to the region
    region.set_cell(cell)
    region.set_cell(neighbor_cell)
    
    # Add a POI
    poi = POI(
        name="Ancient Shrine",
        description="A mysterious shrine hidden in the forest.",
        position={"q": 3, "r": 5},
        poi_type="landmark",
        discovered=False
    )
    region.add_poi(poi)
    
    # Get region information
    print(f"Region name: {region.name}")
    print(f"Region type: {region.type}")
    print(f"Number of cells: {len(region.get_cells())}")
    print(f"Number of POIs: {len(region.get_pois())}")
    
    # Discover POIs
    discovered = region.discover_poi(3, 5, 1)
    print(f"Discovered {discovered} POIs")
    
    # Create a random wilderness region
    print("\nCreating a random wilderness region...")
    wilderness = RegionMap.create_random_wilderness("Wild Lands")
    print(f"Wilderness name: {wilderness.name}")
    print(f"Wilderness type: {wilderness.type}")
    print(f"Number of wilderness cells: {len(wilderness.get_cells())}")
    print(f"Number of wilderness POIs: {len(wilderness.get_pois())}")
    
    # Convert to JSON
    region_data = region.to_json()
    print("\nRegion data:")
    print(f"Name: {region_data.name}")
    print(f"Type: {region_data.type}")
    print(f"Discovered percentage: {region_data.discovered_percentage:.2f}%")
    print(f"Danger level: {region_data.danger_level:.2f}")

if __name__ == "__main__":
    main() 