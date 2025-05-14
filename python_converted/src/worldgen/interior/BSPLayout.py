#!/usr/bin/env python3
"""
BSPLayout.py - Part of the World Generation System

This file was auto-converted from TypeScript to Python.
"""

from typing import Dict, List, Optional, Any, Union, TypeVar, Protocol
from abc import ABC, abstractmethod
from typing import Any, List
import math
from abc import ABC, abstractmethod


let roomIdCounter = 0
function generateRoomId() {
  return `room_${roomIdCounter++}`
}
class BSPLayout {
  def __init__(self, private params: InteriorParams):
  generateRooms(): List[Room] {
    const minRoomSize = 3
    const rooms: List[Room] = []
    function split(x: float, y: float, width: float, length: float) {
      if (width <= minRoomSize * 2 && length <= minRoomSize * 2) {
        rooms.append({
          id: generateRoomId(),
          type: 'generic',
          x,
          y,
          width,
          length
        })
        return
      }
      const splitVertically = width > length
      if (splitVertically && width > minRoomSize * 2) {
        const splitAt = Math.floor(width / 2)
        split(x, y, splitAt, length)
        split(x + splitAt, y, width - splitAt, length)
      } else if (length > minRoomSize * 2) {
        const splitAt = Math.floor(length / 2)
        split(x, y, width, splitAt)
        split(x, y + splitAt, width, length - splitAt)
      } else {
        rooms.append({
          id: generateRoomId(),
          type: 'generic',
          x,
          y,
          width,
          length
        })
      }
    }
    split(0, 0, self.params.width, self.params.length())
    return rooms
  }
} 