"""
Tension Event Factories

Convenience functions for creating tension events according to 
Development Bible standards and best practices.
"""

from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, Optional

from backend.systems.tension.models.tension_events import TensionEvent, TensionEventType


def create_player_combat_event(
    region_id: str,
    poi_id: str,
    lethal: bool = False,
    stealth: bool = False,
    enemies_defeated: int = 1,
    combat_duration_minutes: int = 5,
    timestamp: Optional[datetime] = None,
    **additional_data
) -> TensionEvent:
    """
    Create a player combat tension event
    
    Args:
        region_id: Region where combat occurred
        poi_id: Point of interest where combat occurred
        lethal: Whether the combat was lethal
        stealth: Whether stealth was used
        enemies_defeated: Number of enemies defeated
        combat_duration_minutes: How long the combat lasted
        timestamp: When the event occurred (defaults to now)
        **additional_data: Additional event-specific data
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    event_data = {
        'lethal': lethal,
        'stealth': stealth,
        'enemies_defeated': enemies_defeated,
        'combat_duration_minutes': combat_duration_minutes,
        **additional_data
    }
    
    return TensionEvent(
        event_type=TensionEventType.PLAYER_COMBAT,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp,
        data=event_data,
        event_id=str(uuid4())
    )


def create_npc_death_event(
    region_id: str,
    poi_id: str,
    important: bool = False,
    civilian: bool = True,
    cause_of_death: str = "unknown",
    npc_name: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    **additional_data
) -> TensionEvent:
    """
    Create an NPC death tension event
    
    Args:
        region_id: Region where death occurred
        poi_id: Point of interest where death occurred
        important: Whether the NPC was important/notable
        civilian: Whether the NPC was a civilian
        cause_of_death: How the NPC died
        npc_name: Name of the deceased NPC
        timestamp: When the event occurred (defaults to now)
        **additional_data: Additional event-specific data
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    event_data = {
        'important': important,
        'civilian': civilian,
        'cause_of_death': cause_of_death,
        'npc_name': npc_name,
        **additional_data
    }
    
    return TensionEvent(
        event_type=TensionEventType.NPC_DEATH,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp,
        data=event_data,
        event_id=str(uuid4())
    )


def create_environmental_disaster_event(
    region_id: str,
    poi_id: str,
    disaster_type: str = "natural",
    severity: float = 1.0,
    casualties: int = 0,
    damage_description: str = "",
    timestamp: Optional[datetime] = None,
    **additional_data
) -> TensionEvent:
    """
    Create an environmental disaster tension event
    
    Args:
        region_id: Region where disaster occurred
        poi_id: Point of interest affected
        disaster_type: Type of disaster (earthquake, flood, fire, etc.)
        severity: Severity multiplier (0.5 = minor, 1.0 = normal, 2.0 = major)
        casualties: Number of casualties from the disaster
        damage_description: Description of damage caused
        timestamp: When the event occurred (defaults to now)
        **additional_data: Additional event-specific data
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    event_data = {
        'disaster_type': disaster_type,
        'severity': severity,
        'casualties': casualties,
        'damage_description': damage_description,
        **additional_data
    }
    
    return TensionEvent(
        event_type=TensionEventType.ENVIRONMENTAL_DISASTER,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp,
        data=event_data,
        event_id=str(uuid4())
    )


def create_political_change_event(
    region_id: str,
    poi_id: str,
    change_type: str = "leadership",
    regime_change: bool = False,
    popular_support: float = 0.5,
    change_description: str = "",
    timestamp: Optional[datetime] = None,
    **additional_data
) -> TensionEvent:
    """
    Create a political change tension event
    
    Args:
        region_id: Region where political change occurred
        poi_id: Point of interest affected
        change_type: Type of change (leadership, policy, regime, etc.)
        regime_change: Whether this was a complete regime change
        popular_support: Popular support for the change (0.0 to 1.0)
        change_description: Description of the political change
        timestamp: When the event occurred (defaults to now)
        **additional_data: Additional event-specific data
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    event_data = {
        'change_type': change_type,
        'regime_change': regime_change,
        'popular_support': popular_support,
        'change_description': change_description,
        **additional_data
    }
    
    return TensionEvent(
        event_type=TensionEventType.POLITICAL_CHANGE,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp,
        data=event_data,
        event_id=str(uuid4())
    )


def create_festival_event(
    region_id: str,
    poi_id: str,
    festival_name: str = "Local Festival",
    duration_hours: float = 24.0,
    attendance: int = 100,
    success_level: float = 1.0,
    timestamp: Optional[datetime] = None,
    **additional_data
) -> TensionEvent:
    """
    Create a festival tension event (typically reduces tension)
    
    Args:
        region_id: Region where festival occurred
        poi_id: Point of interest where festival was held
        festival_name: Name of the festival
        duration_hours: How long the festival lasts
        attendance: Number of attendees
        success_level: How successful the festival was (0.5 = poor, 1.0 = normal, 2.0 = amazing)
        timestamp: When the event occurred (defaults to now)
        **additional_data: Additional event-specific data
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    event_data = {
        'festival_name': festival_name,
        'duration_hours': duration_hours,
        'attendance': attendance,
        'success_level': success_level,
        **additional_data
    }
    
    return TensionEvent(
        event_type=TensionEventType.FESTIVAL,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp,
        data=event_data,
        event_id=str(uuid4())
    )


def create_economic_change_event(
    region_id: str,
    poi_id: str,
    change_type: str = "trade",
    economic_impact: float = 0.0,
    affected_population: int = 100,
    change_description: str = "",
    timestamp: Optional[datetime] = None,
    **additional_data
) -> TensionEvent:
    """
    Create an economic change tension event
    
    Args:
        region_id: Region where economic change occurred
        poi_id: Point of interest affected
        change_type: Type of economic change (trade, employment, taxation, etc.)
        economic_impact: Economic impact (-1.0 = very negative, 0.0 = neutral, 1.0 = very positive)
        affected_population: Number of people affected
        change_description: Description of the economic change
        timestamp: When the event occurred (defaults to now)
        **additional_data: Additional event-specific data
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    event_data = {
        'change_type': change_type,
        'economic_impact': economic_impact,
        'affected_population': affected_population,
        'change_description': change_description,
        **additional_data
    }
    
    return TensionEvent(
        event_type=TensionEventType.ECONOMIC_CHANGE,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp,
        data=event_data,
        event_id=str(uuid4())
    )


def create_magical_event(
    region_id: str,
    poi_id: str,
    magic_type: str = "arcane",
    intensity: float = 1.0,
    beneficial: bool = False,
    event_description: str = "",
    timestamp: Optional[datetime] = None,
    **additional_data
) -> TensionEvent:
    """
    Create a magical event that affects tension
    
    Args:
        region_id: Region where magical event occurred
        poi_id: Point of interest affected
        magic_type: Type of magic (arcane, divine, primal, etc.)
        intensity: Intensity of the magical event
        beneficial: Whether the magic was beneficial or harmful
        event_description: Description of the magical event
        timestamp: When the event occurred (defaults to now)
        **additional_data: Additional event-specific data
    """
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    event_data = {
        'magic_type': magic_type,
        'intensity': intensity,
        'beneficial': beneficial,
        'event_description': event_description,
        **additional_data
    }
    
    return TensionEvent(
        event_type=TensionEventType.MAGICAL_EVENT,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp,
        data=event_data,
        event_id=str(uuid4())
    )


# Batch event creation helpers

def create_combat_sequence_events(
    region_id: str,
    poi_id: str,
    num_encounters: int = 3,
    encounter_spacing_minutes: int = 30,
    base_timestamp: Optional[datetime] = None
) -> list[TensionEvent]:
    """
    Create a sequence of combat events representing an extended battle
    
    Args:
        region_id: Region where combat occurred
        poi_id: Point of interest where combat occurred
        num_encounters: Number of individual combat encounters
        encounter_spacing_minutes: Time between encounters
        base_timestamp: Starting time (defaults to now)
    """
    if base_timestamp is None:
        base_timestamp = datetime.utcnow()
    
    events = []
    
    for i in range(num_encounters):
        event_time = base_timestamp.replace(
            minute=(base_timestamp.minute + i * encounter_spacing_minutes) % 60
        )
        
        # Scale up intensity over time
        lethal = i >= num_encounters // 2  # Later encounters more lethal
        enemies = min(1 + i, 5)  # More enemies in later encounters
        
        event = create_player_combat_event(
            region_id=region_id,
            poi_id=poi_id,
            lethal=lethal,
            enemies_defeated=enemies,
            timestamp=event_time,
            sequence_number=i + 1,
            total_in_sequence=num_encounters
        )
        
        events.append(event)
    
    return events 