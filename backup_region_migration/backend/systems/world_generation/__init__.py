"""
World Generation System

Handles world generation logic for Visual DM. Creates continent-sized worlds 
(100-200 regions) with optional islands, featuring proper biome placement,
terrain generation, and resource distribution.

Canonical location: backend.systems.world_generation
"""

from .services.world_generator import (
    WorldGenerator,
    WorldGenerationConfig,
    WorldGenerationResult
)

from .config.biome_config import BiomeConfigManager
from .config.world_templates import WorldTemplateManager, WorldTemplate

from .algorithms.perlin_noise import PerlinNoiseGenerator
from .algorithms.biome_placement import BiomePlacementEngine

__version__ = "1.0.0"

__all__ = [
    # Core services
    "WorldGenerator",
    "WorldGenerationConfig",
    "WorldGenerationResult",
    
    # Configuration managers
    "BiomeConfigManager",
    "WorldTemplateManager",
    "WorldTemplate",
    
    # Algorithms
    "PerlinNoiseGenerator",
    "BiomePlacementEngine"
] 