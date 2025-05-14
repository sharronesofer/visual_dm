from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.world_state import WorldState
from app.models.event import Event
from app.models.faction import Faction
from app.core.database import db
from app.api.schemas.world import WorldSchema
from app.api.schemas.event import EventSchema
from app.api.schemas.faction import FactionSchema

world_bp = Blueprint('world', __name__)

# --- Worlds CRUD ---
@world_bp.route('/worlds', methods=['GET'])
@jwt_required()
def list_worlds():
    worlds = WorldState.query.all()
    return jsonify(WorldSchema(many=True).dump(worlds)), 200

@world_bp.route('/worlds', methods=['POST'])
@jwt_required()
def create_world():
    data = request.get_json(force=True)
    schema = WorldSchema()
    try:
        world_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    world = WorldState(**world_data)
    db.session.add(world)
    db.session.commit()
    return jsonify(schema.dump(world)), 201

@world_bp.route('/worlds/<int:world_id>', methods=['GET'])
@jwt_required()
def get_world(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        return jsonify({'error': 'World not found'}), 404
    return jsonify(WorldSchema().dump(world)), 200

@world_bp.route('/worlds/<int:world_id>', methods=['PUT'])
@jwt_required()
def update_world(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        return jsonify({'error': 'World not found'}), 404
    data = request.get_json(force=True)
    schema = WorldSchema()
    try:
        world_data = schema.load(data, partial=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    for key, value in world_data.items():
        setattr(world, key, value)
    db.session.commit()
    return jsonify(schema.dump(world)), 200

@world_bp.route('/worlds/<int:world_id>', methods=['DELETE'])
@jwt_required()
def delete_world(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        return jsonify({'error': 'World not found'}), 404
    db.session.delete(world)
    db.session.commit()
    return jsonify({'message': 'World deleted'}), 200

# --- World Time ---
@world_bp.route('/worlds/<int:world_id>/time', methods=['GET'])
@jwt_required()
def get_world_time(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        return jsonify({'error': 'World not found'}), 404
    return jsonify({'time': world.last_major_shift.isoformat() if world.last_major_shift else None}), 200

@world_bp.route('/worlds/<int:world_id>/time', methods=['PUT'])
@jwt_required()
def update_world_time(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        return jsonify({'error': 'World not found'}), 404
    data = request.get_json(force=True)
    time = data.get('time')
    if not time:
        return jsonify({'error': 'Missing time'}), 400
    from dateutil.parser import parse
    try:
        world.last_major_shift = parse(time)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    db.session.commit()
    return jsonify({'time': world.last_major_shift.isoformat()}), 200

# --- World Weather ---
@world_bp.route('/worlds/<int:world_id>/weather', methods=['GET'])
@jwt_required()
def get_world_weather(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        return jsonify({'error': 'World not found'}), 404
    return jsonify({'weather': getattr(world, 'weather', None)}), 200

@world_bp.route('/worlds/<int:world_id>/weather', methods=['PUT'])
@jwt_required()
def update_world_weather(world_id):
    world = WorldState.query.get(world_id)
    if not world:
        return jsonify({'error': 'World not found'}), 404
    data = request.get_json(force=True)
    weather = data.get('weather')
    if not weather:
        return jsonify({'error': 'Missing weather'}), 400
    setattr(world, 'weather', weather)
    db.session.commit()
    return jsonify({'weather': weather}), 200

# --- World Events CRUD ---
@world_bp.route('/worlds/<int:world_id>/events', methods=['GET'])
@jwt_required()
def list_world_events(world_id):
    events = Event.query.filter_by(region_id=world_id).all()
    return jsonify(EventSchema(many=True).dump(events)), 200

@world_bp.route('/worlds/<int:world_id>/events', methods=['POST'])
@jwt_required()
def create_world_event(world_id):
    data = request.get_json(force=True)
    schema = EventSchema()
    try:
        event_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    event = Event(region_id=world_id, **event_data)
    db.session.add(event)
    db.session.commit()
    return jsonify(schema.dump(event)), 201

@world_bp.route('/worlds/<int:world_id>/events/<int:event_id>', methods=['GET'])
@jwt_required()
def get_world_event(world_id, event_id):
    event = Event.query.filter_by(region_id=world_id, id=event_id).first()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify(EventSchema().dump(event)), 200

@world_bp.route('/worlds/<int:world_id>/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_world_event(world_id, event_id):
    event = Event.query.filter_by(region_id=world_id, id=event_id).first()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    data = request.get_json(force=True)
    schema = EventSchema()
    try:
        event_data = schema.load(data, partial=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    for key, value in event_data.items():
        setattr(event, key, value)
    db.session.commit()
    return jsonify(schema.dump(event)), 200

@world_bp.route('/worlds/<int:world_id>/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_world_event(world_id, event_id):
    event = Event.query.filter_by(region_id=world_id, id=event_id).first()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted'}), 200

# --- World Factions CRUD ---
@world_bp.route('/worlds/<int:world_id>/factions', methods=['GET'])
@jwt_required()
def list_world_factions(world_id):
    factions = Faction.query.all()  # TODO: Filter by world/region if model supports
    return jsonify(FactionSchema(many=True).dump(factions)), 200

@world_bp.route('/worlds/<int:world_id>/factions', methods=['POST'])
@jwt_required()
def create_world_faction(world_id):
    data = request.get_json(force=True)
    schema = FactionSchema()
    try:
        faction_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    faction = Faction(**faction_data)
    db.session.add(faction)
    db.session.commit()
    return jsonify(schema.dump(faction)), 201

@world_bp.route('/worlds/<int:world_id>/factions/<int:faction_id>', methods=['GET'])
@jwt_required()
def get_world_faction(world_id, faction_id):
    faction = Faction.query.get(faction_id)
    if not faction:
        return jsonify({'error': 'Faction not found'}), 404
    return jsonify(FactionSchema().dump(faction)), 200

@world_bp.route('/worlds/<int:world_id>/factions/<int:faction_id>', methods=['PUT'])
@jwt_required()
def update_world_faction(world_id, faction_id):
    faction = Faction.query.get(faction_id)
    if not faction:
        return jsonify({'error': 'Faction not found'}), 404
    data = request.get_json(force=True)
    schema = FactionSchema()
    try:
        faction_data = schema.load(data, partial=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    for key, value in faction_data.items():
        setattr(faction, key, value)
    db.session.commit()
    return jsonify(schema.dump(faction)), 200

@world_bp.route('/worlds/<int:world_id>/factions/<int:faction_id>', methods=['DELETE'])
@jwt_required()
def delete_world_faction(world_id, faction_id):
    faction = Faction.query.get(faction_id)
    if not faction:
        return jsonify({'error': 'Faction not found'}), 404
    db.session.delete(faction)
    db.session.commit()
    return jsonify({'message': 'Faction deleted'}), 200 