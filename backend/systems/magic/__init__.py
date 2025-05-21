"""
Magic system for the visual DM.

This package contains the magic system for the visual DM,
including spells, magic abilities, effects, and spellbooks.
"""

from .models import (
    MagicModel, SpellModel, SpellEffect, 
    SpellSlot, SpellSchool, Spellbook, 
    SpellComponent
)
from .schemas import (
    MagicCreate, MagicResponse, MagicUpdate,
    SpellCreate, SpellResponse, SpellUpdate,
    SpellEffectCreate, SpellEffectResponse, SpellEffectUpdate,
    SpellSlotCreate, SpellSlotResponse, SpellSlotUpdate,
    SpellbookCreate, SpellbookResponse, SpellbookUpdate,
    MagicSchoolEnum
)
from .services import (
    MagicService, SpellService, 
    SpellbookService, SpellEffectService,
    SpellSlotService
)
from .repositories import (
    MagicRepository, SpellRepository,
    SpellEffectRepository, SpellbookRepository,
    SpellSlotRepository
)
from .utils import (
    calculate_spell_power, validate_spell_requirements,
    check_spell_compatibility, can_cast_spell,
    apply_spell_effect, calculate_spell_duration,
    generate_effect_description, check_spell_slot_availability,
    calculate_spell_difficulty, parse_spell_target_area,
    calculate_magic_learning_time, format_spell_duration
)
from .router import router

__all__ = [
    # Models
    'MagicModel', 'SpellModel', 'SpellEffect',
    'SpellSlot', 'SpellSchool', 'Spellbook',
    'SpellComponent',
    
    # Schemas
    'MagicCreate', 'MagicResponse', 'MagicUpdate',
    'SpellCreate', 'SpellResponse', 'SpellUpdate',
    'SpellEffectCreate', 'SpellEffectResponse', 'SpellEffectUpdate',
    'SpellSlotCreate', 'SpellSlotResponse', 'SpellSlotUpdate',
    'SpellbookCreate', 'SpellbookResponse', 'SpellbookUpdate',
    'MagicSchoolEnum',
    
    # Services
    'MagicService', 'SpellService',
    'SpellbookService', 'SpellEffectService',
    'SpellSlotService',
    
    # Repositories
    'MagicRepository', 'SpellRepository',
    'SpellEffectRepository', 'SpellbookRepository',
    'SpellSlotRepository',
    
    # Utilities
    'calculate_spell_power', 'validate_spell_requirements',
    'check_spell_compatibility', 'can_cast_spell',
    'apply_spell_effect', 'calculate_spell_duration',
    'generate_effect_description', 'check_spell_slot_availability',
    'calculate_spell_difficulty', 'parse_spell_target_area',
    'calculate_magic_learning_time', 'format_spell_duration',
    
    # Router
    'router'
]
