"""
Magic system repositories.

This module exports all repository classes for database operations related to the magic system.
"""

from .base import BaseRepository
from .magic_repository import MagicRepository
from .spell_repository import SpellRepository
from .spellbook_repository import SpellbookRepository
from .spell_effect_repository import SpellEffectRepository
from .spell_slot_repository import SpellSlotRepository

__all__ = [
    'BaseRepository', 
    'MagicRepository', 
    'SpellRepository', 
    'SpellbookRepository',
    'SpellEffectRepository', 
    'SpellSlotRepository'
] 