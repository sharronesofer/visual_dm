#!/usr/bin/env python3
"""
types.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from abc import ABC, abstractmethod


{ BuildingType }
class InteriorParams:
    buildingType: BuildingType
    width: float
    length: float
    height: float
    entryPoints: Dict[str, Any]
class InteriorLayout:
    rooms: List[Room]
    doors: List[Door]
    furniture: List[FurniturePlacement]
    decorations: List[DecorationPlacement]
class Room:
    id: str
    type: str
    x: float
    y: float
    width: float
    length: float
class Door:
    fromRoom: str
    toRoom: str
    x: float
    y: float
class FurniturePlacement:
    roomId: str
    type: str
    x: float
    y: float
    rotation: float
class DecorationPlacement:
    roomId: str
    type: str
    x: float
    y: float
    rotation: float
    colorPalette: List[str]
class InteriorMesh:
    vertices: List[List[float]]
    faces: List[List[float]]
    lod: float
class VariationParams:
    region: str
    culture: str
    style: str 