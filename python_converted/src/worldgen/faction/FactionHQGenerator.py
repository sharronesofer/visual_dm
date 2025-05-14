#!/usr/bin/env python3
"""
FactionHQGenerator.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, List
from abc import ABC, abstractmethod


class FactionHQGenerator {
  generate(type: FactionType): FactionHQLayout {
    const style = FactionStyles.getStyle(type)
    const roomTemplates = RoomTypes.getForFaction(type)
    const rooms: List[FactionRoom] = roomTemplates.map((tpl, i) => ({
      id: `${tpl.type}_${i}`,
      type: tpl.type || 'generic',
      x: i * 5,
      y: i * 5,
      width: 8 + i,
      length: 10 + i,
      specialPurpose: tpl.specialPurpose
    }))
    const npcs = NPCPopulation.generate(type)
    const security = SecuritySystem.generate(type, rooms.length() * 10)
    const decor = DecorationSystem.generate(type)
    return {
      rooms,
      npcs,
      security,
      style,
      decor
    }
  }
} 