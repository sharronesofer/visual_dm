"""Dialogue system - Business logic only

Infrastructure components (models, repositories, utils, cache_service, ai_service, 
monitoring_service, security_service, validation_service) have been moved to:
- backend.infrastructure.dialogue_models
- backend.infrastructure.dialogue_repositories  
- backend.infrastructure.dialogue_utils
- backend.infrastructure.dialogue_services

This module now contains only business logic:
- Core dialogue orchestration and management
- Integration with other business systems
- Conversation flow and state management
"""

# Core business logic imports
from . import conversation

# Integration modules (business logic) - imported conditionally to avoid circular dependencies
try:
    from . import services
    from . import dialogue_system_new
    from . import dialogue_manager
    from . import memory_integration
    from . import rumor_integration  
    from . import motif_integration
    from . import faction_integration
    from . import population_integration
    from . import world_state_integration
    from . import time_integration
    from . import poi_integration
    from . import quest_integration
    from . import region_integration
    from . import war_integration
    from . import relationship_integration
    
    __all__ = [
        'dialogue_system_new',
        'dialogue_manager', 
        'conversation',
        'services',
        'memory_integration',
        'rumor_integration', 
        'motif_integration',
        'faction_integration',
        'population_integration',
        'world_state_integration',
        'time_integration',
        'poi_integration',
        'quest_integration',
        'region_integration',
        'war_integration',
        'relationship_integration'
    ]
except ImportError as e:
    # Fallback for when other systems have import issues
    __all__ = [
        'conversation'
    ]

