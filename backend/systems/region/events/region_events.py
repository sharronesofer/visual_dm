"""
Region System Events

Comprehensive event types for region system integration with other game systems.
These events enable real-time cross-system communication for:
- Region creation, updates, and deletion
- Faction territory control changes
- Character location tracking
- Quest location validation
- Resource and POI management
- World generation events
"""

from enum import Enum
from typing import Dict, Any, Optional, List, Union
from uuid import UUID
from datetime import datetime
import time
from pydantic import BaseModel, Field, ConfigDict

# Import EventBase directly to avoid circular imports
class EventBase(BaseModel):
    """Base class for all event types in the system."""
    event_type: str
    timestamp: float = Field(default_factory=time.time)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

from backend.systems.region.models import (
    RegionType, BiomeType, ClimateType, DangerLevel, HexCoordinate, RegionMetadata
)


# ============================================================================
# REGION EVENT TYPES
# ============================================================================

class RegionEventType(Enum):
    """Types of region events"""
    # Core CRUD events
    REGION_CREATED = "region.created"
    REGION_UPDATED = "region.updated"
    REGION_DELETED = "region.deleted"
    
    # Territory control events
    TERRITORY_CLAIMED = "territory.claimed"
    TERRITORY_RELEASED = "territory.released"
    TERRITORY_CONTESTED = "territory.contested"
    
    # Population events
    POPULATION_CHANGED = "population.changed"
    SETTLEMENT_CREATED = "settlement.created"
    SETTLEMENT_DESTROYED = "settlement.destroyed"
    
    # Exploration events
    REGION_DISCOVERED = "region.discovered"
    REGION_EXPLORED = "region.explored"
    
    # Resource events
    RESOURCE_DISCOVERED = "resource.discovered"
    RESOURCE_DEPLETED = "resource.depleted"
    RESOURCE_EXTRACTED = "resource.extracted"
    
    # POI events
    POI_CREATED = "poi.created"
    POI_UPDATED = "poi.updated"
    POI_DISCOVERED = "poi.discovered"
    
    # Environmental events
    BIOME_CHANGED = "biome.changed"
    CLIMATE_CHANGED = "climate.changed"
    DANGER_LEVEL_CHANGED = "danger.changed"
    
    # World generation events
    CONTINENT_GENERATED = "continent.generated"
    WORLD_GENERATED = "world.generated"


class ContinentEventType(Enum):
    """Types of continent events"""
    CONTINENT_CREATED = "continent.created"
    CONTINENT_UPDATED = "continent.updated"
    CONTINENT_DELETED = "continent.deleted"


# ============================================================================
# BASE REGION EVENT CLASSES
# ============================================================================

class RegionEvent(EventBase):
    """Base class for all region-related events"""
    event_type: str = "region.base"
    region_id: UUID
    region_name: str
    continent_id: Optional[UUID] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if not hasattr(self, 'event_type') or self.event_type == "region.base":
            # Set the event_type based on the class name if not explicitly set
            class_name = self.__class__.__name__
            if hasattr(RegionEventType, class_name.upper().replace('EVENT', '')):
                self.event_type = getattr(RegionEventType, class_name.upper().replace('EVENT', '')).value


# ============================================================================
# CORE CRUD EVENTS
# ============================================================================

class RegionCreatedEvent(RegionEvent):
    """Event fired when a new region is created"""
    event_type: str = RegionEventType.REGION_CREATED.value
    region_type: RegionType
    dominant_biome: BiomeType
    climate: ClimateType
    danger_level: DangerLevel
    coordinates: List[HexCoordinate]
    area_square_km: float
    created_by: Optional[str] = None  # User or system that created it
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class RegionUpdatedEvent(RegionEvent):
    """Event fired when a region is updated"""
    event_type: str = RegionEventType.REGION_UPDATED.value
    changed_fields: Dict[str, Any]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]
    updated_by: Optional[str] = None


class RegionDeletedEvent(RegionEvent):
    """Event fired when a region is deleted"""
    event_type: str = RegionEventType.REGION_DELETED.value
    deleted_by: Optional[str] = None
    backup_data: Optional[Dict[str, Any]] = None  # For potential restoration


# ============================================================================
# TERRITORY CONTROL EVENTS
# ============================================================================

class TerritoryClaimedEvent(RegionEvent):
    """Event fired when a faction claims territory in a region"""
    event_type: str = RegionEventType.TERRITORY_CLAIMED.value
    faction_id: UUID
    faction_name: str
    previous_controller: Optional[UUID] = None
    control_strength: float = 1.0  # 0.0 to 1.0
    claim_method: str = "conquest"  # conquest, diplomacy, purchase, etc.
    claim_details: Optional[Dict[str, Any]] = None


class TerritoryReleasedEvent(RegionEvent):
    """Event fired when a faction releases control of territory"""
    event_type: str = RegionEventType.TERRITORY_RELEASED.value
    faction_id: UUID
    faction_name: str
    release_reason: str = "voluntary"  # voluntary, conquest, collapse, etc.
    new_controller: Optional[UUID] = None


class TerritoryContestedEvent(RegionEvent):
    """Event fired when territory control is disputed"""
    event_type: str = RegionEventType.TERRITORY_CONTESTED.value
    contesting_factions: List[UUID]
    current_controller: Optional[UUID] = None
    contest_type: str = "military"  # military, diplomatic, economic
    contest_details: Optional[Dict[str, Any]] = None


# ============================================================================
# POPULATION EVENTS
# ============================================================================

class PopulationChangedEvent(RegionEvent):
    """Event fired when region population changes"""
    event_type: str = RegionEventType.POPULATION_CHANGED.value
    old_population: int
    new_population: int
    change_reason: str = "natural"  # natural, migration, war, plague, etc.
    affected_demographics: Optional[Dict[str, Any]] = None


class SettlementCreatedEvent(RegionEvent):
    """Event fired when a new settlement is established"""
    event_type: str = RegionEventType.SETTLEMENT_CREATED.value
    settlement_name: str
    settlement_type: str = "village"  # village, town, city, outpost
    location: HexCoordinate
    initial_population: int = 0
    founder_faction: Optional[UUID] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class SettlementDestroyedEvent(RegionEvent):
    """Event fired when a settlement is destroyed"""
    event_type: str = RegionEventType.SETTLEMENT_DESTROYED.value
    settlement_name: str
    destruction_cause: str = "unknown"  # war, disaster, abandonment
    survivors: int = 0
    refugee_destination: Optional[UUID] = None


# ============================================================================
# EXPLORATION EVENTS
# ============================================================================

class RegionDiscoveredEvent(RegionEvent):
    """Event fired when a region is first discovered"""
    event_type: str = RegionEventType.REGION_DISCOVERED.value
    discovered_by: Optional[str] = None  # Character or faction
    discovery_method: str = "exploration"  # exploration, map, divination
    previously_known: bool = False
    discovery_details: Optional[Dict[str, Any]] = None


class RegionExploredEvent(RegionEvent):
    """Event fired when a region exploration level increases"""
    event_type: str = RegionEventType.REGION_EXPLORED.value
    old_exploration_level: float
    new_exploration_level: float
    explored_by: Optional[str] = None
    discoveries_made: List[str] = []
    exploration_details: Optional[Dict[str, Any]] = None


# ============================================================================
# RESOURCE EVENTS
# ============================================================================

class ResourceDiscoveredEvent(RegionEvent):
    """Event fired when a new resource is discovered"""
    event_type: str = RegionEventType.RESOURCE_DISCOVERED.value
    resource_type: str
    location: HexCoordinate
    abundance: float  # 0.0 to 1.0
    quality: float    # 0.0 to 1.0
    discovered_by: Optional[str] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ResourceDepletedEvent(RegionEvent):
    """Event fired when a resource becomes depleted"""
    event_type: str = RegionEventType.RESOURCE_DEPLETED.value
    resource_type: str
    location: HexCoordinate
    depletion_cause: str = "extraction"  # extraction, disaster, time
    final_reserves: float = 0.0
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ResourceExtractedEvent(RegionEvent):
    """Event fired when resources are extracted"""
    event_type: str = RegionEventType.RESOURCE_EXTRACTED.value
    resource_type: str
    location: HexCoordinate
    amount_extracted: float
    extracted_by: Optional[str] = None  # Character or faction
    extraction_method: str = "manual"
    remaining_reserves: float
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


# ============================================================================
# POI EVENTS
# ============================================================================

class POICreatedEvent(RegionEvent):
    """Event fired when a new POI is created"""
    event_type: str = RegionEventType.POI_CREATED.value
    poi_id: UUID
    poi_name: str
    poi_type: str
    location: HexCoordinate
    importance_level: int = 1
    created_by: Optional[str] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class POIUpdatedEvent(RegionEvent):
    """Event fired when a POI is updated"""
    event_type: str = RegionEventType.POI_UPDATED.value
    poi_id: UUID
    poi_name: str
    changed_fields: Dict[str, Any]
    old_values: Dict[str, Any]
    new_values: Dict[str, Any]


class POIDiscoveredEvent(RegionEvent):
    """Event fired when a POI is discovered"""
    event_type: str = RegionEventType.POI_DISCOVERED.value
    poi_id: UUID
    poi_name: str
    poi_type: str
    location: HexCoordinate
    discovered_by: Optional[str] = None
    discovery_method: str = "exploration"
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


# ============================================================================
# ENVIRONMENTAL EVENTS
# ============================================================================

class BiomeChangedEvent(RegionEvent):
    """Event fired when a region's biome changes"""
    event_type: str = RegionEventType.BIOME_CHANGED.value
    old_biome: BiomeType
    new_biome: BiomeType
    change_cause: str = "natural"  # natural, magical, disaster
    change_speed: str = "gradual"  # gradual, sudden
    affected_area_percent: float = 100.0


class ClimateChangedEvent(RegionEvent):
    """Event fired when a region's climate changes"""
    event_type: str = RegionEventType.CLIMATE_CHANGED.value
    old_climate: ClimateType
    new_climate: ClimateType
    change_cause: str = "natural"
    temperature_delta: Optional[float] = None
    precipitation_delta: Optional[float] = None


class DangerLevelChangedEvent(RegionEvent):
    """Event fired when a region's danger level changes"""
    event_type: str = RegionEventType.DANGER_LEVEL_CHANGED.value
    old_danger_level: DangerLevel
    new_danger_level: DangerLevel
    change_cause: str = "unknown"  # monsters, war, magic, natural
    threat_details: Optional[Dict[str, Any]] = None


# ============================================================================
# WORLD GENERATION EVENTS
# ============================================================================

class ContinentGeneratedEvent(EventBase):
    """Event fired when a continent is procedurally generated"""
    event_type: str = ContinentEventType.CONTINENT_CREATED.value
    continent_id: UUID
    continent_name: str
    region_count: int
    total_area_square_km: float
    generation_seed: Optional[int] = None
    generation_parameters: Optional[Dict[str, Any]] = None
    generated_by: Optional[str] = None


class WorldGeneratedEvent(EventBase):
    """Event fired when an entire world is procedurally generated"""
    event_type: str = RegionEventType.WORLD_GENERATED.value
    continent_count: int
    total_region_count: int
    total_area_square_km: float
    generation_seed: Optional[int] = None
    generation_time_seconds: Optional[float] = None
    generation_statistics: Optional[Dict[str, Any]] = None
    generated_by: Optional[str] = None


# ============================================================================
# CHARACTER LOCATION EVENTS
# ============================================================================

class CharacterLocationChangedEvent(EventBase):
    """Event fired when a character moves between regions"""
    event_type: str = "character.location_changed"
    character_id: UUID
    character_name: str
    old_region_id: Optional[UUID] = None
    new_region_id: Optional[UUID] = None
    old_location: Optional[HexCoordinate] = None
    new_location: Optional[HexCoordinate] = None
    movement_method: str = "walking"  # walking, riding, teleport, etc.
    travel_time: Optional[float] = None  # Time in game minutes
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class CharacterEnteredRegionEvent(RegionEvent):
    """Event fired when a character enters a region"""
    event_type: str = "character.entered_region"
    character_id: UUID
    character_name: str
    entry_location: HexCoordinate
    entry_method: str = "walking"
    previous_region_id: Optional[UUID] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class CharacterLeftRegionEvent(RegionEvent):
    """Event fired when a character leaves a region"""
    event_type: str = "character.left_region"
    character_id: UUID
    character_name: str
    exit_location: HexCoordinate
    exit_method: str = "walking"
    destination_region_id: Optional[UUID] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


# ============================================================================
# QUEST LOCATION EVENTS
# ============================================================================

class QuestLocationValidatedEvent(RegionEvent):
    """Event fired when a quest location is validated"""
    event_type: str = "quest.location_validated"
    quest_id: UUID
    quest_name: str
    location: HexCoordinate
    validation_status: str = "valid"  # valid, invalid, moved
    validation_details: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


class QuestRegionCompletedEvent(RegionEvent):
    """Event fired when all quests in a region are completed"""
    event_type: str = "quest.region_completed"
    completed_quest_count: int
    total_reward_value: Optional[float] = None
    completion_details: Optional[Dict[str, Any]] = None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_region_created_event(region_metadata: RegionMetadata, created_by: Optional[str] = None) -> RegionCreatedEvent:
    """Create a RegionCreatedEvent from RegionMetadata"""
    return RegionCreatedEvent(
        region_id=region_metadata.id,
        region_name=region_metadata.name,
        continent_id=region_metadata.continent_id,
        region_type=region_metadata.region_type,
        dominant_biome=region_metadata.profile.dominant_biome,
        climate=region_metadata.profile.climate,
        danger_level=region_metadata.danger_level,
        coordinates=region_metadata.hex_coordinates,
        area_square_km=region_metadata.area_square_km,
        created_by=created_by
    )


def create_territory_claimed_event(
    region_metadata: RegionMetadata,
    faction_id: UUID,
    faction_name: str,
    previous_controller: Optional[UUID] = None,
    claim_method: str = "conquest"
) -> TerritoryClaimedEvent:
    """Create a TerritoryClaimedEvent"""
    return TerritoryClaimedEvent(
        region_id=region_metadata.id,
        region_name=region_metadata.name,
        continent_id=region_metadata.continent_id,
        faction_id=faction_id,
        faction_name=faction_name,
        previous_controller=previous_controller,
        claim_method=claim_method
    )


def create_character_location_event(
    character_id: UUID,
    character_name: str,
    old_region_id: Optional[UUID],
    new_region_id: Optional[UUID],
    old_location: Optional[HexCoordinate] = None,
    new_location: Optional[HexCoordinate] = None,
    movement_method: str = "walking"
) -> CharacterLocationChangedEvent:
    """Create a CharacterLocationChangedEvent"""
    return CharacterLocationChangedEvent(
        character_id=character_id,
        character_name=character_name,
        old_region_id=old_region_id,
        new_region_id=new_region_id,
        old_location=old_location,
        new_location=new_location,
        movement_method=movement_method
    )


# Export all event types
__all__ = [
    # Enums
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