"""
Region System Events - Pure Business Domain

Business domain event types for region system integration with other game systems.
These events enable cross-system communication for:
- Region creation, updates, and deletion
- Faction territory control changes
- Character location tracking
- Quest location validation
- Resource and POI management
- World generation events

Technical event serialization and dispatching moved to infrastructure layer.
"""

from enum import Enum
from typing import Dict, Any, Optional, List, Union
from uuid import UUID
from datetime import datetime

from backend.systems.region.models import (
    RegionType, BiomeType, ClimateType, DangerLevel, HexCoordinate, RegionMetadata
)


# ============================================================================
# BUSINESS DOMAIN EVENT DATA STRUCTURES
# ============================================================================

class RegionEventData:
    """Business domain structure for region events"""
    def __init__(self,
                 event_type: str,
                 timestamp: Optional[datetime] = None,
                 **event_data):
        self.event_type = event_type
        self.timestamp = timestamp or datetime.utcnow()
        self.event_data = event_data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            **self.event_data
        }


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
# BUSINESS EVENT CREATION FUNCTIONS
# ============================================================================

def create_region_created_event(
    region_id: UUID,
    region_name: str,
    region_type: str,
    dominant_biome: str,
    climate: str,
    danger_level: int,
    coordinates: List[HexCoordinate],
    area_square_km: float,
    continent_id: Optional[UUID] = None,
    created_by: Optional[str] = None
) -> RegionEventData:
    """Create a region created event with business validation"""
    return RegionEventData(
        event_type=RegionEventType.REGION_CREATED.value,
        region_id=str(region_id),
        region_name=region_name,
        region_type=region_type,
        dominant_biome=dominant_biome,
        climate=climate,
        danger_level=danger_level,
        coordinates=[coord.to_dict() for coord in coordinates],
        area_square_km=area_square_km,
        continent_id=str(continent_id) if continent_id else None,
        created_by=created_by
    )


def create_region_updated_event(
    region_id: UUID,
    region_name: str,
    changed_fields: Dict[str, Any],
    old_values: Dict[str, Any],
    new_values: Dict[str, Any],
    continent_id: Optional[UUID] = None,
    updated_by: Optional[str] = None
) -> RegionEventData:
    """Create a region updated event with business validation"""
    return RegionEventData(
        event_type=RegionEventType.REGION_UPDATED.value,
        region_id=str(region_id),
        region_name=region_name,
        changed_fields=changed_fields,
        old_values=old_values,
        new_values=new_values,
        continent_id=str(continent_id) if continent_id else None,
        updated_by=updated_by
    )


def create_region_deleted_event(
    region_id: UUID,
    region_name: str,
    continent_id: Optional[UUID] = None,
    deleted_by: Optional[str] = None,
    backup_data: Optional[Dict[str, Any]] = None
) -> RegionEventData:
    """Create a region deleted event with business validation"""
    return RegionEventData(
        event_type=RegionEventType.REGION_DELETED.value,
        region_id=str(region_id),
        region_name=region_name,
        continent_id=str(continent_id) if continent_id else None,
        deleted_by=deleted_by,
        backup_data=backup_data
    )


def create_territory_claimed_event(
    region_id: UUID,
    region_name: str,
    faction_id: UUID,
    faction_name: str,
    previous_controller: Optional[UUID] = None,
    control_strength: float = 1.0,
    claim_method: str = "conquest",
    continent_id: Optional[UUID] = None,
    claim_details: Optional[Dict[str, Any]] = None
) -> RegionEventData:
    """Create a territory claimed event with business validation"""
    # Business rule: Validate control strength
    if not 0.0 <= control_strength <= 1.0:
        raise ValueError(f"Control strength must be between 0.0 and 1.0, got: {control_strength}")
    
    # Business rule: Validate claim method
    valid_methods = ["conquest", "diplomacy", "purchase", "inheritance", "discovery"]
    if claim_method not in valid_methods:
        raise ValueError(f"Invalid claim method: {claim_method}. Must be one of: {valid_methods}")
    
    return RegionEventData(
        event_type=RegionEventType.TERRITORY_CLAIMED.value,
        region_id=str(region_id),
        region_name=region_name,
        faction_id=str(faction_id),
        faction_name=faction_name,
        previous_controller=str(previous_controller) if previous_controller else None,
        control_strength=control_strength,
        claim_method=claim_method,
        continent_id=str(continent_id) if continent_id else None,
        claim_details=claim_details
    )


def create_territory_released_event(
    region_id: UUID,
    region_name: str,
    faction_id: UUID,
    faction_name: str,
    release_reason: str = "voluntary",
    new_controller: Optional[UUID] = None,
    continent_id: Optional[UUID] = None
) -> RegionEventData:
    """Create a territory released event with business validation"""
    # Business rule: Validate release reason
    valid_reasons = ["voluntary", "conquest", "collapse", "diplomatic", "economic"]
    if release_reason not in valid_reasons:
        raise ValueError(f"Invalid release reason: {release_reason}. Must be one of: {valid_reasons}")
    
    return RegionEventData(
        event_type=RegionEventType.TERRITORY_RELEASED.value,
        region_id=str(region_id),
        region_name=region_name,
        faction_id=str(faction_id),
        faction_name=faction_name,
        release_reason=release_reason,
        new_controller=str(new_controller) if new_controller else None,
        continent_id=str(continent_id) if continent_id else None
    )


def create_population_changed_event(
    region_id: UUID,
    region_name: str,
    old_population: int,
    new_population: int,
    change_reason: str = "natural",
    continent_id: Optional[UUID] = None,
    affected_demographics: Optional[Dict[str, Any]] = None
) -> RegionEventData:
    """Create a population changed event with business validation"""
    # Business rule: Validate population values
    if old_population < 0 or new_population < 0:
        raise ValueError("Population values cannot be negative")
    
    # Business rule: Validate change reason
    valid_reasons = ["natural", "migration", "war", "plague", "economic", "disaster"]
    if change_reason not in valid_reasons:
        raise ValueError(f"Invalid change reason: {change_reason}. Must be one of: {valid_reasons}")
    
    return RegionEventData(
        event_type=RegionEventType.POPULATION_CHANGED.value,
        region_id=str(region_id),
        region_name=region_name,
        old_population=old_population,
        new_population=new_population,
        population_change=new_population - old_population,
        change_reason=change_reason,
        continent_id=str(continent_id) if continent_id else None,
        affected_demographics=affected_demographics
    )


def create_resource_discovered_event(
    region_id: UUID,
    region_name: str,
    resource_type: str,
    location: HexCoordinate,
    abundance: float,
    quality: float,
    continent_id: Optional[UUID] = None,
    discovered_by: Optional[str] = None
) -> RegionEventData:
    """Create a resource discovered event with business validation"""
    # Business rule: Validate abundance and quality
    if not 0.0 <= abundance <= 1.0:
        raise ValueError(f"Abundance must be between 0.0 and 1.0, got: {abundance}")
    if not 0.0 <= quality <= 1.0:
        raise ValueError(f"Quality must be between 0.0 and 1.0, got: {quality}")
    
    return RegionEventData(
        event_type=RegionEventType.RESOURCE_DISCOVERED.value,
        region_id=str(region_id),
        region_name=region_name,
        resource_type=resource_type,
        location=location.to_dict(),
        abundance=abundance,
        quality=quality,
        continent_id=str(continent_id) if continent_id else None,
        discovered_by=discovered_by
    )


def create_poi_created_event(
    region_id: UUID,
    region_name: str,
    poi_id: UUID,
    poi_name: str,
    poi_type: str,
    location: HexCoordinate,
    importance_level: int = 1,
    continent_id: Optional[UUID] = None,
    created_by: Optional[str] = None
) -> RegionEventData:
    """Create a POI created event with business validation"""
    # Business rule: Validate importance level
    if not 1 <= importance_level <= 10:
        raise ValueError(f"Importance level must be between 1 and 10, got: {importance_level}")
    
    return RegionEventData(
        event_type=RegionEventType.POI_CREATED.value,
        region_id=str(region_id),
        region_name=region_name,
        poi_id=str(poi_id),
        poi_name=poi_name,
        poi_type=poi_type,
        location=location.to_dict(),
        importance_level=importance_level,
        continent_id=str(continent_id) if continent_id else None,
        created_by=created_by
    )


def create_character_location_event(
    character_id: UUID,
    character_name: str,
    old_region_id: Optional[UUID],
    new_region_id: Optional[UUID],
    old_location: Optional[HexCoordinate] = None,
    new_location: Optional[HexCoordinate] = None,
    movement_method: str = "walking",
    travel_time: Optional[float] = None
) -> RegionEventData:
    """Create a character location changed event with business validation"""
    # Business rule: Validate movement method
    valid_methods = ["walking", "riding", "flying", "teleport", "sailing", "fast_travel"]
    if movement_method not in valid_methods:
        raise ValueError(f"Invalid movement method: {movement_method}. Must be one of: {valid_methods}")
    
    # Business rule: Validate travel time
    if travel_time is not None and travel_time < 0:
        raise ValueError("Travel time cannot be negative")
    
    return RegionEventData(
        event_type="character.location_changed",
        character_id=str(character_id),
        character_name=character_name,
        old_region_id=str(old_region_id) if old_region_id else None,
        new_region_id=str(new_region_id) if new_region_id else None,
        old_location=old_location.to_dict() if old_location else None,
        new_location=new_location.to_dict() if new_location else None,
        movement_method=movement_method,
        travel_time=travel_time
    )


def create_biome_changed_event(
    region_id: UUID,
    region_name: str,
    old_biome: str,
    new_biome: str,
    change_cause: str = "natural",
    change_speed: str = "gradual",
    affected_area_percent: float = 100.0,
    continent_id: Optional[UUID] = None
) -> RegionEventData:
    """Create a biome changed event with business validation"""
    # Business rule: Validate change speed
    valid_speeds = ["gradual", "sudden", "instant"]
    if change_speed not in valid_speeds:
        raise ValueError(f"Invalid change speed: {change_speed}. Must be one of: {valid_speeds}")
    
    # Business rule: Validate affected area percentage
    if not 0.0 <= affected_area_percent <= 100.0:
        raise ValueError(f"Affected area percent must be between 0.0 and 100.0, got: {affected_area_percent}")
    
    return RegionEventData(
        event_type=RegionEventType.BIOME_CHANGED.value,
        region_id=str(region_id),
        region_name=region_name,
        old_biome=old_biome,
        new_biome=new_biome,
        change_cause=change_cause,
        change_speed=change_speed,
        affected_area_percent=affected_area_percent,
        continent_id=str(continent_id) if continent_id else None
    )


def create_continent_generated_event(
    continent_id: UUID,
    continent_name: str,
    region_count: int,
    total_area_square_km: float,
    generation_seed: Optional[int] = None,
    generation_parameters: Optional[Dict[str, Any]] = None,
    generated_by: Optional[str] = None
) -> RegionEventData:
    """Create a continent generated event with business validation"""
    # Business rule: Validate region count and area
    if region_count < 0:
        raise ValueError("Region count cannot be negative")
    if total_area_square_km < 0:
        raise ValueError("Total area cannot be negative")
    
    return RegionEventData(
        event_type=ContinentEventType.CONTINENT_CREATED.value,
        continent_id=str(continent_id),
        continent_name=continent_name,
        region_count=region_count,
        total_area_square_km=total_area_square_km,
        generation_seed=generation_seed,
        generation_parameters=generation_parameters,
        generated_by=generated_by
    )


# ============================================================================
# BUSINESS VALIDATION FUNCTIONS
# ============================================================================

def validate_event_type(event_type: str) -> bool:
    """Validate if an event type is supported"""
    all_event_types = [e.value for e in RegionEventType] + [e.value for e in ContinentEventType]
    all_event_types.extend(["character.location_changed", "character.entered_region", "character.left_region"])
    return event_type in all_event_types


def validate_region_event_data(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate region event data according to business rules"""
    validated_data = event_data.copy()
    
    # Business rule: Required fields for region events
    if 'region_id' in validated_data:
        try:
            UUID(str(validated_data['region_id']))
        except ValueError:
            raise ValueError(f"Invalid region_id format: {validated_data['region_id']}")
    
    # Business rule: Validate numeric ranges
    if 'danger_level' in validated_data:
        danger_level = validated_data['danger_level']
        if not 1 <= danger_level <= 10:
            raise ValueError(f"Danger level must be between 1 and 10, got: {danger_level}")
    
    if 'population' in validated_data:
        population = validated_data['population']
        if population < 0:
            raise ValueError("Population cannot be negative")
    
    return validated_data


def get_valid_event_types() -> List[str]:
    """Get list of all valid event types"""
    event_types = [e.value for e in RegionEventType] + [e.value for e in ContinentEventType]
    event_types.extend(["character.location_changed", "character.entered_region", "character.left_region"])
    return sorted(event_types)


# ============================================================================
# BUSINESS UTILITY FUNCTIONS
# ============================================================================

def calculate_event_priority(event_type: str, event_data: Dict[str, Any]) -> str:
    """Calculate event priority based on business rules"""
    # Business rule: Critical events
    critical_events = [
        RegionEventType.REGION_DELETED.value,
        RegionEventType.TERRITORY_CONTESTED.value,
        "character.location_changed"
    ]
    
    # Business rule: High priority events
    high_priority_events = [
        RegionEventType.REGION_CREATED.value,
        RegionEventType.TERRITORY_CLAIMED.value,
        RegionEventType.TERRITORY_RELEASED.value,
        RegionEventType.DANGER_LEVEL_CHANGED.value
    ]
    
    if event_type in critical_events:
        return "critical"
    elif event_type in high_priority_events:
        return "high"
    elif event_type.startswith("resource.") or event_type.startswith("poi."):
        return "normal"
    else:
        return "low"


def should_broadcast_event(event_type: str, event_data: Dict[str, Any]) -> bool:
    """Determine if an event should be broadcast to other systems"""
    # Business rule: Always broadcast critical system events
    broadcast_events = [
        RegionEventType.REGION_CREATED.value,
        RegionEventType.REGION_DELETED.value,
        RegionEventType.TERRITORY_CLAIMED.value,
        RegionEventType.TERRITORY_RELEASED.value,
        "character.location_changed"
    ]
    
    return event_type in broadcast_events


__all__ = [
    # Event data structures
    "RegionEventData",
    
    # Event type enums
    "RegionEventType",
    "ContinentEventType",
    
    # Event creation functions
    "create_region_created_event",
    "create_region_updated_event",
    "create_region_deleted_event",
    "create_territory_claimed_event",
    "create_territory_released_event",
    "create_population_changed_event",
    "create_resource_discovered_event",
    "create_poi_created_event",
    "create_character_location_event",
    "create_biome_changed_event",
    "create_continent_generated_event",
    
    # Validation functions
    "validate_event_type",
    "validate_region_event_data",
    "get_valid_event_types",
    
    # Utility functions
    "calculate_event_priority",
    "should_broadcast_event"
] 