"""
Combat system module for Visual DM.

This module provides a turn-based combat system with effects, combatants, and state management.
The combat system uses FastAPI for API endpoints and Pydantic for schema validation.

Core components:
- Models: Define data structures for combat statistics
- Schemas: Define API request/response formats
- Services: Implement combat business logic
- Repositories: Handle data storage and retrieval
- Routers: Define API endpoints for combat operations
"""

# Visual DM Combat System
#
# This package manages combat encounters, mechanics, state, and persistence.
# It implements a turn-based system with actions, status effects, and AI-driven opponents.

# Import the core classes
from backend.systems.combat.combat_class import Combatant
from backend.systems.combat.combat_state_class import CombatState
from backend.systems.combat.combat_handler_class import CombatAction

# Import the utility modules
from backend.systems.combat.combat_utils import (
    roll_d20, roll_initiative, resolve_saving_throw,
    initiate_combat, resolve_combat_action,
    get_active_combat, end_combat
)

# Import status effect utilities
from backend.systems.combat.status_effects_utils import (
    apply_status_effect, tick_status_effects, 
    resolve_status_effects, remove_status_effect
)

# Import specialized combat effect utilities
from backend.systems.combat.combat_effects_utils import (
    apply_fumble, apply_critical_hit_effect, apply_area_effect
)

# Import combat narrative utilities
from backend.systems.combat.combat_narrative_utils import (
    narrate_action, generate_combat_summary, log_combat_event
)

# Import encounter generation utilities
from backend.systems.combat.combat_encounter_utils import (
    generate_scaled_encounter, get_encounter_difficulty, 
    balance_encounter
)

# Import Firebase utilities
from backend.systems.combat.combat_state_firebase_utils import (
    start_firebase_combat, CombatActionHandler,
    sync_post_combat_state_to_firebase, update_combatant_state
)

# Import routers
from backend.systems.combat.routers import combat_router

# Import repositories
from backend.systems.combat.repositories import CombatRepository, combat_repository

# Import services
from backend.systems.combat.services import CombatService, combat_service

# Expose combat RAM storage
from backend.systems.combat.combat_ram import ACTIVE_BATTLES

__all__ = [
    # Classes
    "Combatant", "CombatState", "CombatAction",
    
    # Core utilities
    "roll_d20", "roll_initiative", "resolve_saving_throw",
    "initiate_combat", "resolve_combat_action",
    "get_active_combat", "end_combat",
    
    # Status effects
    "apply_status_effect", "tick_status_effects", 
    "resolve_status_effects", "remove_status_effect",
    
    # Combat effects
    "apply_fumble", "apply_critical_hit_effect", "apply_area_effect",
    
    # Narrative
    "narrate_action", "generate_combat_summary", "log_combat_event",
    
    # Encounter generation
    "generate_scaled_encounter", "get_encounter_difficulty", "balance_encounter",
    
    # Firebase
    "start_firebase_combat", "CombatActionHandler",
    "sync_post_combat_state_to_firebase", "update_combatant_state",
    
    # API
    "combat_router",
    
    # Infrastructure
    "CombatRepository", "combat_repository",
    "CombatService", "combat_service",
    
    # Storage
    "ACTIVE_BATTLES"
]
