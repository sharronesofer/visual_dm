from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required
from app.models.world_state import WorldState
from app.models.event import Event
from app.models.faction import Faction
from app.core.database import db

from app.api.schemas.world import WorldSchema
from app.api.schemas.event import EventSchema
from app.api.schemas.faction import FactionSchema

from app.core.validation.validators import (
    StringValidator, NumberValidator, DateTimeValidator, ListValidator
)
from app.core.validation.middleware import validate_json, validate_query_params
from app.core.validation.rate_limiter import rate_limit
from app.core.validation.transaction import transaction
from app.core.api.error_handling.exceptions import NotFoundError, ValidationError

# Define validation schemas
WORLD_VALIDATOR_SCHEMA = {
    'name': StringValidator('name', min_length=3, max_length=50),
    'description': StringValidator('description', required=False, max_length=500),
    'current_era': StringValidator('current_era', required=False, max_length=100),
    'global_tension': NumberValidator('global_tension', required=False, min_value=0, max_value=100, is_integer=True),
    'major_events': ListValidator('major_events', required=False, item_validator=NumberValidator('major_events[]', is_integer=True)),
    'kingdom_count': NumberValidator('kingdom_count', required=False, min_value=0, is_integer=True)
}

WORLD_TIME_VALIDATOR_SCHEMA = {
    'time': StringValidator('time')
}

WORLD_WEATHER_VALIDATOR_SCHEMA = {
    'weather': StringValidator('weather', min_length=3, max_length=50)
}

EVENT_VALIDATOR_SCHEMA = {
    'title': StringValidator('title', min_length=3, max_length=100),
    'description': StringValidator('description', required=False, max_length=1000),
    'event_type': StringValidator('event_type', required=False, max_length=50),
    'impact_level': NumberValidator('impact_level', required=False, min_value=1, max_value=10, is_integer=True)
}

FACTION_VALIDATOR_SCHEMA = {
    'name': StringValidator('name', min_length=3, max_length=100),
    'description': StringValidator('description', required=False, max_length=1000),
    'alignment': StringValidator('alignment', required=False, max_length=50),
    'power_level': NumberValidator('power_level', required=False, min_value=1, max_value=100, is_integer=True)
}

world_bp = Blueprint('world', __name__)

# --- Worlds CRUD ---
@world_bp.route('/worlds', methods=['GET'])
@jwt_required()
@rate_limit('world_list')
def list_worlds():
    worlds = WorldState.query.all()
    return jsonify(WorldSchema(many=True).dump(worlds)), 200

@world_bp.route('/worlds', methods=['POST'])
@jwt_required()
@validate_json(WORLD_VALIDATOR_SCHEMA)
@rate_limit('world_create')
@transaction('create_world')
def create_world():
    # Get validated data from request context
    data = g.validated_data
    
    # Create world
    world = WorldState(**data)
    db.session.add(world)
    
    # Return result
    return jsonify(WorldSchema().dump(world)), 201

@world_bp.route('/worlds/<int:world_id>', methods=['GET'])
@jwt_required()
@rate_limit('world_get')
def get_world(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    return jsonify(WorldSchema().dump(world)), 200

@world_bp.route('/worlds/<int:world_id>', methods=['PUT'])
@jwt_required()
@validate_json(WORLD_VALIDATOR_SCHEMA)
@rate_limit('world_update')
@transaction('update_world')
def update_world(world_id):
    # Get world
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    # Get validated data from request context
    data = g.validated_data
    
    # Update world
    for key, value in data.items():
        setattr(world, key, value)
    
    return jsonify(WorldSchema().dump(world)), 200

@world_bp.route('/worlds/<int:world_id>', methods=['DELETE'])
@jwt_required()
@rate_limit('world_delete')
@transaction('delete_world')
def delete_world(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    db.session.delete(world)
    
    return jsonify({'message': 'World deleted'}), 200

# --- World Time ---
@world_bp.route('/worlds/<int:world_id>/time', methods=['GET'])
@jwt_required()
@rate_limit('world_time_get')
def get_world_time(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    return jsonify({'time': world.last_major_shift.isoformat() if world.last_major_shift else None}), 200

@world_bp.route('/worlds/<int:world_id>/time', methods=['PUT'])
@jwt_required()
@validate_json(WORLD_TIME_VALIDATOR_SCHEMA)
@rate_limit('world_time_update')
@transaction('update_world_time')
def update_world_time(world_id):
    # Get world
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    # Get validated data from request context
    data = g.validated_data
    time_str = data['time']
    
    # Parse time
    from dateutil.parser import parse
    try:
        world.last_major_shift = parse(time_str)
    except Exception as e:
        raise ValidationError(
            message=f"Invalid time format: {str(e)}",
            details=[{
                "field": "time",
                "message": f"Invalid time format: {str(e)}",
                "value": time_str
            }]
        )
    
    return jsonify({'time': world.last_major_shift.isoformat()}), 200

# --- World Weather ---
@world_bp.route('/worlds/<int:world_id>/weather', methods=['GET'])
@jwt_required()
@rate_limit('world_weather_get')
def get_world_weather(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    return jsonify({'weather': getattr(world, 'weather', None)}), 200

@world_bp.route('/worlds/<int:world_id>/weather', methods=['PUT'])
@jwt_required()
@validate_json(WORLD_WEATHER_VALIDATOR_SCHEMA)
@rate_limit('world_weather_update')
@transaction('update_world_weather')
def update_world_weather(world_id):
    # Get world
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    # Get validated data from request context
    data = g.validated_data
    weather = data['weather']
    
    # Update weather
    setattr(world, 'weather', weather)
    
    return jsonify({'weather': weather}), 200

# --- World Events CRUD ---
@world_bp.route('/worlds/<int:world_id>/events', methods=['GET'])
@jwt_required()
@rate_limit('world_events_list')
def list_world_events(world_id):
    # Ensure world exists
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    events = Event.query.filter_by(region_id=world_id).all()
    return jsonify(EventSchema(many=True).dump(events)), 200

@world_bp.route('/worlds/<int:world_id>/events', methods=['POST'])
@jwt_required()
@validate_json(EVENT_VALIDATOR_SCHEMA)
@rate_limit('world_event_create')
@transaction('create_world_event')
def create_world_event(world_id):
    # Ensure world exists
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    # Get validated data from request context
    data = g.validated_data
    
    # Create event
    event = Event(region_id=world_id, **data)
    db.session.add(event)
    
    return jsonify(EventSchema().dump(event)), 201

@world_bp.route('/worlds/<int:world_id>/events/<int:event_id>', methods=['GET'])
@jwt_required()
@rate_limit('world_event_get')
def get_world_event(world_id, event_id):
    event = Event.query.filter_by(region_id=world_id, id=event_id).first()
    if not event:
        raise NotFoundError("Event", str(event_id))
    
    return jsonify(EventSchema().dump(event)), 200

@world_bp.route('/worlds/<int:world_id>/events/<int:event_id>', methods=['PUT'])
@jwt_required()
@validate_json(EVENT_VALIDATOR_SCHEMA)
@rate_limit('world_event_update')
@transaction('update_world_event')
def update_world_event(world_id, event_id):
    # Get event
    event = Event.query.filter_by(region_id=world_id, id=event_id).first()
    if not event:
        raise NotFoundError("Event", str(event_id))
    
    # Get validated data from request context
    data = g.validated_data
    
    # Update event
    for key, value in data.items():
        setattr(event, key, value)
    
    return jsonify(EventSchema().dump(event)), 200

@world_bp.route('/worlds/<int:world_id>/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
@rate_limit('world_event_delete')
@transaction('delete_world_event')
def delete_world_event(world_id, event_id):
    event = Event.query.filter_by(region_id=world_id, id=event_id).first()
    if not event:
        raise NotFoundError("Event", str(event_id))
    
    db.session.delete(event)
    
    return jsonify({'message': 'Event deleted'}), 200

# --- World Factions CRUD ---
@world_bp.route('/worlds/<int:world_id>/factions', methods=['GET'])
@jwt_required()
@rate_limit('world_factions_list')
def list_world_factions(world_id):
    # Ensure world exists
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    factions = Faction.query.all()  # TODO: Filter by world/region if model supports
    return jsonify(FactionSchema(many=True).dump(factions)), 200

@world_bp.route('/worlds/<int:world_id>/factions', methods=['POST'])
@jwt_required()
@validate_json(FACTION_VALIDATOR_SCHEMA)
@rate_limit('world_faction_create')
@transaction('create_world_faction')
def create_world_faction(world_id):
    # Ensure world exists
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    # Get validated data from request context
    data = g.validated_data
    
    # Create faction
    faction = Faction(**data)
    db.session.add(faction)
    
    return jsonify(FactionSchema().dump(faction)), 201

@world_bp.route('/worlds/<int:world_id>/factions/<int:faction_id>', methods=['GET'])
@jwt_required()
@rate_limit('world_faction_get')
def get_world_faction(world_id, faction_id):
    # Ensure world exists
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    faction = Faction.query.get(faction_id)
    if not faction:
        raise NotFoundError("Faction", str(faction_id))
    
    return jsonify(FactionSchema().dump(faction)), 200

@world_bp.route('/worlds/<int:world_id>/factions/<int:faction_id>', methods=['PUT'])
@jwt_required()
@validate_json(FACTION_VALIDATOR_SCHEMA)
@rate_limit('world_faction_update')
@transaction('update_world_faction')
def update_world_faction(world_id, faction_id):
    # Ensure world exists
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    # Get faction
    faction = Faction.query.get(faction_id)
    if not faction:
        raise NotFoundError("Faction", str(faction_id))
    
    # Get validated data from request context
    data = g.validated_data
    
    # Update faction
    for key, value in data.items():
        setattr(faction, key, value)
    
    return jsonify(FactionSchema().dump(faction)), 200

@world_bp.route('/worlds/<int:world_id>/factions/<int:faction_id>', methods=['DELETE'])
@jwt_required()
@rate_limit('world_faction_delete')
@transaction('delete_world_faction')
def delete_world_faction(world_id, faction_id):
    # Ensure world exists
    world = WorldState.query.get(world_id)
    if not world:
        raise NotFoundError("World", str(world_id))
    
    faction = Faction.query.get(faction_id)
    if not faction:
        raise NotFoundError("Faction", str(faction_id))
    
    db.session.delete(faction)
    
    return jsonify({'message': 'Faction deleted'}), 200 