from flask import Blueprint, request, jsonify
from firebase_admin import db
from uuid import uuid4
from datetime import datetime
from typing import Dict, Any, List

from app.auth.auth_utils import require_auth
from app.utils.validation import validate_required_fields
from app.game.world.pois.types import POIType

poi_bp = Blueprint('pois', __name__)

@poi_bp.route('/create', methods=['POST'])
@require_auth
def create_poi():
    """Create a new point of interest in a region."""
    try:
        data = request.get_json()
        required_fields = ['region_id', 'name', 'type', 'description', 'location']
        validate_required_fields(data, required_fields)

        poi_id = str(uuid4())
        poi_data = {
            'id': poi_id,
            'region_id': data['region_id'],
            'name': data['name'],
            'type': data['type'],
            'description': data['description'],
            'location': data['location'],
            'created_at': datetime.utcnow().isoformat(),
            'status': data.get('status', 'active'),
            'owner_id': data.get('owner_id'),
            'faction_id': data.get('faction_id'),
            'resources': data.get('resources', {}),
            'properties': data.get('properties', {})
        }

        # Validate POI type
        if poi_data['type'] not in POIType.__members__:
            return jsonify({'error': f'Invalid POI type. Must be one of: {list(POIType.__members__.keys())}'}), 400

        # Save POI data
        db.reference(f'pois/{poi_id}').set(poi_data)
        
        return jsonify({'message': 'POI created successfully', 'poi': poi_data}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@poi_bp.route('/<poi_id>', methods=['GET'])
@require_auth
def get_poi(poi_id: str):
    """Get details of a specific POI."""
    try:
        poi_ref = db.reference(f'pois/{poi_id}')
        poi_data = poi_ref.get()

        if not poi_data:
            return jsonify({'error': 'POI not found'}), 404

        return jsonify(poi_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@poi_bp.route('/<poi_id>/update', methods=['PUT'])
@require_auth
def update_poi(poi_id: str):
    """Update a POI's details."""
    try:
        data = request.get_json()
        poi_ref = db.reference(f'pois/{poi_id}')
        poi_data = poi_ref.get()

        if not poi_data:
            return jsonify({'error': 'POI not found'}), 404

        # Update allowed fields
        updateable_fields = ['name', 'description', 'status', 'owner_id', 'faction_id', 'resources', 'properties']
        updates = {k: v for k, v in data.items() if k in updateable_fields}
        
        if 'type' in data and data['type'] not in POIType.__members__:
            return jsonify({'error': f'Invalid POI type. Must be one of: {list(POIType.__members__.keys())}'}), 400

        poi_ref.update(updates)
        updated_data = poi_ref.get()

        return jsonify({'message': 'POI updated successfully', 'poi': updated_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@poi_bp.route('/region/<region_id>', methods=['GET'])
@require_auth
def list_region_pois(region_id: str):
    """List all POIs in a specific region."""
    try:
        pois_ref = db.reference('pois')
        all_pois = pois_ref.get() or {}
        
        # Filter POIs by region
        region_pois = {
            poi_id: poi_data 
            for poi_id, poi_data in all_pois.items() 
            if poi_data.get('region_id') == region_id
        }

        return jsonify(region_pois), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@poi_bp.route('/<poi_id>/delete', methods=['DELETE'])
@require_auth
def delete_poi(poi_id: str):
    """Delete a POI."""
    try:
        poi_ref = db.reference(f'pois/{poi_id}')
        poi_data = poi_ref.get()

        if not poi_data:
            return jsonify({'error': 'POI not found'}), 404

        poi_ref.delete()
        return jsonify({'message': 'POI deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400 