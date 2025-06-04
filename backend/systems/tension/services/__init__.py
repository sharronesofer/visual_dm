"""
Tension System Services

This module contains the service layer for the tension system following
Development Bible standards for business logic separation and protocols.
"""

from .tension_business_service import (
    TensionBusinessService,
    TensionConfigRepository,
    TensionRepository,
    FactionService,
    EventDispatcher,
    create_tension_business_service
)

from .tension_service import TensionService

from .event_factories import (
    create_player_combat_event,
    create_npc_death_event,
    create_environmental_disaster_event,
    create_political_change_event,
    create_festival_event
)

__all__ = [
    'TensionBusinessService',
    'TensionConfigRepository',
    'TensionRepository',
    'FactionService',
    'EventDispatcher',
    'create_tension_business_service',
    'TensionService',
    'create_player_combat_event',
    'create_npc_death_event',
    'create_environmental_disaster_event',
    'create_political_change_event',
    'create_festival_event'
] 