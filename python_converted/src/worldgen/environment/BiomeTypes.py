#!/usr/bin/env python3
"""
BiomeTypes.py - Part of the World Generation System

Defines biome types, classifications, and parameters for the world generation system.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Union, Set
from dataclasses import dataclass, field


class BiomeType(Enum):
    """Enumeration of all available biome types in the world generation system"""
    # Major dry biomes
    DESERT = "desert"
    SAVANNA = "savanna"
    SHRUBLAND = "shrubland"
    
    # Major temperate biomes
    PLAINS = "plains"
    GRASSLAND = "grassland"
    TEMPERATE_FOREST = "temperate_forest"
    TEMPERATE_RAINFOREST = "temperate_rainforest"
    
    # Major cold biomes
    TAIGA = "taiga"
    TUNDRA = "tundra"
    ICE = "ice"
    
    # Major tropical biomes
    TROPICAL_RAINFOREST = "tropical_rainforest"
    TROPICAL_SEASONAL_FOREST = "tropical_seasonal_forest"
    
    # Major wetland biomes
    MARSH = "marsh"
    SWAMP = "swamp"
    BOG = "bog"
    
    # Major mountain biomes
    ALPINE = "alpine"
    MOUNTAIN = "mountain"
    VOLCANO = "volcano"
    
    # Major water biomes
    OCEAN = "ocean"
    COAST = "coast"
    RIVER = "river"
    LAKE = "lake"
    
    # Transition biomes
    BEACH = "beach"
    ESTUARY = "estuary"
    OASIS = "oasis"
    
    # Special transition biomes
    ECOTONE = "ecotone"  # Generic transition zone


class BiomeClassification(Enum):
    """Classification of biomes by their general characteristics"""
    DRY = "dry"
    TEMPERATE = "temperate"
    COLD = "cold"
    TROPICAL = "tropical"
    WETLAND = "wetland"
    MOUNTAIN = "mountain"
    WATER = "water"
    TRANSITION = "transition"


class MoistureLevel(Enum):
    """Moisture level classifications"""
    VERY_DRY = 0
    DRY = 1
    MODERATE = 2
    MOIST = 3
    WET = 4
    VERY_WET = 5


class TemperatureLevel(Enum):
    """Temperature level classifications"""
    FREEZING = 0
    COLD = 1
    COOL = 2
    MILD = 3
    WARM = 4
    HOT = 5
    VERY_HOT = 6


@dataclass
class BiomeParameters:
    """Parameters defining the environmental conditions of a biome"""
    # Primary parameters
    temperature_range: tuple[float, float]  # Min and max temperature in Celsius
    moisture_range: tuple[float, float]  # Min and max moisture (0-1)
    elevation_range: tuple[float, float]  # Min and max elevation in meters
    
    # Classification
    classification: BiomeClassification
    temperature_class: TemperatureLevel
    moisture_class: MoistureLevel
    
    # Optional parameters
    soil_fertility: float = 0.5  # 0-1 scale
    vegetation_density: float = 0.5  # 0-1 scale
    biodiversity: float = 0.5  # 0-1 scale
    
    # Aesthetic parameters
    base_color: str = "#7D9951"  # Default to a neutral green
    
    # Transitional properties
    is_transition_biome: bool = False
    transition_weight: float = 1.0  # How suitable as transition (higher = more suitable)


# Define standard biome parameters
BIOME_PARAMETERS: Dict[BiomeType, BiomeParameters] = {
    BiomeType.DESERT: BiomeParameters(
        temperature_range=(20, 50),
        moisture_range=(0, 0.2),
        elevation_range=(0, 2500),
        classification=BiomeClassification.DRY,
        temperature_class=TemperatureLevel.HOT,
        moisture_class=MoistureLevel.VERY_DRY,
        soil_fertility=0.1,
        vegetation_density=0.1,
        biodiversity=0.2,
        base_color="#E9DDAF"
    ),
    BiomeType.SAVANNA: BiomeParameters(
        temperature_range=(20, 30),
        moisture_range=(0.2, 0.4),
        elevation_range=(0, 2000),
        classification=BiomeClassification.DRY,
        temperature_class=TemperatureLevel.HOT,
        moisture_class=MoistureLevel.DRY,
        soil_fertility=0.4,
        vegetation_density=0.3,
        biodiversity=0.5,
        base_color="#D6CC9E"
    ),
    BiomeType.SHRUBLAND: BiomeParameters(
        temperature_range=(5, 25),
        moisture_range=(0.2, 0.4),
        elevation_range=(0, 2500),
        classification=BiomeClassification.DRY,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.DRY,
        soil_fertility=0.3,
        vegetation_density=0.4,
        biodiversity=0.4,
        base_color="#C5C591",
        transition_weight=1.5
    ),
    BiomeType.PLAINS: BiomeParameters(
        temperature_range=(0, 25),
        moisture_range=(0.3, 0.6),
        elevation_range=(0, 2000),
        classification=BiomeClassification.TEMPERATE,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.MODERATE,
        soil_fertility=0.7,
        vegetation_density=0.5,
        biodiversity=0.5,
        base_color="#B5CF80",
        transition_weight=1.8
    ),
    BiomeType.GRASSLAND: BiomeParameters(
        temperature_range=(5, 20),
        moisture_range=(0.4, 0.6),
        elevation_range=(0, 2500),
        classification=BiomeClassification.TEMPERATE,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.MODERATE,
        soil_fertility=0.8,
        vegetation_density=0.6,
        biodiversity=0.6,
        base_color="#A8CF80",
        transition_weight=2.0
    ),
    BiomeType.TEMPERATE_FOREST: BiomeParameters(
        temperature_range=(3, 18),
        moisture_range=(0.6, 0.8),
        elevation_range=(0, 2000),
        classification=BiomeClassification.TEMPERATE,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.MOIST,
        soil_fertility=0.9,
        vegetation_density=0.9,
        biodiversity=0.8,
        base_color="#52A36E"
    ),
    BiomeType.TEMPERATE_RAINFOREST: BiomeParameters(
        temperature_range=(8, 17),
        moisture_range=(0.8, 1.0),
        elevation_range=(0, 2000),
        classification=BiomeClassification.TEMPERATE,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.VERY_WET,
        soil_fertility=0.8,
        vegetation_density=1.0,
        biodiversity=0.9,
        base_color="#2E8C5E"
    ),
    BiomeType.TAIGA: BiomeParameters(
        temperature_range=(-10, 5),
        moisture_range=(0.4, 0.8),
        elevation_range=(0, 2000),
        classification=BiomeClassification.COLD,
        temperature_class=TemperatureLevel.COLD,
        moisture_class=MoistureLevel.MOIST,
        soil_fertility=0.4,
        vegetation_density=0.7,
        biodiversity=0.5,
        base_color="#7A9978"
    ),
    BiomeType.TUNDRA: BiomeParameters(
        temperature_range=(-15, 0),
        moisture_range=(0.1, 0.4),
        elevation_range=(0, 3000),
        classification=BiomeClassification.COLD,
        temperature_class=TemperatureLevel.FREEZING,
        moisture_class=MoistureLevel.DRY,
        soil_fertility=0.2,
        vegetation_density=0.2,
        biodiversity=0.3,
        base_color="#BFCCC2",
        transition_weight=1.2
    ),
    BiomeType.ICE: BiomeParameters(
        temperature_range=(-50, -5),
        moisture_range=(0.0, 0.3),
        elevation_range=(0, 5000),
        classification=BiomeClassification.COLD,
        temperature_class=TemperatureLevel.FREEZING,
        moisture_class=MoistureLevel.VERY_DRY,
        soil_fertility=0.0,
        vegetation_density=0.0,
        biodiversity=0.1,
        base_color="#EAEFF2"
    ),
    BiomeType.TROPICAL_RAINFOREST: BiomeParameters(
        temperature_range=(20, 35),
        moisture_range=(0.8, 1.0),
        elevation_range=(0, 1500),
        classification=BiomeClassification.TROPICAL,
        temperature_class=TemperatureLevel.VERY_HOT,
        moisture_class=MoistureLevel.VERY_WET,
        soil_fertility=0.7,
        vegetation_density=1.0,
        biodiversity=1.0,
        base_color="#10853E"
    ),
    BiomeType.TROPICAL_SEASONAL_FOREST: BiomeParameters(
        temperature_range=(20, 35),
        moisture_range=(0.6, 0.8),
        elevation_range=(0, 1500),
        classification=BiomeClassification.TROPICAL,
        temperature_class=TemperatureLevel.HOT,
        moisture_class=MoistureLevel.MOIST,
        soil_fertility=0.8,
        vegetation_density=0.9,
        biodiversity=0.9,
        base_color="#379148"
    ),
    BiomeType.MARSH: BiomeParameters(
        temperature_range=(5, 25),
        moisture_range=(0.8, 1.0),
        elevation_range=(0, 500),
        classification=BiomeClassification.WETLAND,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.VERY_WET,
        soil_fertility=0.8,
        vegetation_density=0.7,
        biodiversity=0.8,
        base_color="#6A8F6C"
    ),
    BiomeType.SWAMP: BiomeParameters(
        temperature_range=(15, 30),
        moisture_range=(0.8, 1.0),
        elevation_range=(0, 500),
        classification=BiomeClassification.WETLAND,
        temperature_class=TemperatureLevel.WARM,
        moisture_class=MoistureLevel.VERY_WET,
        soil_fertility=0.7,
        vegetation_density=0.8,
        biodiversity=0.8,
        base_color="#5F8D6A"
    ),
    BiomeType.BOG: BiomeParameters(
        temperature_range=(0, 15),
        moisture_range=(0.8, 1.0),
        elevation_range=(0, 500),
        classification=BiomeClassification.WETLAND,
        temperature_class=TemperatureLevel.COOL,
        moisture_class=MoistureLevel.VERY_WET,
        soil_fertility=0.5,
        vegetation_density=0.6,
        biodiversity=0.6,
        base_color="#7D8F75"
    ),
    BiomeType.ALPINE: BiomeParameters(
        temperature_range=(-10, 5),
        moisture_range=(0.3, 0.7),
        elevation_range=(2000, 4000),
        classification=BiomeClassification.MOUNTAIN,
        temperature_class=TemperatureLevel.COLD,
        moisture_class=MoistureLevel.MODERATE,
        soil_fertility=0.3,
        vegetation_density=0.3,
        biodiversity=0.4,
        base_color="#A5A8AF"
    ),
    BiomeType.MOUNTAIN: BiomeParameters(
        temperature_range=(-5, 15),
        moisture_range=(0.3, 0.7),
        elevation_range=(1000, 4000),
        classification=BiomeClassification.MOUNTAIN,
        temperature_class=TemperatureLevel.COOL,
        moisture_class=MoistureLevel.MODERATE,
        soil_fertility=0.4,
        vegetation_density=0.5,
        biodiversity=0.5,
        base_color="#918F7F"
    ),
    BiomeType.VOLCANO: BiomeParameters(
        temperature_range=(10, 50),
        moisture_range=(0.1, 0.5),
        elevation_range=(500, 5000),
        classification=BiomeClassification.MOUNTAIN,
        temperature_class=TemperatureLevel.VERY_HOT,
        moisture_class=MoistureLevel.DRY,
        soil_fertility=0.6,
        vegetation_density=0.3,
        biodiversity=0.3,
        base_color="#7F615D"
    ),
    BiomeType.OCEAN: BiomeParameters(
        temperature_range=(-5, 30),
        moisture_range=(1.0, 1.0),
        elevation_range=(-10000, -10),
        classification=BiomeClassification.WATER,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.VERY_WET,
        soil_fertility=0.0,
        vegetation_density=0.2,
        biodiversity=0.7,
        base_color="#1A4C80"
    ),
    BiomeType.COAST: BiomeParameters(
        temperature_range=(-5, 30),
        moisture_range=(1.0, 1.0),
        elevation_range=(-200, -1),
        classification=BiomeClassification.WATER,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.VERY_WET,
        soil_fertility=0.0,
        vegetation_density=0.3,
        biodiversity=0.8,
        base_color="#306EA6"
    ),
    BiomeType.RIVER: BiomeParameters(
        temperature_range=(-5, 30),
        moisture_range=(1.0, 1.0),
        elevation_range=(-20, 0),
        classification=BiomeClassification.WATER,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.VERY_WET,
        soil_fertility=0.0,
        vegetation_density=0.4,
        biodiversity=0.7,
        base_color="#4F9BCD"
    ),
    BiomeType.LAKE: BiomeParameters(
        temperature_range=(-5, 30),
        moisture_range=(1.0, 1.0),
        elevation_range=(-50, 0),
        classification=BiomeClassification.WATER,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.VERY_WET,
        soil_fertility=0.0,
        vegetation_density=0.3,
        biodiversity=0.6,
        base_color="#4287B5"
    ),
    BiomeType.BEACH: BiomeParameters(
        temperature_range=(5, 35),
        moisture_range=(0.3, 0.7),
        elevation_range=(0, 5),
        classification=BiomeClassification.TRANSITION,
        temperature_class=TemperatureLevel.WARM,
        moisture_class=MoistureLevel.MODERATE,
        soil_fertility=0.2,
        vegetation_density=0.2,
        biodiversity=0.4,
        base_color="#E6D9AF",
        is_transition_biome=True,
        transition_weight=2.0
    ),
    BiomeType.ESTUARY: BiomeParameters(
        temperature_range=(5, 30),
        moisture_range=(0.7, 1.0),
        elevation_range=(-10, 5),
        classification=BiomeClassification.TRANSITION,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.VERY_WET,
        soil_fertility=0.7,
        vegetation_density=0.6,
        biodiversity=0.9,
        base_color="#7D9E8C",
        is_transition_biome=True,
        transition_weight=1.5
    ),
    BiomeType.OASIS: BiomeParameters(
        temperature_range=(15, 40),
        moisture_range=(0.6, 0.9),
        elevation_range=(0, 500),
        classification=BiomeClassification.TRANSITION,
        temperature_class=TemperatureLevel.HOT,
        moisture_class=MoistureLevel.MOIST,
        soil_fertility=0.8,
        vegetation_density=0.8,
        biodiversity=0.7,
        base_color="#75A743",
        is_transition_biome=True,
        transition_weight=1.0
    ),
    BiomeType.ECOTONE: BiomeParameters(
        temperature_range=(-10, 40),
        moisture_range=(0.3, 0.8),
        elevation_range=(0, 3000),
        classification=BiomeClassification.TRANSITION,
        temperature_class=TemperatureLevel.MILD,
        moisture_class=MoistureLevel.MODERATE,
        soil_fertility=0.5,
        vegetation_density=0.5,
        biodiversity=0.7,
        base_color="#A0B080",
        is_transition_biome=True,
        transition_weight=3.0
    ),
}

# Define biomes that are good for transitions
TRANSITION_BIOMES = {
    BiomeType.SHRUBLAND,
    BiomeType.PLAINS, 
    BiomeType.GRASSLAND,
    BiomeType.ECOTONE,
    BiomeType.BEACH,
    BiomeType.ESTUARY,
    BiomeType.OASIS,
}

# Get biome by temperature and moisture
def get_biome_by_conditions(temperature: float, moisture: float, elevation: float) -> BiomeType:
    """
    Determine the appropriate biome based on temperature, moisture, and elevation.
    
    Args:
        temperature: Temperature in Celsius
        moisture: Moisture level (0-1)
        elevation: Elevation in meters
        
    Returns:
        The most appropriate BiomeType for these conditions
    """
    best_match = None
    best_score = float('inf')
    
    for biome_type, params in BIOME_PARAMETERS.items():
        # Skip transition biomes for initial assignment
        if params.is_transition_biome:
            continue
            
        # Check if within elevation range
        if not (params.elevation_range[0] <= elevation <= params.elevation_range[1]):
            continue
            
        # Calculate score based on distance from ideal conditions
        temp_score = 0
        if temperature < params.temperature_range[0]:
            temp_score = params.temperature_range[0] - temperature
        elif temperature > params.temperature_range[1]:
            temp_score = temperature - params.temperature_range[1]
            
        moisture_score = 0
        if moisture < params.moisture_range[0]:
            moisture_score = params.moisture_range[0] - moisture
        elif moisture > params.moisture_range[1]:
            moisture_score = moisture - params.moisture_range[1]
            
        # Combine scores (weighted)
        total_score = (temp_score * 1.0) + (moisture_score * 2.0)
        
        if total_score < best_score:
            best_score = total_score
            best_match = biome_type
    
    # Fallback to a default biome if no match found
    if best_match is None:
        if elevation < 0:
            return BiomeType.OCEAN
        else:
            return BiomeType.PLAINS
            
    return best_match 