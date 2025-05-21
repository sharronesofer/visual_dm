"""
Loot system package.

This package provides a comprehensive system for managing item generation, shop and inventory
operations, location-based loot distribution, and loot history analytics.
"""

from .models import (
    LootBase,
    BaseItem,
    RarityTier,
    Location,
    LocationType,
    Container,
    ContainerType,
    ContainerContent,
    Shop,
    ShopType,
    ShopInventory,
    LootHistory,
    LootSourceType,
    LootAnalytics,
    MetricType
)

__all__ = [
    # Base
    "LootBase",
    # Item
    "BaseItem",
    "RarityTier",
    # Location
    "Location",
    "LocationType",
    "Container",
    "ContainerType",
    "ContainerContent",
    # Shop
    "Shop",
    "ShopType",
    "ShopInventory",
    # History
    "LootHistory",
    "LootSourceType",
    "LootAnalytics",
    "MetricType"
] 