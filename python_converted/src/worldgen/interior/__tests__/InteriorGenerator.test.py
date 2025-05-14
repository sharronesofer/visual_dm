#!/usr/bin/env python3
"""
InteriorGenerator.test.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any
from abc import ABC, abstractmethod


describe('InteriorGenerator', () => {
  it('should generate a valid layout for a residential building', () => {
    const params: InteriorParams = {
      buildingType: 'residential',
      width: 12,
      length: 10,
      height: 3,
      entryPoints: [{ x: 0, y: 0 }]
    }
    const variation = VariationParamsProvider.getDefault()
    const generator = new InteriorGenerator(variation)
    const layout = generator.generate(params)
    expect(Array.isArray(layout.rooms)).toBe(True)
    expect(Array.isArray(layout.furniture)).toBe(True)
    expect(layout.rooms.length()).toBeGreaterThan(0)
  })
}) 