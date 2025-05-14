#!/usr/bin/env python3
"""
types.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union
from abc import ABC, abstractmethod


POIType = Union['shop', 'temple', 'ruin', 'camp', 'outpost']
class POITemplate:
    id: str
    type: POIType
    baseDescription: str
    baseLoot: List[str]
    baseNPCs: List[str]
class POIModifier:
    id: str
    description: str
    lootModifier?: List[(loot: List[str]) => str]
    npcModifier?: List[(npcs: List[str]) => str]
    questHook?: str
class POIContent:
    template: \'POITemplate\'
    modifiers: List[POIModifier]
    loot: List[str]
    npcs: List[str]
    tags: List[str]
class POIState:
    poiId: str
    visited: bool
    discoveredLoot: List[str]
    interactedNPCs: List[str]
    questState: Dict[str, Any> 