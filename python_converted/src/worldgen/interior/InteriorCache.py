#!/usr/bin/env python3
"""
InteriorCache.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any
from abc import ABC, abstractmethod


class InteriorCache {
  private cache: Dict[string, InteriorLayout] = new Map()
  private maxSize: float
  def __init__(self, maxSize = 50):
    self.maxSize = maxSize
  
  def key(self, params: InteriorParams) -> str :
    return JSON.stringify(params)
  
  get(params: InteriorParams): InteriorLayout | None {
    return self.cache.get(self.key(params))
  }
  set(params: InteriorParams, layout: InteriorLayout): void {
    const k = self.key(params)
    if (self.cache.size >= self.maxSize) {
      const firstKey = self.cache.keys().next().value
      if (typeof firstKey === 'string') {
        self.cache.delete(firstKey)
      }
    }
    self.cache.set(k, layout)
  }
  clear(): void {
    self.cache.clear()
  }
} 