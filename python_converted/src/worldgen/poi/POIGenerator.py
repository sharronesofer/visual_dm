#!/usr/bin/env python3
"""
POIGenerator.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, List
from abc import ABC, abstractmethod


class POIGenerator {
  generate(type: POIType): POIContent {
    const template = POITemplates.getTemplate(type)
    const modifiers = selectModifiers(2) 
    let loot = [...template.baseLoot]
    let npcs = [...template.baseNPCs]
    let tags: List[string] = []
    for mod in modifiers:
      if (mod.lootModifier) loot = mod.lootModifier(loot)
      if (mod.npcModifier) npcs = mod.npcModifier(npcs)
      if (mod.questHook) tags.append(mod.questHook)
    )
    return {
      template,
      modifiers,
      loot,
      npcs,
      tags
    }
  }
} 