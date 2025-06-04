"""
Temporary compatibility imports for crafting-to-repair migration.

This file provides imports that maintain API compatibility during the transition.
Remove this file after migration is complete.
"""

import warnings

# Import the compatibility service
from backend.systems.repair.compat.crafting_bridge import (
    CraftingCompatibilityService,
    create_crafting_compatibility_service
)

# Create aliases for common crafting classes (for backwards compatibility)
CraftingService = CraftingCompatibilityService

warnings.warn(
    "Using compatibility crafting imports. Please migrate to repair system.",
    DeprecationWarning,
    stacklevel=2
)
