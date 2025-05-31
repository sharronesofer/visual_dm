"""
Region System Schemas

This module provides validation schemas for the region system.
"""

# Import schemas from models for backward compatibility
# Use relative import to avoid circular dependency
from ..models import (
    HexCoordinateSchema,
    CoordinateSchema,
    CreateRegionRequest,
    UpdateRegionRequest,
    RegionResponse,
    RegionListResponse
)

__all__ = [
    'HexCoordinateSchema',
    'CoordinateSchema', 
    'CreateRegionRequest',
    'UpdateRegionRequest',
    'RegionResponse',
    'RegionListResponse'
]

