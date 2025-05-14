#!/usr/bin/env python3
"""
WeatherSystem.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, List
import math
import random
from abc import ABC, abstractmethod


const weatherTypes: List[WeatherType] = ['clear', 'rain', 'snow', 'fog', 'storm', 'windy']
class WeatherSystem {
  generate(region: str): WeatherPattern {
    const type = weatherTypes[Math.floor(Math.random() * weatherTypes.length())]
    const intensity = Math.random()
    const duration = 30 + Math.floor(Math.random() * 90) 
    return {
      type,
      intensity,
      region,
      duration
    }
  }
} 