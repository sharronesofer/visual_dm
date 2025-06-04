"""
Tension Event Factory Functions

Provides convenient factory functions for creating common tension events
following Development Bible patterns.
"""

from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, Optional

from backend.systems.tension.models.tension_events import TensionEvent, TensionEventType


# Combat Event Factories
def create_player_combat_event(
    region_id: str,
    poi_id: str,
    lethal: bool = False,
    stealth: bool = False,
    enemies_defeated: int = 1,
    difficulty: str = "normal",
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a player combat event."""
    return TensionEvent(
        event_type=TensionEventType.PLAYER_COMBAT,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'lethal': lethal,
            'stealth': stealth,
            'enemies_defeated': enemies_defeated,
            'difficulty': difficulty
        },
        event_id=str(uuid4()),
        description=f"Player combat: {'lethal' if lethal else 'non-lethal'}, {enemies_defeated} enemies"
    )


def create_faction_warfare_event(
    region_id: str,
    poi_id: str,
    attacking_faction: str,
    defending_faction: str,
    casualties: int = 0,
    victor: Optional[str] = None,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a faction warfare event."""
    return TensionEvent(
        event_type=TensionEventType.FACTION_WARFARE,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'attacking_faction': attacking_faction,
            'defending_faction': defending_faction,
            'casualties': casualties,
            'victor': victor
        },
        event_id=str(uuid4()),
        severity=1.5,
        description=f"Warfare between {attacking_faction} and {defending_faction}"
    )


def create_assassination_event(
    region_id: str,
    poi_id: str,
    target_importance: str = "minor",  # minor, important, major
    successful: bool = True,
    perpetrator_known: bool = False,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create an assassination event."""
    severity_map = {"minor": 1.0, "important": 1.5, "major": 2.0}
    return TensionEvent(
        event_type=TensionEventType.ASSASSINATION,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'target_importance': target_importance,
            'successful': successful,
            'perpetrator_known': perpetrator_known
        },
        event_id=str(uuid4()),
        severity=severity_map.get(target_importance, 1.0),
        description=f"{'Successful' if successful else 'Failed'} assassination of {target_importance} target"
    )


# Death and Violence Event Factories
def create_npc_death_event(
    region_id: str,
    poi_id: str,
    important: bool = False,
    civilian: bool = True,
    cause: str = "unknown",
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create an NPC death event."""
    return TensionEvent(
        event_type=TensionEventType.NPC_DEATH,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'important': important,
            'civilian': civilian,
            'cause': cause
        },
        event_id=str(uuid4()),
        severity=1.5 if important else 1.0,
        description=f"Death of {'important ' if important else ''}{'civilian' if civilian else 'combatant'}"
    )


def create_mass_casualties_event(
    region_id: str,
    poi_id: str,
    casualty_count: int,
    cause: str = "disaster",
    civilian_casualties: int = 0,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a mass casualties event."""
    severity = min(3.0, 1.0 + (casualty_count / 10))  # Scale with casualties
    return TensionEvent(
        event_type=TensionEventType.MASS_CASUALTIES,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'casualty_count': casualty_count,
            'cause': cause,
            'civilian_casualties': civilian_casualties
        },
        event_id=str(uuid4()),
        severity=severity,
        description=f"Mass casualties: {casualty_count} victims from {cause}"
    )


def create_execution_event(
    region_id: str,
    poi_id: str,
    public: bool = True,
    crime: str = "treason",
    victim_status: str = "criminal",
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create an execution event."""
    return TensionEvent(
        event_type=TensionEventType.EXECUTION,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'public': public,
            'crime': crime,
            'victim_status': victim_status
        },
        event_id=str(uuid4()),
        severity=1.3 if public else 1.0,
        description=f"{'Public' if public else 'Private'} execution for {crime}"
    )


# Environmental Event Factories
def create_environmental_disaster_event(
    region_id: str,
    poi_id: str,
    disaster_type: str = "storm",
    severity: float = 1.0,
    casualties: int = 0,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create an environmental disaster event."""
    return TensionEvent(
        event_type=TensionEventType.ENVIRONMENTAL_DISASTER,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'disaster_type': disaster_type,
            'casualties': casualties,
            'infrastructure_damage': severity > 1.5
        },
        event_id=str(uuid4()),
        severity=severity,
        description=f"{disaster_type.title()} disaster (severity: {severity})"
    )


def create_plague_outbreak_event(
    region_id: str,
    poi_id: str,
    disease_name: str = "unknown plague",
    infection_rate: float = 0.1,
    mortality_rate: float = 0.05,
    containment_level: str = "none",
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a plague outbreak event."""
    severity = 1.0 + (infection_rate * 2) + (mortality_rate * 5)
    return TensionEvent(
        event_type=TensionEventType.PLAGUE_OUTBREAK,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'disease_name': disease_name,
            'infection_rate': infection_rate,
            'mortality_rate': mortality_rate,
            'containment_level': containment_level
        },
        event_id=str(uuid4()),
        severity=min(3.0, severity),
        duration_hours=168,  # Plagues last for weeks
        description=f"Outbreak of {disease_name}"
    )


def create_famine_event(
    region_id: str,
    poi_id: str,
    cause: str = "crop failure",
    severity_level: str = "moderate",
    duration_months: int = 3,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a famine event."""
    severity_map = {"mild": 1.2, "moderate": 1.8, "severe": 2.5, "extreme": 3.0}
    return TensionEvent(
        event_type=TensionEventType.FAMINE,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'cause': cause,
            'severity_level': severity_level,
            'duration_months': duration_months
        },
        event_id=str(uuid4()),
        severity=severity_map.get(severity_level, 1.5),
        duration_hours=duration_months * 730,  # Convert months to hours
        description=f"{severity_level.title()} famine due to {cause}"
    )


# Political Event Factories
def create_regime_change_event(
    region_id: str,
    poi_id: str,
    old_regime: str,
    new_regime: str,
    violent_transition: bool = False,
    popular_support: float = 0.5,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a regime change event."""
    severity = 2.0 if violent_transition else 1.5
    if popular_support < 0.3:
        severity += 0.5
    
    return TensionEvent(
        event_type=TensionEventType.REGIME_CHANGE,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'old_regime': old_regime,
            'new_regime': new_regime,
            'violent_transition': violent_transition,
            'popular_support': popular_support
        },
        event_id=str(uuid4()),
        severity=severity,
        description=f"Regime change: {old_regime} → {new_regime}"
    )


def create_rebellion_event(
    region_id: str,
    poi_id: str,
    rebel_faction: str,
    cause: str = "oppression",
    size: str = "small",
    success_likelihood: float = 0.2,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a rebellion event."""
    size_severity = {"small": 1.2, "medium": 1.8, "large": 2.5, "massive": 3.0}
    return TensionEvent(
        event_type=TensionEventType.REBELLION,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'rebel_faction': rebel_faction,
            'cause': cause,
            'size': size,
            'success_likelihood': success_likelihood
        },
        event_id=str(uuid4()),
        severity=size_severity.get(size, 1.5),
        duration_hours=72,
        description=f"{size.title()} rebellion by {rebel_faction} against {cause}"
    )


def create_corruption_exposed_event(
    region_id: str,
    poi_id: str,
    official_name: str,
    corruption_type: str = "bribery",
    public_outrage: float = 0.7,
    consequences_expected: bool = True,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a corruption exposure event."""
    return TensionEvent(
        event_type=TensionEventType.CORRUPTION_EXPOSED,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'official_name': official_name,
            'corruption_type': corruption_type,
            'public_outrage': public_outrage,
            'consequences_expected': consequences_expected
        },
        event_id=str(uuid4()),
        severity=1.0 + public_outrage,
        description=f"Corruption exposed: {official_name} accused of {corruption_type}"
    )


# Economic Event Factories
def create_economic_crisis_event(
    region_id: str,
    poi_id: str,
    crisis_type: str = "recession",
    unemployment_rise: float = 0.1,
    business_failures: int = 5,
    government_response: str = "none",
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create an economic crisis event."""
    severity = 1.5 + (unemployment_rise * 5) + (business_failures / 10)
    return TensionEvent(
        event_type=TensionEventType.ECONOMIC_CRISIS,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'crisis_type': crisis_type,
            'unemployment_rise': unemployment_rise,
            'business_failures': business_failures,
            'government_response': government_response
        },
        event_id=str(uuid4()),
        severity=min(3.0, severity),
        duration_hours=720,  # Economic crises last for months
        description=f"Economic {crisis_type} with {unemployment_rise*100:.1f}% unemployment rise"
    )


def create_trade_embargo_event(
    region_id: str,
    poi_id: str,
    embargoing_nation: str,
    goods_affected: list,
    expected_duration: str = "indefinite",
    economic_impact: float = 0.3,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a trade embargo event."""
    return TensionEvent(
        event_type=TensionEventType.TRADE_EMBARGO,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'embargoing_nation': embargoing_nation,
            'goods_affected': goods_affected,
            'expected_duration': expected_duration,
            'economic_impact': economic_impact
        },
        event_id=str(uuid4()),
        severity=1.0 + economic_impact,
        duration_hours=2160,  # Default 3 months
        description=f"Trade embargo by {embargoing_nation} affecting {len(goods_affected)} goods"
    )


# Social Event Factories
def create_festival_event(
    region_id: str,
    poi_id: str,
    festival_name: str = "Harvest Festival",
    success_level: float = 1.0,
    attendance: str = "high",
    duration_days: int = 3,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a festival event (reduces tension)."""
    return TensionEvent(
        event_type=TensionEventType.FESTIVAL,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'festival_name': festival_name,
            'success_level': success_level,
            'attendance': attendance,
            'duration_days': duration_days
        },
        event_id=str(uuid4()),
        severity=success_level,  # Higher success = more tension reduction
        duration_hours=duration_days * 24,
        description=f"{festival_name} with {attendance} attendance"
    )


def create_riot_event(
    region_id: str,
    poi_id: str,
    trigger_cause: str = "injustice",
    intensity: str = "moderate",
    casualties: int = 0,
    property_damage: bool = True,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a riot event."""
    intensity_severity = {"minor": 1.2, "moderate": 1.8, "severe": 2.5, "extreme": 3.0}
    return TensionEvent(
        event_type=TensionEventType.RIOT,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'trigger_cause': trigger_cause,
            'intensity': intensity,
            'casualties': casualties,
            'property_damage': property_damage
        },
        event_id=str(uuid4()),
        severity=intensity_severity.get(intensity, 1.5),
        duration_hours=12,
        description=f"{intensity.title()} riot triggered by {trigger_cause}"
    )


def create_protest_event(
    region_id: str,
    poi_id: str,
    cause: str = "government policy",
    size: str = "medium",
    peaceful: bool = True,
    demands: list = None,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a protest event."""
    size_impact = {"small": 0.5, "medium": 1.0, "large": 1.5, "massive": 2.0}
    severity = size_impact.get(size, 1.0)
    if not peaceful:
        severity *= 1.5
    
    return TensionEvent(
        event_type=TensionEventType.PROTEST,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'cause': cause,
            'size': size,
            'peaceful': peaceful,
            'demands': demands or []
        },
        event_id=str(uuid4()),
        severity=severity,
        duration_hours=8,
        description=f"{size.title()} {'peaceful' if peaceful else 'violent'} protest about {cause}"
    )


# Criminal Event Factories
def create_organized_crime_event(
    region_id: str,
    poi_id: str,
    crime_type: str = "racketeering",
    organization: str = "unknown gang",
    law_enforcement_response: str = "investigating",
    public_awareness: float = 0.3,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create an organized crime event."""
    return TensionEvent(
        event_type=TensionEventType.ORGANIZED_CRIME,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'crime_type': crime_type,
            'organization': organization,
            'law_enforcement_response': law_enforcement_response,
            'public_awareness': public_awareness
        },
        event_id=str(uuid4()),
        severity=1.0 + public_awareness,
        description=f"{crime_type.title()} by {organization}"
    )


def create_kidnapping_event(
    region_id: str,
    poi_id: str,
    victim_status: str = "citizen",
    ransom_demanded: bool = True,
    victim_found: Optional[bool] = None,
    perpetrator_known: bool = False,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a kidnapping event."""
    status_severity = {"citizen": 1.0, "merchant": 1.3, "noble": 1.8, "official": 2.0}
    severity = status_severity.get(victim_status, 1.0)
    if victim_found is False:  # Victim found dead
        severity *= 1.5
    
    return TensionEvent(
        event_type=TensionEventType.KIDNAPPING,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'victim_status': victim_status,
            'ransom_demanded': ransom_demanded,
            'victim_found': victim_found,
            'perpetrator_known': perpetrator_known
        },
        event_id=str(uuid4()),
        severity=severity,
        description=f"Kidnapping of {victim_status}"
    )


# Religious Event Factories
def create_religious_conflict_event(
    region_id: str,
    poi_id: str,
    faith_1: str,
    faith_2: str,
    conflict_type: str = "theological dispute",
    violence_level: str = "none",
    casualties: int = 0,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a religious conflict event."""
    violence_severity = {"none": 1.0, "minor": 1.3, "moderate": 1.8, "severe": 2.5}
    return TensionEvent(
        event_type=TensionEventType.RELIGIOUS_CONFLICT,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'faith_1': faith_1,
            'faith_2': faith_2,
            'conflict_type': conflict_type,
            'violence_level': violence_level,
            'casualties': casualties
        },
        event_id=str(uuid4()),
        severity=violence_severity.get(violence_level, 1.0),
        description=f"Religious conflict: {faith_1} vs {faith_2} over {conflict_type}"
    )


def create_heresy_event(
    region_id: str,
    poi_id: str,
    accused_name: str,
    heretical_teaching: str,
    church_response: str = "investigation",
    public_support: float = 0.1,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a heresy accusation event."""
    return TensionEvent(
        event_type=TensionEventType.HERESY,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'accused_name': accused_name,
            'heretical_teaching': heretical_teaching,
            'church_response': church_response,
            'public_support': public_support
        },
        event_id=str(uuid4()),
        severity=1.2 + public_support,
        description=f"Heresy accusation against {accused_name} for {heretical_teaching}"
    )


def create_temple_desecration_event(
    region_id: str,
    poi_id: str,
    temple_deity: str,
    damage_level: str = "minor",
    perpetrator_known: bool = False,
    motive: str = "unknown",
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a temple desecration event."""
    damage_severity = {"minor": 1.2, "moderate": 1.5, "severe": 2.0, "complete": 2.5}
    return TensionEvent(
        event_type=TensionEventType.TEMPLE_DESECRATION,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'temple_deity': temple_deity,
            'damage_level': damage_level,
            'perpetrator_known': perpetrator_known,
            'motive': motive
        },
        event_id=str(uuid4()),
        severity=damage_severity.get(damage_level, 1.5),
        description=f"{damage_level.title()} desecration of {temple_deity} temple"
    )


# Magical Event Factories
def create_magical_accident_event(
    region_id: str,
    poi_id: str,
    accident_type: str = "spell misfire",
    caster_experience: str = "novice",
    casualties: int = 0,
    magical_contamination: bool = False,
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a magical accident event."""
    experience_modifier = {"novice": 1.5, "apprentice": 1.2, "journeyman": 1.0, "master": 0.8}
    severity = experience_modifier.get(caster_experience, 1.0)
    if magical_contamination:
        severity *= 1.5
    
    return TensionEvent(
        event_type=TensionEventType.MAGICAL_ACCIDENT,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'accident_type': accident_type,
            'caster_experience': caster_experience,
            'casualties': casualties,
            'magical_contamination': magical_contamination
        },
        event_id=str(uuid4()),
        severity=severity,
        description=f"Magical accident: {accident_type} by {caster_experience} caster"
    )


def create_planar_incursion_event(
    region_id: str,
    poi_id: str,
    plane_of_origin: str = "unknown plane",
    incursion_size: str = "minor",
    entities_involved: list = None,
    containment_status: str = "uncontained",
    timestamp: Optional[datetime] = None
) -> TensionEvent:
    """Create a planar incursion event."""
    size_severity = {"minor": 1.5, "moderate": 2.0, "major": 2.5, "catastrophic": 3.0}
    return TensionEvent(
        event_type=TensionEventType.PLANAR_INCURSION,
        region_id=region_id,
        poi_id=poi_id,
        timestamp=timestamp or datetime.utcnow(),
        data={
            'plane_of_origin': plane_of_origin,
            'incursion_size': incursion_size,
            'entities_involved': entities_involved or [],
            'containment_status': containment_status
        },
        event_id=str(uuid4()),
        severity=size_severity.get(incursion_size, 2.0),
        duration_hours=48,
        description=f"{incursion_size.title()} incursion from {plane_of_origin}"
    )


# Utility function for bulk event creation
def create_event_sequence(
    region_id: str,
    poi_id: str,
    event_types: list,
    base_timestamp: Optional[datetime] = None,
    time_intervals_hours: list = None
) -> list:
    """
    Create a sequence of related events.
    
    Args:
        event_types: List of tuples (event_factory_function, kwargs)
        time_intervals_hours: Hours between each event (defaults to 1 hour)
    """
    if base_timestamp is None:
        base_timestamp = datetime.utcnow()
    
    if time_intervals_hours is None:
        time_intervals_hours = [1] * (len(event_types) - 1)
    
    events = []
    current_time = base_timestamp
    
    for i, (factory_func, kwargs) in enumerate(event_types):
        # Add region_id and poi_id to kwargs
        kwargs.update({'region_id': region_id, 'poi_id': poi_id, 'timestamp': current_time})
        
        # Create the event
        event = factory_func(**kwargs)
        events.append(event)
        
        # Advance time for next event
        if i < len(time_intervals_hours):
            from datetime import timedelta
            current_time += timedelta(hours=time_intervals_hours[i])
    
    return events 