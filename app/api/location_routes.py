from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.core.models.location import Location
from app.core.models.location_version import LocationVersion, LocationChangeLog
from app.core.services.location_version_service import LocationVersionService
from app.models.event import Event
from app.core.models.resource import Resource
from app.core.database import db
from app.api.schemas.location import LocationSchema
from app.api.schemas.event import EventSchema
from app.api.schemas.resource import ResourceSchema
from app.api.schemas.version import LocationVersionSchema, LocationChangeLogSchema
from datetime import datetime

location_bp = Blueprint('location', __name__)
version_service = LocationVersionService()

# --- Location CRUD ---
@location_bp.route('/locations', methods=['GET'])
@jwt_required()
def list_locations():
    locations = Location.query.all()
    return jsonify(LocationSchema(many=True).dump(locations)), 200

@location_bp.route('/locations', methods=['POST'])
@jwt_required()
def create_location():
    data = request.get_json(force=True)
    schema = LocationSchema()
    try:
        location_data = schema.load(data)
        location = Location(**location_data)
        db.session.add(location)
        db.session.commit()
        
        # Create initial version
        version_service.create_initial_version(location, changed_by=get_jwt_identity())
        
        return jsonify(schema.dump(location)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@location_bp.route('/locations/<int:location_id>', methods=['GET'])
@jwt_required()
def get_location(location_id):
    location = Location.query.get(location_id)
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    return jsonify(LocationSchema().dump(location)), 200

@location_bp.route('/locations/<int:location_id>', methods=['PUT'])
@jwt_required()
def update_location(location_id):
    location = Location.query.get_or_404(location_id)
    data = request.get_json(force=True)
    schema = LocationSchema()
    
    try:
        updates = schema.load(data, partial=True)
        change_reason = data.get('change_reason', 'Location update')
        
        # Update location and create version
        version, logs = version_service.update_location(
            location=location,
            updates=updates,
            change_reason=change_reason,
            changed_by=get_jwt_identity()
        )
        
        if not version:
            return jsonify({'message': 'No changes detected'}), 200
            
        return jsonify(schema.dump(location)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@location_bp.route('/locations/<int:location_id>', methods=['DELETE'])
@jwt_required()
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    
    try:
        # Create final version marking deletion
        version = location.create_version(
            change_type='deletion',
            change_reason='Location deleted',
            changed_by=get_jwt_identity()
        )
        db.session.add(version)
        
        # Delete location
        db.session.delete(location)
        db.session.commit()
        
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# --- Location State ---
@location_bp.route('/locations/<int:location_id>/state', methods=['GET'])
@jwt_required()
def get_location_state(location_id):
    location = Location.query.get(location_id)
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    return jsonify({'state': location.state}), 200

@location_bp.route('/locations/<int:location_id>/state', methods=['PUT'])
@jwt_required()
def update_location_state(location_id):
    location = Location.query.get(location_id)
    if not location:
        return jsonify({'error': 'Location not found'}), 404
    data = request.get_json(force=True)
    state = data.get('state')
    if not isinstance(state, dict):
        return jsonify({'error': 'State must be a dict'}), 400
    location.state = state
    db.session.commit()
    return jsonify({'state': location.state}), 200

# --- Location Events CRUD ---
@location_bp.route('/locations/<int:location_id>/events', methods=['GET'])
@jwt_required()
def list_location_events(location_id):
    events = Event.query.filter_by(region_id=location_id).all()
    return jsonify(EventSchema(many=True).dump(events)), 200

@location_bp.route('/locations/<int:location_id>/events', methods=['POST'])
@jwt_required()
def create_location_event(location_id):
    data = request.get_json(force=True)
    schema = EventSchema()
    try:
        event_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    event = Event(region_id=location_id, **event_data)
    db.session.add(event)
    db.session.commit()
    return jsonify(schema.dump(event)), 201

@location_bp.route('/locations/<int:location_id>/events/<int:event_id>', methods=['GET'])
@jwt_required()
def get_location_event(location_id, event_id):
    event = Event.query.filter_by(region_id=location_id, id=event_id).first()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    return jsonify(EventSchema().dump(event)), 200

@location_bp.route('/locations/<int:location_id>/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_location_event(location_id, event_id):
    event = Event.query.filter_by(region_id=location_id, id=event_id).first()
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

@location_bp.route('/locations/<int:location_id>/events/<int:event_id>', methods=['DELETE'])
@jwt_required()
def delete_location_event(location_id, event_id):
    event = Event.query.filter_by(region_id=location_id, id=event_id).first()
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Event deleted'}), 200

# --- Location Resources CRUD ---
@location_bp.route('/locations/<int:location_id>/resources', methods=['GET'])
@jwt_required()
def list_location_resources(location_id):
    resources = Resource.query.filter_by(region_id=location_id).all()
    return jsonify(ResourceSchema(many=True).dump(resources)), 200

@location_bp.route('/locations/<int:location_id>/resources', methods=['POST'])
@jwt_required()
def create_location_resource(location_id):
    data = request.get_json(force=True)
    schema = ResourceSchema()
    try:
        resource_data = schema.load(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    resource = Resource(region_id=location_id, **resource_data)
    db.session.add(resource)
    db.session.commit()
    return jsonify(schema.dump(resource)), 201

@location_bp.route('/locations/<int:location_id>/resources/<int:resource_id>', methods=['GET'])
@jwt_required()
def get_location_resource(location_id, resource_id):
    resource = Resource.query.filter_by(region_id=location_id, id=resource_id).first()
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    return jsonify(ResourceSchema().dump(resource)), 200

@location_bp.route('/locations/<int:location_id>/resources/<int:resource_id>', methods=['PUT'])
@jwt_required()
def update_location_resource(location_id, resource_id):
    resource = Resource.query.filter_by(region_id=location_id, id=resource_id).first()
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    data = request.get_json(force=True)
    schema = ResourceSchema()
    try:
        resource_data = schema.load(data, partial=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    for key, value in resource_data.items():
        setattr(resource, key, value)
    db.session.commit()
    return jsonify(schema.dump(resource)), 200

@location_bp.route('/locations/<int:location_id>/resources/<int:resource_id>', methods=['DELETE'])
@jwt_required()
def delete_location_resource(location_id, resource_id):
    resource = Resource.query.filter_by(region_id=location_id, id=resource_id).first()
    if not resource:
        return jsonify({'error': 'Resource not found'}), 404
    db.session.delete(resource)
    db.session.commit()
    return jsonify({'message': 'Resource deleted'}), 200

# --- Version Control Routes ---
@location_bp.route('/locations/<int:location_id>/versions', methods=['GET'])
@jwt_required()
def get_version_history(location_id):
    """Get version history for a location."""
    versions = version_service.get_version_history(location_id)
    return jsonify(LocationVersionSchema(many=True).dump(versions)), 200

@location_bp.route('/locations/<int:location_id>/versions/<int:version_number>', methods=['GET'])
@jwt_required()
def get_version(location_id, version_number):
    """Get a specific version of a location."""
    version = version_service.get_version(location_id, version_number)
    if not version:
        return jsonify({'error': 'Version not found'}), 404
    return jsonify(LocationVersionSchema().dump(version)), 200

@location_bp.route('/locations/<int:location_id>/versions/<int:version_number>/revert', methods=['POST'])
@jwt_required()
def revert_to_version(location_id, version_number):
    """Revert a location to a specific version."""
    location = Location.query.get_or_404(location_id)
    change_reason = request.json.get('change_reason', f'Reverted to version {version_number}')
    
    version = version_service.revert_location(location, version_number, change_reason)
    if not version:
        return jsonify({'error': 'Failed to revert to specified version'}), 400
        
    return jsonify(LocationVersionSchema().dump(version)), 200

@location_bp.route('/locations/<int:location_id>/changes', methods=['GET'])
@jwt_required()
def get_changes(location_id):
    """Get changes between versions."""
    from_version = request.args.get('from_version', type=int, default=0)
    to_version = request.args.get('to_version', type=int)
    
    changes = version_service.get_changes_between_versions(
        location_id=location_id,
        from_version=from_version,
        to_version=to_version
    )
    
    return jsonify(LocationChangeLogSchema(many=True).dump(changes)), 200

@location_bp.route('/locations/<int:location_id>/at-date', methods=['GET'])
@jwt_required()
def get_location_at_date(location_id):
    """Get location state at a specific date."""
    try:
        target_date = datetime.fromisoformat(request.args.get('date'))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)'}), 400
        
    version = version_service.get_location_at_date(location_id, target_date)
    if not version:
        return jsonify({'error': 'No version found for specified date'}), 404
        
    return jsonify(LocationVersionSchema().dump(version)), 200 