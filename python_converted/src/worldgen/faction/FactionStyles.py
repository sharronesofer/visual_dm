#!/usr/bin/env python3
"""
FactionStyles.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, Dict
from abc import ABC, abstractmethod


const styles: Dict[FactionType, FactionStyle] = {
  guild: Dict[str, Any],
  order: Dict[str, Any],
  syndicate: Dict[str, Any],
  militia: Dict[str, Any],
  cult: Dict[str, Any]
}
class FactionStyles {
  static getStyle(type: FactionType): FactionStyle {
    return styles[type]
  }
} 