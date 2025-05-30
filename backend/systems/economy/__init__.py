"""
Economy system module.

This module provides a centralized economy system for managing resources,
trade routes, and markets, as well as shop-related functionality. The main API
is exposed through the EconomyManager which should be accessed as a singleton
via EconomyManager.get_instance().

The shop functionality is integrated with the EconomyManager for consistent
pricing, inventory management, and economic calculations.
"""

from .economy_manager import EconomyManager
from .shop_routes import shop_bp

__all__ = ['EconomyManager', 'shop_bp']
