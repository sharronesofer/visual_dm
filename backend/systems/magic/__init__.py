"""
Magic System Module

This module provides a comprehensive MP-based magic system integrated with 
the combat and character systems. Features include:

- MP-based spellcasting with domain specializations
- JSON-configurable spells, domains, and combat rules
- Concentration mechanics integrated with combat
- AC/DR bypass rules based on spell schools
- Save system integration

Key Components:
- MagicBusinessService: Core business logic service
- MagicCombatBusinessService: Combat integration service
- SpellEffect: Data structure for spell results
- ActiveConcentration: Concentration effect tracking

Usage:
    from backend.systems.magic import create_magic_system, create_magic_combat_service
    
    # Create business services with dependency injection
    magic_service = create_magic_system()
    combat_service = create_magic_combat_service(magic_service)
    
    # Check if a spell can be cast
    can_cast = magic_service.can_cast_spell("fireball", "arcane", current_mp=20)
    
    # Cast a spell with full combat integration
    result = combat_service.attempt_spell_cast(
        caster_id="player_1",
        spell_name="fireball", 
        domain="arcane",
        target_id="enemy_1",
        abilities=character_abilities,
        current_mp=20,
        proficiency_bonus=3
    )
"""

# Business logic services
from .services import (
    MagicBusinessService,
    MagicCombatBusinessService,
    SpellEffect,
    ConcentrationCheck,
    SaveType,
    ActiveConcentration,
    SpellCastingResult,
    TimeProvider,
    create_magic_business_service,
    create_magic_combat_service
)

# Factory functions for complete setup
from backend.infrastructure.data_loaders.magic_config import (
    create_magic_config_repository,
    create_damage_type_service
)
from backend.infrastructure.utils.time_provider import create_system_time_provider


def create_magic_system() -> MagicBusinessService:
    """Factory function to create a complete magic business service with all dependencies"""
    config_repository = create_magic_config_repository()
    damage_type_service = create_damage_type_service()
    return create_magic_business_service(config_repository, damage_type_service)


def create_complete_magic_combat_service() -> MagicCombatBusinessService:
    """Factory function to create a complete magic combat service with all dependencies"""
    magic_service = create_magic_system()
    time_provider = create_system_time_provider()
    return create_magic_combat_service(magic_service, time_provider)


# Convenience instances for backward compatibility
magic_system = create_magic_system()
magic_combat_integration = create_complete_magic_combat_service()


# Make the primary interfaces easily accessible
__all__ = [
    # Factory functions
    "create_magic_system",
    "create_complete_magic_combat_service",
    
    # Convenience instances
    "magic_system",
    "magic_combat_integration",
    
    # Main classes
    "MagicBusinessService",
    "MagicCombatBusinessService",
    
    # Data structures
    "SpellEffect",
    "SpellCastingResult", 
    "ActiveConcentration",
    "ConcentrationCheck",
    
    # Enums and protocols
    "SaveType",
    "TimeProvider"
]
