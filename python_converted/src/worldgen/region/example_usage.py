#!/usr/bin/env python3
"""
Example usage of the region generation system

This script demonstrates how to use the region generation system to:
1. Create procedural regions
2. Create handcrafted regions
3. Use the factory to manage generators
4. Create regions with deterministic seeds
"""
import sys
import os
import json
import random
import time
import logging

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from python_converted.src.worldgen.core.IWorldGenerator import (
    RegionGeneratorOptions, GeneratorType
)
from python_converted.src.worldgen.core.seed_manager import SeedManager
from python_converted.src.worldgen.region.ProceduralRegionGenerator import ProceduralRegionGenerator
from python_converted.src.worldgen.region.HandcraftedRegionGenerator import (
    HandcraftedRegionGenerator, HandcraftedRegionGeneratorOptions
)
from python_converted.src.worldgen.region.RegionGeneratorFactory import RegionGeneratorFactory

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def print_region_summary(region, heading=None):
    """Print a summary of a region to the console"""
    if heading:
        print(f"=== {heading} ===")
    
    print(f"Region: {region.name} (ID: {region.id})")
    print(f"Dimensions: {region.width}x{region.height}")
    
    # Count terrain types
    terrain_counts = {}
    biome_counts = {}
    
    for cell in region.cells:
        terrain_counts[cell.terrain_type] = terrain_counts.get(cell.terrain_type, 0) + 1
        biome_counts[cell.biome] = biome_counts.get(cell.biome, 0) + 1
    
    print("Terrain Types:")
    for terrain, count in terrain_counts.items():
        print(f"  - {terrain}: {count} cells")
    
    print("Biomes:")
    for biome, count in biome_counts.items():
        print(f"  - {biome}: {count} cells")
    
    print(f"Points of Interest: {len(region.points_of_interest)}")
    for poi in region.points_of_interest[:3]:  # Show first 3
        print(f"  - {poi.name} ({poi.poi_type}) at ({poi.x}, {poi.y})")
    if len(region.points_of_interest) > 3:
        print(f"  - ... and {len(region.points_of_interest) - 3} more")
    
    print(f"Resources: {len(region.resources)}")
    for res in region.resources[:3]:  # Show first 3
        print(f"  - {res.resource_type} (quality: {res.quality}) at ({res.x}, {res.y})")
    if len(region.resources) > 3:
        print(f"  - ... and {len(region.resources) - 3} more")
    
    print(f"Metadata: {json.dumps(region.metadata, indent=2)}")
    print()

def example_procedural_generation():
    """Example of generating a region using the procedural generator"""
    print("\n=== Procedural Generation Example ===\n")
    
    # Create a seed manager
    seed_manager = SeedManager(master_seed=12345)
    
    # Create the generator
    generator = ProceduralRegionGenerator()
    generator.seed_manager = seed_manager
    
    # Set some terrain parameters
    generator.set_terrain_parameters({
        "water_level": 0.35,
        "height_multiplier": 1.2
    })
    
    # Create generation options
    options = RegionGeneratorOptions(
        width=32,
        height=32,
        seed=seed_manager.derive_seed("procedural_example"),
        region_type="plains",
        terrain_complexity=0.7,
        resource_abundance=0.8,
        poi_density=0.6,
        is_coastal=True
    )
    
    # Generate the region
    print("Generating procedural region...")
    start_time = time.time()
    result = generator.generate(options)
    generation_time = time.time() - start_time
    
    # Check for success
    if result.success:
        print(f"Generation successful! (Took {generation_time:.3f} seconds)")
        print_region_summary(result.region)
    else:
        print(f"Generation failed: {result.error}")

def example_handcrafted_generation():
    """Example of generating a region using the handcrafted generator"""
    print("\n=== Handcrafted Generation Example ===\n")
    
    # Create a seed manager
    seed_manager = SeedManager(master_seed=54321)
    
    # Create the generator
    generator = HandcraftedRegionGenerator()
    generator.seed_manager = seed_manager
    
    # Create handcrafted options
    options = HandcraftedRegionGeneratorOptions(
        template_id="sample_template",  # This should be created automatically
        width=24,
        height=24,
        seed=seed_manager.derive_seed("handcrafted_example"),
        variation_amount=0.3,  # Add some variation to the template
        randomize_resources=True,
        randomize_pois=False
    )
    
    # Generate the region
    print("Generating handcrafted region...")
    start_time = time.time()
    result = generator.generate(options)
    generation_time = time.time() - start_time
    
    # Check for success
    if result.success:
        print(f"Generation successful! (Took {generation_time:.3f} seconds)")
        print_region_summary(result.region)
    else:
        print(f"Generation failed: {result.error}")

def example_factory_usage():
    """Example of using the factory to create regions"""
    print("\n=== Factory Usage Example ===\n")
    
    # Get the default factory instance
    factory = RegionGeneratorFactory.get_default_instance()
    
    # List available generators
    print("Available generators:")
    for name in factory.get_generator_names():
        generator = factory.get_generator(name)
        print(f"  - {name} (Type: {generator.get_type().value})")
    
    # Create a procedural region
    print("\nCreating procedural region using factory...")
    procedural_options = RegionGeneratorOptions(
        width=24,
        height=24,
        seed=random.randint(1, 100000),
        region_type="forest",
        terrain_complexity=0.5,
        resource_abundance=0.7,
        poi_density=0.3,
        is_forested=True
    )
    
    procedural_result = factory.create_procedural_region(procedural_options)
    print_region_summary(procedural_result.region, "Factory-created Procedural Region")
    
    # Create a handcrafted region
    print("Creating handcrafted region using factory...")
    handcrafted_options = HandcraftedRegionGeneratorOptions(
        template_id="sample_template",
        width=20,
        height=20,
        seed=random.randint(1, 100000),
        variation_amount=0.5
    )
    
    handcrafted_result = factory.create_handcrafted_region(handcrafted_options)
    print_region_summary(handcrafted_result.region, "Factory-created Handcrafted Region")

def example_deterministic_generation():
    """Example of deterministic generation with the same seed"""
    print("\n=== Deterministic Generation Example ===\n")
    
    # Create a specific seed
    demo_seed = 987654321
    
    # Create two generators
    generator1 = ProceduralRegionGenerator()
    generator2 = ProceduralRegionGenerator()
    
    # Create identical options with the same seed
    options1 = RegionGeneratorOptions(
        width=16,
        height=16,
        seed=demo_seed,
        region_type="desert",
        is_arid=True
    )
    
    options2 = RegionGeneratorOptions(
        width=16,
        height=16,
        seed=demo_seed,
        region_type="desert",
        is_arid=True
    )
    
    # Generate regions
    print("Generating first region...")
    result1 = generator1.generate(options1)
    
    print("Generating second region with identical options and seed...")
    result2 = generator2.generate(options2)
    
    # Compare the regions
    region1 = result1.region
    region2 = result2.region
    
    print(f"Region 1 ID: {region1.id}")
    print(f"Region 2 ID: {region2.id}")
    
    # Check if terrain is identical
    identical = True
    for i in range(len(region1.cells)):
        cell1 = region1.cells[i]
        cell2 = region2.cells[i]
        if cell1.terrain_type != cell2.terrain_type or cell1.biome != cell2.biome:
            identical = False
            break
    
    print(f"Regions have identical terrain: {identical}")
    
    # Now generate a region with a different seed
    options3 = RegionGeneratorOptions(
        width=16,
        height=16,
        seed=demo_seed + 1,  # Different seed
        region_type="desert",
        is_arid=True
    )
    
    print("Generating third region with different seed...")
    result3 = generator1.generate(options3)
    region3 = result3.region
    
    # Compare with first region
    identical = True
    different_count = 0
    for i in range(len(region1.cells)):
        cell1 = region1.cells[i]
        cell3 = region3.cells[i]
        if cell1.terrain_type != cell3.terrain_type or cell1.biome != cell3.biome:
            identical = False
            different_count += 1
    
    print(f"Regions with different seeds are identical: {identical}")
    print(f"Number of cells with differences: {different_count} out of {len(region1.cells)}")

if __name__ == "__main__":
    # Run the examples
    example_procedural_generation()
    example_handcrafted_generation()
    example_factory_usage()
    example_deterministic_generation() 