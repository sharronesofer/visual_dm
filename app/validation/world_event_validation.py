"""World event validation module."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from jsonschema import validate, ValidationError

# Event type schemas
WAR_EVENT_SCHEMA = {
    'type': 'object',
    'required': ['aggressor_id', 'defender_id'],
    'properties': {
        'aggressor_id': {'type': 'integer'},
        'defender_id': {'type': 'integer'},
        'initial_demands': {
            'type': 'object',
            'properties': {
                'territory': {'type': 'boolean'},
                'resources': {'type': 'boolean'},
                'vassalization': {'type': 'boolean'}
            }
        }
    }
}

TRADE_EVENT_SCHEMA = {
    'type': 'object',
    'required': ['region1_id', 'region2_id', 'terms'],
    'properties': {
        'region1_id': {'type': 'integer'},
        'region2_id': {'type': 'integer'},
        'terms': {
            'type': 'object',
            'required': ['resource_exchanges'],
            'properties': {
                'resource_exchanges': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'required': ['resource1', 'resource2'],
                        'properties': {
                            'resource1': {'type': 'string'},
                            'resource2': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
}

DIPLOMATIC_EVENT_SCHEMA = {
    'type': 'object',
    'required': ['faction1_id', 'faction2_id', 'crisis_type'],
    'properties': {
        'faction1_id': {'type': 'integer'},
        'faction2_id': {'type': 'integer'},
        'crisis_type': {'type': 'string'},
        'severity': {'type': 'number', 'minimum': 0, 'maximum': 1},
        'resolution_options': {
            'type': 'array',
            'items': {'type': 'string'}
        }
    }
}

FESTIVAL_EVENT_SCHEMA = {
    'type': 'object',
    'required': ['participating_regions', 'bonuses'],
    'properties': {
        'participating_regions': {
            'type': 'array',
            'items': {'type': 'integer'}
        },
        'bonuses': {
            'type': 'object',
            'properties': {
                'prosperity': {'type': 'number'},
                'happiness': {'type': 'number'},
                'cultural_influence': {'type': 'number'}
            }
        },
        'special_events': {
            'type': 'array',
            'items': {'type': 'string'}
        }
    }
}

CALAMITY_EVENT_SCHEMA = {
    'type': 'object',
    'required': ['affected_regions', 'severity', 'effects'],
    'properties': {
        'affected_regions': {
            'type': 'array',
            'items': {'type': 'integer'}
        },
        'severity': {'type': 'number', 'minimum': 0, 'maximum': 1},
        'effects': {
            'type': 'object',
            'properties': {
                'population_impact': {'type': 'number'},
                'infrastructure_damage': {'type': 'number'},
                'resource_depletion': {'type': 'number'}
            }
        }
    }
}

DISCOVERY_EVENT_SCHEMA = {
    'type': 'object',
    'required': ['discoverer_faction_id', 'discovery_type'],
    'properties': {
        'discoverer_faction_id': {'type': 'integer'},
        'discovery_type': {'type': 'string'},
        'breakthrough_level': {'type': 'integer', 'minimum': 1, 'maximum': 5},
        'benefits': {
            'type': 'object',
            'properties': {
                'efficiency_boost': {'type': 'number'}
            }
        },
        'requirements': {
            'type': 'object',
            'properties': {
                'research_cost': {'type': 'number'}
            }
        },
        'spread_chance': {'type': 'number', 'minimum': 0, 'maximum': 1}
    }
}

RELIGIOUS_EVENT_SCHEMA = {
    'type': 'object',
    'required': ['affected_regions', 'event_type', 'intensity'],
    'properties': {
        'affected_regions': {
            'type': 'array',
            'items': {'type': 'integer'}
        },
        'event_type': {'type': 'string'},
        'intensity': {'type': 'number', 'minimum': 0, 'maximum': 1},
        'effects': {
            'type': 'object',
            'properties': {
                'social_stability': {'type': 'number'},
                'cultural_change': {'type': 'number'},
                'faction_relations': {'type': 'number'}
            }
        },
        'duration_modifiers': {
            'type': 'object',
            'properties': {
                'fervor': {'type': 'number'},
                'resistance': {'type': 'number'}
            }
        }
    }
}

# Schema mapping
EVENT_TYPE_SCHEMAS = {
    'war_declaration': WAR_EVENT_SCHEMA,
    'trade_agreement': TRADE_EVENT_SCHEMA,
    'diplomatic_crisis': DIPLOMATIC_EVENT_SCHEMA,
    'global_festival': FESTIVAL_EVENT_SCHEMA,
    'natural_calamity': CALAMITY_EVENT_SCHEMA,
    'technological_discovery': DISCOVERY_EVENT_SCHEMA,
    'religious_movement': RELIGIOUS_EVENT_SCHEMA
}

def validate_event_data(event_type: str, data: Dict[str, Any]) -> None:
    """Validate event data against its schema."""
    if event_type not in EVENT_TYPE_SCHEMAS:
        raise ValidationError(f"Unknown event type: {event_type}")
        
    validate(instance=data, schema=EVENT_TYPE_SCHEMAS[event_type])

def validate_event_timing(start_time: datetime, end_time: Optional[datetime]) -> None:
    """Validate event timing."""
    if end_time and start_time >= end_time:
        raise ValidationError("Event end time must be after start time")

def validate_event_status(status: str) -> None:
    """Validate event status."""
    valid_statuses = {'active', 'completed', 'cancelled'}
    if status not in valid_statuses:
        raise ValidationError(f"Invalid status: {status}. Must be one of: {valid_statuses}")

def validate_affected_entities(event_type: str, data: Dict[str, Any], existing_entities: Dict[str, List[int]]) -> None:
    """Validate that referenced entities exist."""
    if event_type == 'war_declaration':
        _validate_factions([data['aggressor_id'], data['defender_id']], existing_entities['factions'])
    elif event_type == 'trade_agreement':
        _validate_regions([data['region1_id'], data['region2_id']], existing_entities['regions'])
    elif event_type == 'diplomatic_crisis':
        _validate_factions([data['faction1_id'], data['faction2_id']], existing_entities['factions'])
    elif event_type == 'global_festival':
        _validate_regions(data['participating_regions'], existing_entities['regions'])
    elif event_type == 'natural_calamity':
        _validate_regions(data['affected_regions'], existing_entities['regions'])
    elif event_type == 'technological_discovery':
        _validate_factions([data['discoverer_faction_id']], existing_entities['factions'])
    elif event_type == 'religious_movement':
        _validate_regions(data['affected_regions'], existing_entities['regions'])

def _validate_factions(faction_ids: List[int], existing_factions: List[int]) -> None:
    """Validate that factions exist."""
    invalid_factions = set(faction_ids) - set(existing_factions)
    if invalid_factions:
        raise ValidationError(f"Invalid faction IDs: {invalid_factions}")

def _validate_regions(region_ids: List[int], existing_regions: List[int]) -> None:
    """Validate that regions exist."""
    invalid_regions = set(region_ids) - set(existing_regions)
    if invalid_regions:
        raise ValidationError(f"Invalid region IDs: {invalid_regions}")

def validate_event_creation(
    event_type: str,
    data: Dict[str, Any],
    start_time: datetime,
    end_time: Optional[datetime],
    status: str,
    existing_entities: Dict[str, List[int]]
) -> None:
    """Validate all aspects of event creation."""
    try:
        validate_event_data(event_type, data)
        validate_event_timing(start_time, end_time)
        validate_event_status(status)
        validate_affected_entities(event_type, data, existing_entities)
    except ValidationError as e:
        raise ValidationError(f"Event validation failed: {str(e)}")

def validate_event_update(
    event_type: str,
    old_data: Dict[str, Any],
    new_data: Dict[str, Any],
    existing_entities: Dict[str, List[int]]
) -> None:
    """Validate event data updates."""
    # Merge old and new data
    merged_data = {**old_data, **new_data}
    
    try:
        validate_event_data(event_type, merged_data)
        validate_affected_entities(event_type, merged_data, existing_entities)
    except ValidationError as e:
        raise ValidationError(f"Event update validation failed: {str(e)}")

def validate_event_completion(event_type: str, data: Dict[str, Any]) -> None:
    """Validate that an event can be completed."""
    if event_type == 'war_declaration' and 'outcome' not in data:
        raise ValidationError("War events require an outcome to be completed")
    elif event_type == 'diplomatic_crisis' and 'resolution' not in data:
        raise ValidationError("Diplomatic crises require a resolution to be completed") 