#!/usr/bin/env python3
"""
Demo script to visualize biome transitions with matplotlib
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.patches as mpatches

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from python_converted.src.worldgen.environment.BiomeTypes import BiomeType, BIOME_PARAMETERS
from python_converted.src.worldgen.environment.BiomeAdjacencyMatrix import BiomeAdjacencyMatrix
from python_converted.src.worldgen.environment.BiomeTransitionGenerator import BiomeCell, BiomeGrid, BiomeTransitionGenerator
from python_converted.src.worldgen.environment.BiomeConfigManager import BiomeConfigManager
from python_converted.src.worldgen.core.DeterministicRNG import DeterministicRNG


def create_sample_grid(width: int, height: int, pattern: str = "horizontal") -> BiomeGrid:
    """
    Create a sample biome grid with a specific pattern
    
    Args:
        width: Grid width
        height: Grid height
        pattern: Pattern type ('horizontal', 'vertical', 'quadrants', 'random')
        
    Returns:
        BiomeGrid with the specified pattern
    """
    grid = BiomeGrid(width, height)
    
    if pattern == "horizontal":
        # Desert on the left, tundra on the right
        for y in range(height):
            for x in range(width):
                if x < width // 2:
                    biome = BiomeType.DESERT
                    temp = 35.0
                    moisture = 0.1
                else:
                    biome = BiomeType.TUNDRA
                    temp = -5.0
                    moisture = 0.3
                
                grid.cells[y][x] = BiomeCell(
                    x=x, y=y, 
                    biome=biome,
                    elevation=200.0,
                    moisture=moisture,
                    temperature=temp
                )
    
    elif pattern == "vertical":
        # Rainforest on top, desert on bottom
        for y in range(height):
            for x in range(width):
                if y < height // 2:
                    biome = BiomeType.TROPICAL_RAINFOREST
                    temp = 28.0
                    moisture = 0.9
                else:
                    biome = BiomeType.DESERT
                    temp = 35.0
                    moisture = 0.1
                
                grid.cells[y][x] = BiomeCell(
                    x=x, y=y, 
                    biome=biome,
                    elevation=200.0,
                    moisture=moisture,
                    temperature=temp
                )
    
    elif pattern == "quadrants":
        # Four different biomes in quadrants
        biomes = [
            BiomeType.DESERT,  # Top-left
            BiomeType.TUNDRA,  # Top-right
            BiomeType.TROPICAL_RAINFOREST,  # Bottom-left
            BiomeType.TEMPERATE_FOREST  # Bottom-right
        ]
        
        temperatures = [35.0, -5.0, 28.0, 15.0]
        moistures = [0.1, 0.3, 0.9, 0.7]
        
        for y in range(height):
            for x in range(width):
                quadrant = (1 if x >= width // 2 else 0) + (2 if y >= height // 2 else 0)
                
                grid.cells[y][x] = BiomeCell(
                    x=x, y=y, 
                    biome=biomes[quadrant],
                    elevation=200.0,
                    moisture=moistures[quadrant],
                    temperature=temperatures[quadrant]
                )
    
    elif pattern == "random":
        # Random biomes (but chunked for realism)
        rng = DeterministicRNG(seed=12345)
        all_biomes = list(BiomeType)
        # Exclude transition biomes for initial grid
        all_biomes = [b for b in all_biomes if not BIOME_PARAMETERS[b].is_transition_biome]
        
        # Create random chunks
        chunk_size = 5
        num_chunks_x = width // chunk_size + 1
        num_chunks_y = height // chunk_size + 1
        chunk_biomes = []
        
        for _ in range(num_chunks_y):
            row = []
            for _ in range(num_chunks_x):
                # Choose a random biome for this chunk
                biome_idx = rng.randint(0, len(all_biomes) - 1)
                row.append(all_biomes[biome_idx])
            chunk_biomes.append(row)
        
        # Fill grid based on chunks
        for y in range(height):
            for x in range(width):
                chunk_y = y // chunk_size
                chunk_x = x // chunk_size
                
                if chunk_y >= len(chunk_biomes) or chunk_x >= len(chunk_biomes[0]):
                    biome = BiomeType.PLAINS  # Default
                else:
                    biome = chunk_biomes[chunk_y][chunk_x]
                
                # Set environment values based on biome
                params = BIOME_PARAMETERS[biome]
                temp = (params.temperature_range[0] + params.temperature_range[1]) / 2
                moisture = (params.moisture_range[0] + params.moisture_range[1]) / 2
                
                grid.cells[y][x] = BiomeCell(
                    x=x, y=y, 
                    biome=biome,
                    elevation=200.0,
                    moisture=moisture,
                    temperature=temp
                )
    
    return grid


def get_biome_colors() -> dict:
    """Get a mapping of biome types to colors"""
    colors = {}
    for biome in BiomeType:
        params = BIOME_PARAMETERS[biome]
        colors[biome] = params.base_color
    return colors


def visualize_grid(grid: BiomeGrid, title: str, show_transitions: bool = False):
    """
    Visualize a biome grid using matplotlib
    
    Args:
        grid: The biome grid to visualize
        title: Title for the plot
        show_transitions: Whether to highlight transition cells
    """
    # Create a 2D array of biome indices
    biome_grid = np.zeros((grid.height, grid.width), dtype=int)
    transition_mask = np.zeros((grid.height, grid.width), dtype=bool)
    
    # Map each biome to a unique index
    biome_to_index = {biome: i for i, biome in enumerate(BiomeType)}
    
    # Fill the grid with biome indices
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.cells[y][x]
            biome_grid[y, x] = biome_to_index[cell.biome]
            transition_mask[y, x] = cell.is_transition
    
    # Create a colormap from biome colors
    biome_colors = get_biome_colors()
    colors = [biome_colors[biome] for biome in BiomeType]
    cmap = ListedColormap(colors)
    
    # Create a normalization based on biome indices
    bounds = np.arange(len(BiomeType) + 1)
    norm = BoundaryNorm(bounds, cmap.N)
    
    # Create plot
    plt.figure(figsize=(10, 8))
    
    # Plot biomes
    plt.imshow(biome_grid, cmap=cmap, norm=norm, interpolation='nearest')
    
    # Highlight transition cells if requested
    if show_transitions:
        # Create a semi-transparent mask
        plt.imshow(
            np.where(transition_mask, 1, np.nan),
            cmap=ListedColormap(['none', 'white']),
            alpha=0.3
        )
    
    # Create legend
    patches = []
    for biome in BiomeType:
        # Only include biomes that are actually in the grid
        if biome_to_index[biome] in biome_grid:
            patch = mpatches.Patch(color=biome_colors[biome], label=biome.value)
            patches.append(patch)
    
    if show_transitions:
        # Add transition indicator to legend
        patch = mpatches.Patch(facecolor='white', alpha=0.3, edgecolor='black', label='Transition')
        patches.append(patch)
    
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.title(title)
    plt.tight_layout()


def main():
    """Main demo function"""
    # Create a sample grid
    grid_size = 50
    original_grid = create_sample_grid(grid_size, grid_size, pattern="quadrants")
    
    # Create transition generator with default rules
    matrix = BiomeAdjacencyMatrix()
    rng = DeterministicRNG(seed=42)
    generator = BiomeTransitionGenerator(matrix, rng)
    
    # Generate transitions
    result_grid = generator.generate_transitions(original_grid)
    
    # Visualize results
    plt.figure(figsize=(15, 6))
    
    plt.subplot(1, 2, 1)
    visualize_grid(original_grid, "Original Biome Grid")
    
    plt.subplot(1, 2, 2)
    visualize_grid(result_grid, "With Transition Zones", show_transitions=True)
    
    plt.tight_layout()
    plt.show()
    
    print("Demo completed. Transition zones have been visualized.")


if __name__ == "__main__":
    main() 