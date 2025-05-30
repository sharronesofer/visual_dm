"""
Population Control System

This module implements the Population Control System as described in the Visual DM Development Bible.
It manages NPC generation and population thresholds for all Points of Interest (POIs),
implementing dynamic birth rate adjustment, soft/hard caps, and integration with POI state transitions.
"""

from backend.systems.population.models import (
    POIType,
    POIState,
    POIPopulation,
    PopulationConfig,
    PopulationChangedEvent as ModelPopulationChangedEvent,
    PopulationChangeRequest,
    GlobalMultiplierRequest,
    BaseRateRequest
)

from backend.systems.population.service import PopulationService, population_service
from backend.systems.population.router import router as population_router
from backend.systems.population.events import (
    PopulationEventType,
    PopulationEventBase,
    PopulationChangedEventData,
    PopulationStateChangedEventData,
    PopulationCatastropheEventData,
    PopulationWarImpactEventData,
    # Backward compatibility aliases
    PopulationEvent,
    PopulationChangedEvent,
    PopulationStateChangedEvent,
    PopulationCatastropheEvent,
    PopulationWarImpactEvent
)
from backend.systems.population.utils import (
    calculate_growth_rate,
    calculate_next_state,
    estimate_population_timeline,
    calculate_target_population
)

__all__ = [
    # Models
    'POIType',
    'POIState',
    'POIPopulation',
    'PopulationConfig',
    'ModelPopulationChangedEvent',
    'PopulationChangeRequest',
    'GlobalMultiplierRequest',
    'BaseRateRequest',
    
    # Service
    'PopulationService',
    'population_service',
    
    # Router
    'population_router',
    
    # Events
    'PopulationEventType',
    'PopulationEventBase',
    'PopulationChangedEventData',
    'PopulationStateChangedEventData',
    'PopulationCatastropheEventData',
    'PopulationWarImpactEventData',
    # Backward compatibility
    'PopulationEvent',
    'PopulationChangedEvent',
    'PopulationStateChangedEvent',
    'PopulationCatastropheEvent',
    'PopulationWarImpactEvent',
    
    # Utils
    'calculate_growth_rate',
    'calculate_next_state',
    'estimate_population_timeline',
    'calculate_target_population'
]
