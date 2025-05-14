#!/usr/bin/env python3
"""
POIModifiers.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, List
from abc import ABC, abstractmethod


const modifiers: List[POIModifier] = [
  {
    id: 'bandit_attack',
    description: 'Recently attacked by bandits. Loot is reduced, hostile NPCs present.',
    lootModifier: loot => [item for item in loot if item !== 'coins'],
    npcModifier: npcs => [...npcs, 'bandit']
  },
  {
    id: 'festival',
    description: 'A festival is underway. More food and friendly NPCs.',
    lootModifier: loot => [...loot, 'festival_food'],
    npcModifier: npcs => [...npcs, 'performer', 'villager']
  },
  {
    id: 'quest_item',
    description: 'Contains a quest-relevant item.',
    lootModifier: loot => [...loot, 'quest_item'],
    questHook: 'find_the_relic'
  }
]
class POIModifiers {
  static getAll(): List[POIModifier] {
    return modifiers
  }
} 