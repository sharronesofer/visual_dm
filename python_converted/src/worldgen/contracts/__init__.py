#!/usr/bin/env python3
"""
contracts/__init__.py - Data Contracts for World Generation System

This module defines standardized APIs and data contracts for the World Generation System outputs.
It provides well-defined interfaces for how other game systems can interact with:
- Regions
- Points of Interest (POIs)
- Biomes
- Environmental features

Version: 1.0.0
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol, Generic
from enum import Enum
from abc import ABC, abstractmethod

# Import specific contracts once implemented
from .base import (
    WorldGenVersion,
    ContractVersioned,
    WorldGenContract,
    WorldGenContractError,
    WorldGenContractValidator
)

from .region import (
    RegionContract,
    RegionCellContract,
    RegionQuery,
    RegionResult
)

from .poi import (
    POIContract,
    POITemplateContract,
    POIQuery,
    POIResult
)

from .biome import (
    BiomeContract,
    BiomeParametersContract,
    BiomeRelationship,
    BiomeQuery,
    BiomeResult
)

from .environment import (
    EnvironmentContract,
    WeatherContract,
    HazardContract,
    SeasonContract,
    TimeContract,
    EnvironmentQuery,
    EnvironmentResult
)

__all__ = [
    # Base contracts
    'WorldGenVersion',
    'ContractVersioned',
    'WorldGenContract',
    'WorldGenContractError',
    'WorldGenContractValidator',
    
    # Region contracts
    'RegionContract',
    'RegionCellContract',
    'RegionQuery',
    'RegionResult',
    
    # POI contracts
    'POIContract',
    'POITemplateContract',
    'POIQuery', 
    'POIResult',
    
    # Biome contracts
    'BiomeContract',
    'BiomeParametersContract',
    'BiomeRelationship',
    'BiomeQuery',
    'BiomeResult',
    
    # Environment contracts
    'EnvironmentContract',
    'WeatherContract',
    'HazardContract',
    'SeasonContract',
    'TimeContract',
    'EnvironmentQuery',
    'EnvironmentResult'
] 