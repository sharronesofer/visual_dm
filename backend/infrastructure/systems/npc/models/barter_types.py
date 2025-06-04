"""
Shared types for NPC bartering system.

This module contains shared enums and classes used across the barter system
to avoid circular imports between services.
"""

from enum import Enum
from typing import Optional


class ItemTier(Enum):
    """Item availability tiers for bartering"""
    ALWAYS_AVAILABLE = "always_available"
    HIGH_PRICE_RELATIONSHIP = "high_price_relationship"
    NEVER_AVAILABLE = "never_available"


class BarterValidationResult:
    """Result of barter validation with details"""
    
    def __init__(self, allowed: bool, reason: str = "", tier: Optional[ItemTier] = None):
        self.allowed = allowed
        self.reason = reason
        self.tier = tier 