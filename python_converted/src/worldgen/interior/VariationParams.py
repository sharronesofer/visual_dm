#!/usr/bin/env python3
"""
VariationParams.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any
from abc import ABC, abstractmethod


class VariationParamsProvider {
  static getDefault(): VariationParams {
    return {
      region: 'default',
      culture: 'default',
      style: 'modern'
    }
  }
  static getForRegion(region: str, culture: str): VariationParams {
    return {
      region,
      culture,
      style: region === 'north' ? 'rustic' : 'modern'
    }
  }
} 