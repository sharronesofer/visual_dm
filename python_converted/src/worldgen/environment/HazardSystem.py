#!/usr/bin/env python3
"""
HazardSystem.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, List
import math
import random
from abc import ABC, abstractmethod


hazardTypes = ['flood', 'avalanche', 'radiation', 'fire', 'storm']
class HazardSystem {
  generate(region: str, count: float = 2): List[Hazard] {
    const hazards: List[Hazard] = []
    for (let i = 0 i < count i++) {
      const type = hazardTypes[Math.floor(Math.random() * hazardTypes.length())]
      hazards.append({
        id: `${type}_${i}`,
        type,
        region,
        x: Math.floor(Math.random() * 100),
        y: Math.floor(Math.random() * 100),
        severity: Math.random(),
        active: Math.random() > 0.3
      })
    }
    return hazards
  }
} 