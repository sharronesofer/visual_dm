"""
Tension and War Management System

This module manages faction relationships, tension calculation, war declaration, and war outcome simulation.
The system tracks and decays tension values between factions from -100 (alliance) to +100 (war/hostile).

Key components include:
- TensionManager: Manages all tension between factions, including calculation, updates, and decay
- WarManager: Manages war declaration, simulation, and outcomes
- TensionUtils: Utility functions for region tension operations
- WarUtils: Utility functions for war-related operations

This system integrates with:
- Faction system via tension tracking and war status
- Region system via controlled territory and border checks
- Events system by generating and handling war/tension related events
"""

# Export models
from .models import (
    TensionConfig,
    TensionLevel,
    WarConfig, 
    WarOutcome,
    WarOutcomeType,
    WarState
)

# Export service classes
from .services import TensionManager, WarManager

# Export utility functions
from .utils import (
    calculate_border_tension,
    calculate_event_tension,
    calculate_disputed_regions,
    calculate_war_chances,
    evaluate_battle_outcome,
    calculate_resource_changes
)

# Export API router
from .router import router as tension_war_router

# Export examples for learning
from .examples import tension_system_example, war_system_example

__all__ = [
    # Models
    'TensionConfig',
    'TensionLevel',
    'WarConfig',
    'WarOutcome',
    'WarOutcomeType',
    'WarState',
    
    # Service classes
    'TensionManager',
    'WarManager',
    
    # Utility functions
    'calculate_border_tension',
    'calculate_event_tension',
    'calculate_disputed_regions',
    'calculate_war_chances',
    'evaluate_battle_outcome',
    'calculate_resource_changes',
    
    # Router
    'tension_war_router',
    
    # Examples
    'tension_system_example',
    'war_system_example'
]
