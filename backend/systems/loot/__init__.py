"""
Loot system for Visual DM.

This module provides comprehensive loot generation, item management, shop systems,
and economic mechanics for the Visual DM game system.

Main Components:
- LootManager: Central coordinator for all loot operations
- Config System: JSON-driven configuration for rarities, shops, and environments
- Shared Functions: Common utilities used across the system
- Event Integration: Publishes loot-related events to the game event system
"""

# Core management
from .services.loot_manager import LootBusinessManager
# Backwards compatibility alias
LootManager = LootBusinessManager

# Configuration system
from .utils.config_loader import (
    config_loader,
    get_rarity_chances,
    get_rarity_multipliers,
    get_shop_config,
    get_biome_effects,
    get_motif_effects,
    get_economic_factors
)

# Shared utilities
from .utils.shared_functions import (
    group_equipment_by_type,
    gpt_name_and_flavor,
    merge_loot_sets,
    apply_biome_to_loot_table,
    get_current_supply,
    get_current_demand,
    apply_economic_factors_to_price
)

# Core business logic functions
from .utils.loot_core import (
    validate_item,
    calculate_item_power_score,
    generate_item_identity,
    generate_loot_bundle,
    generate_location_specific_loot,
    get_event_dispatcher
)

# Shop utilities
from .utils.loot_shop import (
    generate_shop_inventory,
    get_dynamic_item_price
)

# Service layer
from .services.services import (
    LootBusinessService,
    LootData,
    CreateLootData,
    UpdateLootData
)

# Version info
__version__ = "2.0.0"
__author__ = "Visual DM Team"

# Export list for clarity
__all__ = [
    # Core classes
    "LootManager",
    "LootBusinessService",
    "LootData",
    "CreateLootData",
    "UpdateLootData",
    
    # Configuration functions
    "config_loader",
    "get_rarity_chances",
    "get_rarity_multipliers", 
    "get_shop_config",
    "get_biome_effects",
    "get_motif_effects",
    "get_economic_factors",
    
    # Shared utilities
    "group_equipment_by_type",
    "gpt_name_and_flavor",
    "merge_loot_sets",
    "apply_biome_to_loot_table",
    
    # Core functions
    "validate_item",
    "calculate_item_power_score",
    "generate_item_identity",
    "generate_loot_bundle",
    "generate_location_specific_loot",
    "get_event_dispatcher",
    
    # Shop functions
    "generate_shop_inventory",
    "get_dynamic_item_price",
    "get_current_supply",
    "get_current_demand",
    "apply_economic_factors_to_price",
    
    # Metadata
    "__version__",
    "__author__"
]
