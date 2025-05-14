#!/usr/bin/env python3
"""
BiomeTransitionGenerator.py - Part of the World Generation System

Implements the generation of transition zones between incompatible biomes,
ensuring natural and gradual transitions.
"""

from typing import Dict, List, Set, Tuple, Optional, Union, Any
import math
import random
import numpy as np

from ..core.DeterministicRNG import DeterministicRNG, ISeedConfig
from .BiomeTypes import BiomeType, BiomeParameters, BIOME_PARAMETERS
from .BiomeAdjacencyMatrix import BiomeAdjacencyMatrix, BiomeAdjacencyRule, AdjacencyRuleType


class BiomeCell:
    """Represents a cell in the biome grid"""
    
    def __init__(self, x: int, y: int, biome: BiomeType, 
                 elevation: float = 0.0,
                 moisture: float = 0.0,
                 temperature: float = 0.0,
                 is_transition: bool = False,
                 transition_strength: float = 0.0):
        """
        Initialize a biome cell
        
        Args:
            x: X coordinate
            y: Y coordinate
            biome: The biome type
            elevation: Elevation value (meters)
            moisture: Moisture value (0-1)
            temperature: Temperature value (Celsius)
            is_transition: Whether this is a transition cell
            transition_strength: Transition strength (0-1)
        """
        self.x = x
        self.y = y
        self.biome = biome
        self.elevation = elevation
        self.moisture = moisture
        self.temperature = temperature
        self.is_transition = is_transition
        self.transition_strength = transition_strength
        self.source_biomes: List[BiomeType] = []
        
    def __str__(self) -> str:
        return f"BiomeCell({self.x}, {self.y}, {self.biome.value})"


class BiomeGrid:
    """2D grid of biome cells"""
    
    def __init__(self, width: int, height: int):
        """
        Initialize a biome grid
        
        Args:
            width: The width of the grid
            height: The height of the grid
        """
        self.width = width
        self.height = height
        self.cells: List[List[BiomeCell]] = []
        
        # Initialize cells with placeholder biome
        for y in range(height):
            row = []
            for x in range(width):
                row.append(BiomeCell(x, y, BiomeType.PLAINS))
            self.cells.append(row)
    
    def get_cell(self, x: int, y: int) -> Optional[BiomeCell]:
        """
        Get a cell at the specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            The cell at the coordinates, or None if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return None
    
    def set_cell(self, x: int, y: int, cell: BiomeCell) -> bool:
        """
        Set a cell at the specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            cell: The cell to set
            
        Returns:
            True if successful, False if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x] = cell
            return True
        return False
    
    def get_neighbors(self, x: int, y: int, distance: int = 1) -> List[BiomeCell]:
        """
        Get neighboring cells within the specified distance
        
        Args:
            x: X coordinate
            y: Y coordinate
            distance: Maximum distance for neighbors
            
        Returns:
            List of neighboring cells
        """
        neighbors = []
        
        for dy in range(-distance, distance + 1):
            for dx in range(-distance, distance + 1):
                if dx == 0 and dy == 0:
                    continue  # Skip the center cell
                    
                nx, ny = x + dx, y + dy
                cell = self.get_cell(nx, ny)
                if cell:
                    neighbors.append(cell)
        
        return neighbors
    
    def get_biome_boundaries(self) -> List[Tuple[BiomeCell, BiomeCell]]:
        """
        Find all boundary pairs between different biomes
        
        Returns:
            List of cell pairs that form boundaries between different biomes
        """
        boundaries = []
        
        # Check horizontal boundaries
        for y in range(self.height):
            for x in range(self.width - 1):
                cell1 = self.cells[y][x]
                cell2 = self.cells[y][x + 1]
                
                if cell1.biome != cell2.biome:
                    boundaries.append((cell1, cell2))
        
        # Check vertical boundaries
        for x in range(self.width):
            for y in range(self.height - 1):
                cell1 = self.cells[y][x]
                cell2 = self.cells[y + 1][x]
                
                if cell1.biome != cell2.biome:
                    boundaries.append((cell1, cell2))
        
        return boundaries
    
    def get_biome_regions(self) -> Dict[BiomeType, List[BiomeCell]]:
        """
        Group cells by biome type
        
        Returns:
            Dictionary mapping biome types to lists of cells
        """
        regions = {}
        
        for y in range(self.height):
            for x in range(self.width):
                cell = self.cells[y][x]
                
                if cell.biome not in regions:
                    regions[cell.biome] = []
                    
                regions[cell.biome].append(cell)
        
        return regions
    
    def get_biome_interfaces(self) -> Dict[Tuple[BiomeType, BiomeType], List[Tuple[BiomeCell, BiomeCell]]]:
        """
        Find all interfaces between different biome types
        
        Returns:
            Dictionary mapping biome pairs to lists of boundary cell pairs
        """
        boundaries = self.get_biome_boundaries()
        interfaces = {}
        
        for cell1, cell2 in boundaries:
            # Sort biome types to create consistent keys
            biome_pair = tuple(sorted([cell1.biome, cell2.biome], key=lambda b: b.value))
            
            if biome_pair not in interfaces:
                interfaces[biome_pair] = []
                
            interfaces[biome_pair].append((cell1, cell2))
        
        return interfaces


class BiomeTransitionGenerator:
    """
    Generator for creating transition zones between incompatible biomes,
    using the BiomeAdjacencyMatrix to determine where transitions are needed.
    """
    
    def __init__(self, adjacency_matrix: BiomeAdjacencyMatrix, rng: DeterministicRNG):
        """
        Initialize the transition generator
        
        Args:
            adjacency_matrix: The biome adjacency matrix defining compatibility rules
            rng: Deterministic random number generator for consistent generation
        """
        self.adjacency_matrix = adjacency_matrix
        self.rng = rng
    
    def generate_transitions(self, biome_grid: BiomeGrid) -> BiomeGrid:
        """
        Generate transition zones in the biome grid
        
        Args:
            biome_grid: The input biome grid
            
        Returns:
            The modified biome grid with transition zones
        """
        # Create a copy of the grid for processing
        result_grid = self._create_grid_copy(biome_grid)
        
        # Find all interfaces between different biomes
        interfaces = biome_grid.get_biome_interfaces()
        
        # Process each interface that needs transitions
        for biome_pair, boundary_pairs in interfaces.items():
            biome1, biome2 = biome_pair
            
            # Skip if biomes are compatible
            if self.adjacency_matrix.are_compatible(biome1, biome2):
                continue
                
            # Get transition parameters
            transition_biomes = self.adjacency_matrix.get_transition_biomes(biome1, biome2)
            min_width = self.adjacency_matrix.get_min_transition_width(biome1, biome2)
            
            # If no suitable transition biomes are found, use a generic ecotone
            if not transition_biomes:
                transition_biomes = [BiomeType.ECOTONE]
                
            # Apply transitions for this biome pair
            self._apply_transition(result_grid, boundary_pairs, biome1, biome2, 
                                   transition_biomes, min_width)
        
        # Smooth out transitions
        self._smooth_transitions(result_grid)
        
        return result_grid
    
    def _create_grid_copy(self, biome_grid: BiomeGrid) -> BiomeGrid:
        """
        Create a deep copy of the biome grid
        
        Args:
            biome_grid: The input grid
            
        Returns:
            A new grid with copied cells
        """
        result = BiomeGrid(biome_grid.width, biome_grid.height)
        
        for y in range(biome_grid.height):
            for x in range(biome_grid.width):
                original = biome_grid.cells[y][x]
                
                copy = BiomeCell(
                    x=original.x,
                    y=original.y,
                    biome=original.biome,
                    elevation=original.elevation,
                    moisture=original.moisture,
                    temperature=original.temperature,
                    is_transition=original.is_transition,
                    transition_strength=original.transition_strength
                )
                
                copy.source_biomes = original.source_biomes.copy() if original.source_biomes else []
                
                result.cells[y][x] = copy
        
        return result
    
    def _apply_transition(self, grid: BiomeGrid, boundary_pairs: List[Tuple[BiomeCell, BiomeCell]],
                         biome1: BiomeType, biome2: BiomeType, 
                         transition_biomes: List[BiomeType], min_width: int) -> None:
        """
        Apply transition zones between two biomes
        
        Args:
            grid: The biome grid to modify
            boundary_pairs: The boundary cell pairs between the two biomes
            biome1: First biome type
            biome2: Second biome type
            transition_biomes: List of suitable transition biomes
            min_width: Minimum width of transition zone
        """
        # Calculate maximum distance for transition based on min_width
        max_distance = min_width * 2
        
        # Create a distance map for both biomes
        distance_map1 = self._create_distance_map(grid, biome1)
        distance_map2 = self._create_distance_map(grid, biome2)
        
        # Process each cell in the grid
        for y in range(grid.height):
            for x in range(grid.width):
                dist1 = distance_map1[y][x]
                dist2 = distance_map2[y][x]
                
                # Skip cells that are too far from both biomes
                if dist1 > max_distance and dist2 > max_distance:
                    continue
                    
                # Skip cells that are not in the transition zone
                if dist1 == 0 or dist2 == 0:
                    # This is a core biome cell
                    continue
                
                # Calculate transition strength based on relative distances
                total_dist = dist1 + dist2
                if total_dist == 0:
                    continue
                    
                # Normalize the strength to 0-1 range
                strength1 = dist2 / total_dist if total_dist > 0 else 0.5
                
                # Choose transition biome based on position in the transition zone
                cell = grid.cells[y][x]
                
                # Only apply transitions to cells that aren't already part of a transition
                if not cell.is_transition:
                    # Choose which transition biome to use based on position and randomness
                    # Use a transition_strength-weighted selection algorithm
                    transition_idx = self._choose_transition_biome(
                        transition_biomes, strength1, self._create_child_rng(x, y)
                    )
                    
                    transition_biome = transition_biomes[transition_idx]
                    
                    # Create transition cell
                    new_cell = BiomeCell(
                        x=x,
                        y=y,
                        biome=transition_biome,
                        elevation=cell.elevation,
                        moisture=self._interpolate_moisture(biome1, biome2, strength1),
                        temperature=self._interpolate_temperature(biome1, biome2, strength1),
                        is_transition=True,
                        transition_strength=strength1
                    )
                    
                    # Record source biomes
                    new_cell.source_biomes = [biome1, biome2]
                    
                    grid.cells[y][x] = new_cell
    
    def _create_distance_map(self, grid: BiomeGrid, target_biome: BiomeType) -> List[List[int]]:
        """
        Create a distance map from each cell to the nearest cell of the target biome
        
        Args:
            grid: The biome grid
            target_biome: The target biome type
            
        Returns:
            2D array of distances
        """
        # Initialize distance map with max values
        max_dist = grid.width + grid.height
        dist_map = [[max_dist for _ in range(grid.width)] for _ in range(grid.height)]
        
        # Set distance to 0 for cells of the target biome
        for y in range(grid.height):
            for x in range(grid.width):
                if grid.cells[y][x].biome == target_biome:
                    dist_map[y][x] = 0
        
        # Process outward from target biome cells to calculate distances
        changed = True
        while changed:
            changed = False
            
            for y in range(grid.height):
                for x in range(grid.width):
                    current = dist_map[y][x]
                    
                    # Check neighbors
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                                
                            nx, ny = x + dx, y + dy
                            
                            if 0 <= nx < grid.width and 0 <= ny < grid.height:
                                # Use Euclidean distance for better quality transitions
                                step = 1.0 if dx == 0 or dy == 0 else 1.414  # √2
                                
                                if dist_map[ny][nx] + step < current:
                                    dist_map[y][x] = dist_map[ny][nx] + step
                                    changed = True
        
        return dist_map
    
    def _choose_transition_biome(self, transition_biomes: List[BiomeType], 
                                strength: float, rng: DeterministicRNG) -> int:
        """
        Choose a transition biome from the candidates based on position in the transition zone
        
        Args:
            transition_biomes: List of candidate transition biomes
            strength: Transition strength (0-1)
            rng: Random number generator
            
        Returns:
            Index of the chosen transition biome
        """
        if len(transition_biomes) == 1:
            return 0
            
        # For multiple transition biomes, use weighted selection based on position
        if len(transition_biomes) == 2:
            # With two biomes, use strength directly to choose
            return 0 if rng.random() < strength else 1
        
        # For more than two biomes, use position-based selection
        # Biomes at the beginning of the list are preferred near biome1 (strength near 1)
        # Biomes at the end of the list are preferred near biome2 (strength near 0)
        target_position = strength * (len(transition_biomes) - 1)
        
        # Calculate weights for each transition biome based on distance from target position
        weights = []
        total_weight = 0
        
        for i in range(len(transition_biomes)):
            # Weight is inversely proportional to distance from target position
            distance = abs(i - target_position)
            weight = 1.0 / (1.0 + distance)
            weights.append(weight)
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        
        # Choose biome using weighted random selection
        choice = rng.random()
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if choice <= cumulative:
                return i
        
        # Fallback to last biome
        return len(transition_biomes) - 1
    
    def _interpolate_moisture(self, biome1: BiomeType, biome2: BiomeType, 
                             strength: float) -> float:
        """
        Interpolate moisture value between two biomes
        
        Args:
            biome1: First biome type
            biome2: Second biome type
            strength: Interpolation factor (0-1, 1 means closer to biome1)
            
        Returns:
            Interpolated moisture value
        """
        params1 = BIOME_PARAMETERS[biome1]
        params2 = BIOME_PARAMETERS[biome2]
        
        # Use average moisture for each biome
        moisture1 = (params1.moisture_range[0] + params1.moisture_range[1]) / 2
        moisture2 = (params2.moisture_range[0] + params2.moisture_range[1]) / 2
        
        # Interpolate
        return moisture1 * strength + moisture2 * (1 - strength)
    
    def _interpolate_temperature(self, biome1: BiomeType, biome2: BiomeType, 
                                strength: float) -> float:
        """
        Interpolate temperature value between two biomes
        
        Args:
            biome1: First biome type
            biome2: Second biome type
            strength: Interpolation factor (0-1, 1 means closer to biome1)
            
        Returns:
            Interpolated temperature value
        """
        params1 = BIOME_PARAMETERS[biome1]
        params2 = BIOME_PARAMETERS[biome2]
        
        # Use average temperature for each biome
        temp1 = (params1.temperature_range[0] + params1.temperature_range[1]) / 2
        temp2 = (params2.temperature_range[0] + params2.temperature_range[1]) / 2
        
        # Interpolate
        return temp1 * strength + temp2 * (1 - strength)
    
    def _smooth_transitions(self, grid: BiomeGrid) -> None:
        """
        Smooth out transition zones for more natural-looking borders
        
        Args:
            grid: The biome grid to smooth
        """
        # Create a copy of the grid to avoid modifying cells while processing
        temp_grid = self._create_grid_copy(grid)
        
        # Process each cell that is part of a transition
        for y in range(grid.height):
            for x in range(grid.width):
                cell = grid.cells[y][x]
                
                if cell.is_transition:
                    # Count surrounding biomes to detect islands and smooth them out
                    neighbors = grid.get_neighbors(x, y, distance=1)
                    
                    biome_counts = {}
                    for neighbor in neighbors:
                        if neighbor.biome not in biome_counts:
                            biome_counts[neighbor.biome] = 0
                        biome_counts[neighbor.biome] += 1
                    
                    # If surrounded by mostly one biome type, conform to it
                    # This prevents single-cell islands in transition zones
                    if len(biome_counts) > 0:
                        max_biome = max(biome_counts.items(), key=lambda x: x[1])[0]
                        
                        # Only apply smoothing in some cases to keep transitions diverse
                        if (biome_counts.get(max_biome, 0) >= 6 and 
                            biome_counts.get(cell.biome, 0) <= 2):
                            # Create a smoothed cell
                            new_cell = BiomeCell(
                                x=x,
                                y=y,
                                biome=max_biome,
                                elevation=cell.elevation,
                                moisture=cell.moisture,
                                temperature=cell.temperature,
                                is_transition=True,
                                transition_strength=cell.transition_strength
                            )
                            new_cell.source_biomes = cell.source_biomes.copy()
                            
                            temp_grid.cells[y][x] = new_cell
        
        # Copy the smoothed cells back to the input grid
        for y in range(grid.height):
            for x in range(grid.width):
                grid.cells[y][x] = temp_grid.cells[y][x]
    
    def _create_child_rng(self, x: int, y: int) -> DeterministicRNG:
        """
        Create a child RNG for a specific grid cell
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            Child RNG with deterministic seed
        """
        # Create a name based on coordinates for deterministic derivation
        cell_name = f"transition_{x}_{y}"
        return self.rng.create_child(cell_name) 