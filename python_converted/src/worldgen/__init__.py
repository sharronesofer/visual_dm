#!/usr/bin/env python3
"""
World Generation System - Main module

This module contains various sub-modules for world generation:
- Core utilities
- Environment systems (including biomes, weather, and hazards)
- Region generators
- Interior generators
- POI (Points of Interest) generators
- Faction generators
"""

# Import core components
from .core import *

# Import environment components
from .environment import (
    # Biome types and systems
    BiomeType, BiomeClassification, BiomeParameters, 
    BiomeAdjacencyMatrix, BiomeAdjacencyRule, AdjacencyRuleType,
    BiomeCell, BiomeGrid, BiomeTransitionGenerator, BiomeConfigManager,
    
    # Environmental systems
    WeatherSystem, HazardSystem, GlobalEnvironmentManager,
    
    # Environmental types
    WeatherType, WeatherPattern, HazardType, Hazard, Region, EnvironmentalState
)

# Import from other modules as needed
from .region import *
from .interior import *
from .poi import *
from .faction import *

# Version information
__version__ = "1.0.0"
__author__ = "Visual DM Team"

# Define exported symbols
__all__ = [
    # Core
    'DeterministicRNG',
    'IWorldGenerator',
    
    # Environment - Biomes
    'BiomeType',
    'BiomeClassification',
    'BiomeParameters',
    'BiomeAdjacencyMatrix',
    'BiomeAdjacencyRule',
    'AdjacencyRuleType',
    'BiomeCell',
    'BiomeGrid',
    'BiomeTransitionGenerator',
    'BiomeConfigManager',
    
    # Environment - Systems
    'WeatherSystem',
    'HazardSystem',
    'GlobalEnvironmentManager',
    
    # Environment - Types
    'WeatherType',
    'WeatherPattern',
    'HazardType',
    'Hazard',
    'Region',
    'EnvironmentalState',
    
    # Other modules
    'BaseRegionGenerator',
    'ProceduralRegionGenerator',
    'HandcraftedRegionGenerator',
    'RegionGeneratorFactory',
    'IRegionModifier'
] 