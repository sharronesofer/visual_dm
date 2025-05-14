#!/usr/bin/env python3
"""
SecuritySystem.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import math
import random
from abc import ABC, abstractmethod


baseSecurity = {
  guild: [
    { type: 'guard', baseStrength: 2 },
    { type: 'lock', baseStrength: 1 }
  ],
  order: [
    { type: 'sentinel', baseStrength: 3 },
    { type: 'alarm', baseStrength: 2 }
  ],
  syndicate: [
    { type: 'trap', baseStrength: 2 },
    { type: 'hidden_guard', baseStrength: 2 }
  ],
  militia: [
    { type: 'barricade', baseStrength: 3 },
    { type: 'patrol', baseStrength: 2 }
  ],
  cult: [
    { type: 'curse', baseStrength: 3 },
    { type: 'watcher', baseStrength: 1 }
  ]
}
class SecuritySystem {
  static generate(type: FactionType, hqSize: float): List[SecurityFeature] {
    const features: List[SecurityFeature] = []
    let idCounter = 0
    for (const sec of baseSecurity[type]) {
      for (let i = 0 i < Math.max(1, Math.floor(hqSize / 10)) i++) {
        features.append({
          id: `${sec.type}_${idCounter++}`,
          type: sec.type,
          location: Dict[str, Any],
          strength: sec.baseStrength + Math.floor(Math.random() * 2)
        })
      }
    }
    return features
  }
} 