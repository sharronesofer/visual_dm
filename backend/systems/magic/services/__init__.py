"""
Magic System Services

This module provides business logic services for the magic system.
All services here contain pure business logic without technical dependencies.
"""

from .magic_business_service import (
    MagicBusinessService,
    SpellEffect,
    ConcentrationCheck,
    SaveType,
    MagicConfigRepository,
    DamageTypeService,
    create_magic_business_service
)

from .magic_combat_service import (
    MagicCombatBusinessService,
    ActiveConcentration,
    SpellCastingResult,
    TimeProvider,
    create_magic_combat_service
)

__all__ = [
    # Core business service
    "MagicBusinessService",
    "SpellEffect", 
    "ConcentrationCheck",
    "SaveType",
    "MagicConfigRepository",
    "DamageTypeService",
    "create_magic_business_service",
    
    # Combat integration service
    "MagicCombatBusinessService",
    "ActiveConcentration",
    "SpellCastingResult", 
    "TimeProvider",
    "create_magic_combat_service"
] 