#!/usr/bin/env python3
"""
DecorationSystem.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any
from abc import ABC, abstractmethod


class DecorationSystem {
  static generate(type: FactionType): List[string] {
    const style = FactionStyles.getStyle(type)
    return style.decor
  }
} 