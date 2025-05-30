#!/usr/bin/env python3
"""
World Generation API Example

This example demonstrates how to use the Visual DM world generation API
to create, save, load, and customize procedurally generated worlds.
"""

import os
import asyncio
import time
import json
from pprint import pprint

# Import world generation API
from backend.systems.world_generation.api import (
    generate_world,
    generate_custom_world,
    generate_world_async,
    generate_custom_world_async,
    save_world,
    load_world,
    get_world_info,
    subscribe_to_world_events,
    DEFAULT_SIZES
)

# Import event types
from backend.systems.world_generation.events import WorldGenerationEventType

# Output directory for generated worlds
OUTPUT_DIR = "generated_worlds"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def example_1_basic_generation():
    """Example 1: Basic world generation with default settings."""
    print("\n--- Example 1: Basic World Generation ---")
    
    # Generate a world with default settings
    print("Generating world with default settings...")
    start_time = time.time()
    world = generate_world(seed=12345)
    elapsed_time = time.time() - start_time
    
    # Get world info
    info = get_world_info(world)
    print(f"World '{info['name']}' generated in {elapsed_time:.2f} seconds")
    print(f"Regions: {info['regions']}")
    print(f"Total tiles: {info['total_tiles']}")
    print(f"Land percentage: {info['land_percentage']:.1f}%")
    
    # Save the world
    output_path = os.path.join(OUTPUT_DIR, "default_world.json")
    save_world(world, output_path)
    print(f"World saved to {output_path}")
    
    return world

def example_2_custom_generation():
    """Example a custom world with specific settings."""
    print("\n--- Example 2: Custom World Generation ---")
    
    # Custom generation settings
    elevation_settings = {
        "mountain_density": 0.5,  # More mountains
        "hill_density": 0.6,
        "smoothing_iterations": 4,  # More smoothing
        "ocean_percentage": 0.4  # Less ocean
    }
    
    river_settings = {
        "num_rivers": 5,  # More rivers
        "max_river_length": 100,  # Longer rivers
        "tributary_chance": 0.4,  # More tributaries
        "meander_factor": 0.5  # More meandering
    }
    
    # Generate a custom world
    print("Generating custom world...")
    start_time = time.time()
    world = generate_custom_world(
        seed=67890,
        size="large",  # Larger world
        name="Custom Mountainous World",
        elevation_settings=elevation_settings,
        river_settings=river_settings
    )
    elapsed_time = time.time() - start_time
    
    # Get world info
    info = get_world_info(world)
    print(f"World '{info['name']}' generated in {elapsed_time:.2f} seconds")
    print(f"Regions: {info['regions']}")
    print(f"Total tiles: {info['total_tiles']}")
    print(f"Land percentage: {info['land_percentage']:.1f}%")
    
    # Print biome distribution
    print("\nBiome distribution:")
    biome_counts = info['biome_counts']
    total_tiles = info['total_tiles']
    for biome, count in sorted(biome_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_tiles) * 100
        print(f"  {biome}: {count} tiles ({percentage:.1f}%)")
    
    # Save the world
    output_path = os.path.join(OUTPUT_DIR, "custom_mountainous_world.json")
    save_world(world, output_path)
    print(f"World saved to {output_path}")
    
    return world

async def example_3_async_generation():
    """Example 3: Asynchronous world generation."""
    print("\n--- Example 3: Asynchronous World Generation ---")
    
    # Event handler for progress updates
    def on_progress(event):
        print(f"Generation progress: {event.progress * 100:.1f}% - Phase: {event.current_phase}")
    
    # Event handler for completion
    def on_completion(event):
        print(f"Generation completed in {event.elapsed_time:.2f} seconds")
    
    # Subscribe to events
    subscribe_to_world_events(WorldGenerationEventType.GENERATION_PROGRESS, on_progress)
    subscribe_to_world_events(WorldGenerationEventType.GENERATION_COMPLETED, on_completion)
    
    # Generate a world asynchronously
    print("Generating world asynchronously...")
    start_time = time.time()
    
    world = await generate_world_async(
        seed=54321,
        size="medium",
        name="Async Generated World"
    )
    
    elapsed_time = time.time() - start_time
    
    # Get world info
    info = get_world_info(world)
    print(f"World '{info['name']}' async generation completed in {elapsed_time:.2f} seconds")
    
    # Save the world
    output_path = os.path.join(OUTPUT_DIR, "async_world.json")
    save_world(world, output_path)
    print(f"World saved to {output_path}")
    
    return world

def example_4_world_loading():
    """Example 4: Loading and analyzing worlds."""
    print("\n--- Example 4: Loading and Analyzing Worlds ---")
    
    # Load a world
    input_path = os.path.join(OUTPUT_DIR, "default_world.json")
    print(f"Loading world from {input_path}...")
    
    world = load_world(input_path)
    info = get_world_info(world)
    
    print(f"Loaded world '{info['name']}'")
    print(f"Author: {info['author']}")
    print(f"Creation date: {info['creation_date']}")
    print(f"Description: {info['description']}")
    
    # Analyze resource distribution
    if 'resource_counts' in info and info['resource_counts']:
        print("\nResource distribution:")
        for resource, count in sorted(info['resource_counts'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {resource}: {count} occurrences")
    else:
        print("\nNo resources found in this world")
    
    return world

def example_5_multi_region_world():
    """Example 5: Generate a world with multiple regions."""
    print("\n--- Example 5: Multi-Region World Generation ---")
    
    # Generate a world with multiple regions
    print("Generating world with 4 regions...")
    start_time = time.time()
    
    world = generate_custom_world(
        seed=98765,
        size="small",  # Smaller regions, but more of them
        regions=4,  # 4 regions
        name="Multi-Region World",
        region_layout="grid"  # Layout as 2x2 grid
    )
    
    elapsed_time = time.time() - start_time
    
    # Get world info
    info = get_world_info(world)
    print(f"World '{info['name']}' with {info['regions']} regions generated in {elapsed_time:.2f} seconds")
    print(f"Total tiles: {info['total_tiles']}")
    
    # Print region information
    print("\nRegion details:")
    for region_id, region in world.get('regions', {}).items():
        num_tiles = len(region.get('tiles', {}))
        coords = region.get('coordinates', {})
        print(f"  Region {region_id}: {num_tiles} tiles, coordinates: ({coords.get('x', 0)}, {coords.get('y', 0)})")
    
    # Save the world
    output_path = os.path.join(OUTPUT_DIR, "multi_region_world.json")
    save_world(world, output_path)
    print(f"World saved to {output_path}")
    
    return world

def example_6_world_sizes():
    """Example 6: Comparing different world sizes."""
    print("\n--- Example 6: Comparing World Sizes ---")
    
    sizes = ["tiny", "small", "medium", "large", "huge"]
    results = {}
    
    print("Generating worlds of different sizes:")
    for size in sizes:
        print(f"Generating {size} world...")
        tiles = DEFAULT_SIZES[size]
        print(f"  Size: {size} ({tiles}x{tiles} tiles)")
        
        start_time = time.time()
        world = generate_world(
            seed=42,  # Same seed for comparability
            size=size,
            name=f"{size.capitalize()} World"
        )
        elapsed_time = time.time() - start_time
        
        # Get info
        info = get_world_info(world)
        results[size] = {
            "tiles": info['total_tiles'],
            "generation_time": elapsed_time,
            "land_percentage": info['land_percentage']
        }
        
        print(f"  Generation time: {elapsed_time:.2f} seconds")
        print(f"  Land percentage: {info['land_percentage']:.1f}%")
        
        # Save the world
        output_path = os.path.join(OUTPUT_DIR, f"{size}_world.json")
        save_world(world, output_path)
    
    # Print summary
    print("\nSize comparison summary:")
    print(f"{'Size':<8} {'Tiles':<10} {'Time (s)':<10} {'Land %':<10}")
    print(f"{'-' * 40}")
    for size in sizes:
        data = results[size]
        print(f"{size:<8} {data['tiles']:<10} {data['generation_time']:<10.2f} {data['land_percentage']:<10.1f}")

async def run_examples():
    """Run all examples."""
    example_1_basic_generation()
    example_2_custom_generation()
    await example_3_async_generation()
    example_4_world_loading()
    example_5_multi_region_world()
    example_6_world_sizes()

if __name__ == "__main__":
    # Run all examples
    asyncio.run(run_examples()) 