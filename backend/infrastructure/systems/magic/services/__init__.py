"""
Magic System Infrastructure Services

This module provides infrastructure adapters and utility services for the magic system.
The actual business logic is in backend.systems.magic.services.
"""

# Re-export canonical business services for infrastructure use
from backend.systems.magic.services import (
    MagicBusinessService,
    MagicCombatBusinessService,
    create_magic_business_service,
    create_magic_combat_service
)

# Infrastructure-specific utilities can be added here as needed
__all__ = [
    'MagicBusinessService',
    'MagicCombatBusinessService', 
    'create_magic_business_service',
    'create_magic_combat_service'
]
