"""World Generation System - Environment module

This module contains the environment systems and biome types for world generation:

- Biome Types (BiomeTypes)
- Biome Adjacency Matrix (BiomeAdjacencyMatrix)
- Biome Transition Generator (BiomeTransitionGenerator)
- Biome Configuration Manager (BiomeConfigManager)
- Weather System (WeatherSystem)
- Hazard System (HazardSystem)
- Global Environment Manager (GlobalEnvironmentManager)
"""

from .BiomeTypes import (
    BiomeType, 
    BiomeClassification, 
    BiomeParameters,
    BIOME_PARAMETERS,
    TRANSITION_BIOMES,
    MoistureLevel,
    TemperatureLevel,
    get_biome_by_conditions
)

from .BiomeAdjacencyMatrix import (
    BiomeAdjacencyMatrix,
    BiomeAdjacencyRule,
    AdjacencyRuleType
)

from .BiomeTransitionGenerator import (
    BiomeCell,
    BiomeGrid,
    BiomeTransitionGenerator
)

from .BiomeConfigManager import BiomeConfigManager

from .types import (
    WeatherType,
    WeatherPattern,
    HazardType,
    Hazard,
    Region,
    EnvironmentalState
)

from .WeatherSystem import WeatherSystem
from .HazardSystem import HazardSystem
from .GlobalEnvironmentManager import GlobalEnvironmentManager

__all__ = [
    # Biome types and parameters
    'BiomeType',
    'BiomeClassification',
    'BiomeParameters',
    'BIOME_PARAMETERS',
    'TRANSITION_BIOMES',
    'MoistureLevel',
    'TemperatureLevel',
    'get_biome_by_conditions',
    
    # Biome adjacency and transitions
    'BiomeAdjacencyMatrix',
    'BiomeAdjacencyRule',
    'AdjacencyRuleType',
    'BiomeCell',
    'BiomeGrid',
    'BiomeTransitionGenerator',
    'BiomeConfigManager',
    
    # Environmental types
    'WeatherType',
    'WeatherPattern',
    'HazardType',
    'Hazard',
    'Region',
    'EnvironmentalState',
    
    # Systems
    'WeatherSystem',
    'HazardSystem',
    'GlobalEnvironmentManager'
] 