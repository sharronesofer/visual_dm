#!/usr/bin/env python3
"""
types.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, List, Union
from abc import ABC, abstractmethod


WeatherType = Union['clear', 'rain', 'snow', 'fog', 'storm', 'windy']
class WeatherPattern:
    type: WeatherType
    intensity: float
    region: str
    duration: float
HazardType = Union['flood', 'avalanche', 'radiation', 'fire', 'storm']
class Hazard:
    id: str
    type: HazardType
    region: str
    x: float
    y: float
    severity: float
    active: bool
class Region:
    id: str
    name: str
    climate: str
class EnvironmentalState:
    weather: \'WeatherPattern\'
    hazards: List[Hazard]
    season: str
    time: float 