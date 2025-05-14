"""
Region management module.
Handles region-related functionality including tension, factions, and world state.
"""

from app.regions.tension_utils import (
    decay_region_tension,
    check_faction_war_triggers
)

__all__ = [
    'decay_region_tension',
    'check_faction_war_triggers'
] 