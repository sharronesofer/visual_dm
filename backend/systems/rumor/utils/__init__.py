"""
Rumor system utilities - Business Logic

This module contains utility functions for the rumor system business logic.
REFACTORING COMPLETED: Infrastructure dependencies have been moved to 
backend.infrastructure.systems.rumor where appropriate.
"""

# Import business logic utility modules
from . import decay_and_propagation
from . import npc_rumor_utils  
from . import truth_tracker

# Import the new rumor rules and configuration functions
from .rumor_rules import (
    get_rumor_constants,
    get_rumor_decay_rate,
    get_rumor_mutation_chance,
    get_rumor_spread_radius,
    get_rumor_believability_threshold,
    get_npc_rumor_behavior,
    get_rumor_config,
    reload_rumor_config,
    set_rumor_config_provider
)

__all__ = [
    'decay_and_propagation',
    'npc_rumor_utils', 
    'truth_tracker',
    # Rumor rules and configuration
    'get_rumor_constants',
    'get_rumor_decay_rate',
    'get_rumor_mutation_chance',
    'get_rumor_spread_radius', 
    'get_rumor_believability_threshold',
    'get_npc_rumor_behavior',
    'get_rumor_config',
    'reload_rumor_config',
    'set_rumor_config_provider'
]
