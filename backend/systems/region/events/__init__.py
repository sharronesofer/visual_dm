"""Events for region system"""

from .region_events import *

__all__ = [
    # Event enums
    "RegionEventType", "ContinentEventType",
    
    # Base classes
    "RegionEvent",
    
    # Core CRUD events
    "RegionCreatedEvent", "RegionUpdatedEvent", "RegionDeletedEvent",
    
    # Territory control events
    "TerritoryClaimedEvent", "TerritoryReleasedEvent", "TerritoryContestedEvent",
    
    # Population events
    "PopulationChangedEvent", "SettlementCreatedEvent", "SettlementDestroyedEvent",
    
    # Exploration events
    "RegionDiscoveredEvent", "RegionExploredEvent",
    
    # Resource events
    "ResourceDiscoveredEvent", "ResourceDepletedEvent", "ResourceExtractedEvent",
    
    # POI events
    "POICreatedEvent", "POIUpdatedEvent", "POIDiscoveredEvent",
    
    # Environmental events
    "BiomeChangedEvent", "ClimateChangedEvent", "DangerLevelChangedEvent",
    
    # World generation events
    "ContinentGeneratedEvent", "WorldGeneratedEvent",
    
    # Character location events
    "CharacterLocationChangedEvent", "CharacterEnteredRegionEvent", "CharacterLeftRegionEvent",
    
    # Quest location events
    "QuestLocationValidatedEvent", "QuestRegionCompletedEvent",
    
    # Utility functions
    "create_region_created_event", "create_territory_claimed_event", "create_character_location_event"
]

