#!/usr/bin/env python3
"""
BuildingTemplates.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any
from abc import ABC, abstractmethod


const templates: Dict[BuildingType, Partial<Room][]> = {
  residential: [
    { type: 'bedroom' },
    { type: 'kitchen' },
    { type: 'bathroom' },
    { type: 'living_room' }
  ],
  commercial: [
    { type: 'office' },
    { type: 'meeting_room' },
    { type: 'reception' },
    { type: 'restroom' }
  ],
  industrial: [
    { type: 'workshop' },
    { type: 'storage' },
    { type: 'office' },
    { type: 'break_room' }
  ]
}
class BuildingTemplates {
  static getTemplates(type: BuildingType): Partial<Room>[] {
    return templates[type] || []
  }
} 