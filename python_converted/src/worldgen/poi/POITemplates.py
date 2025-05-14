#!/usr/bin/env python3
"""
POITemplates.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, Dict
from abc import ABC, abstractmethod


const templates: Dict[POIType, POITemplate] = {
  shop: Dict[str, Any],
  temple: Dict[str, Any],
  ruin: Dict[str, Any],
  camp: Dict[str, Any],
  outpost: Dict[str, Any]
}
class POITemplates {
  static getTemplate(type: POIType): POITemplate {
    return templates[type]
  }
} 