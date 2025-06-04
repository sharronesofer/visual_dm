"""
Tension System - War and Conflict Management

This module provides the tension/war system for managing conflict and unrest
in regions and points of interest according to Development Bible standards.

Architecture:
- Pure business logic services with protocol-based dependency injection
- Domain models for tension state and configuration
- Event-driven tension updates with proper data validation
- Repository pattern for persistence abstraction
"""

# Domain Models
from backend.systems.tension.models.tension_state import (
    TensionState,
    TensionModifier,
    TensionConfig,
    ConflictTrigger,
    RevoltConfig,
    CalculationConstants
)

# Event Models and Enums
from backend.systems.tension.models.tension_events import (
    TensionEvent,
    TensionEventType
)

# Business Service
from backend.systems.tension.services.tension_business_service import (
    TensionBusinessService,
    TensionConfigRepository,
    TensionRepository,
    FactionService,
    EventDispatcher,
    create_tension_business_service
)

# Service Facade (renamed from UnifiedTensionManager per user clarification)
from backend.systems.tension.services.tension_service import TensionService

# Event Factories
from backend.systems.tension.services.event_factories import (
    create_player_combat_event,
    create_npc_death_event,
    create_environmental_disaster_event,
    create_political_change_event,
    create_festival_event
)

# Legacy alias for backward compatibility (to be deprecated)
UnifiedTensionManager = TensionService

__all__ = [
    # Domain Models
    'TensionState',
    'TensionModifier', 
    'TensionConfig',
    'ConflictTrigger',
    'RevoltConfig',
    'CalculationConstants',
    
    # Event Models
    'TensionEvent',
    'TensionEventType',
    
    # Business Service and Protocols
    'TensionBusinessService',
    'TensionConfigRepository',
    'TensionRepository',
    'FactionService',
    'EventDispatcher',
    'create_tension_business_service',
    
    # Service Facade
    'TensionService',
    'UnifiedTensionManager',  # Legacy alias
    
    # Event Factories
    'create_player_combat_event',
    'create_npc_death_event', 
    'create_environmental_disaster_event',
    'create_political_change_event',
    'create_festival_event'
] 