from flask import Blueprint, jsonify, request
from app.utils.auth import require_auth
from app.game.world.terrain_manager import TerrainManager
from app.game.world.pois.schema import POISchema
from app.core.utils.gpt.utils import log_usage

world_bp = Blueprint('world', __name__)

@world_bp.route('/generate_terrain', methods=['POST'])
@require_auth
def generate_terrain():
    """Generate terrain for a region."""
    data = request.get_json()
    region_id = data.get('region_id')
    character_id = data.get('character_id')
    
    if not region_id or not character_id:
        return jsonify({'error': 'Missing required fields'}), 400
        
    try:
        terrain_manager = TerrainManager(region_id, character_id)
        terrain_data = terrain_manager.get_terrain()
        log_usage(character_id, tokens=100, model='terrain-gen')  # Approximate token usage
        return jsonify(terrain_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@world_bp.route('/pois', methods=['POST'])
@require_auth
def create_poi():
    """Create a new Point of Interest."""
    data = request.get_json()
    schema = POISchema()
    
    try:
        validated_data = schema.load(data)
        # TODO: Save POI to database
        return jsonify(validated_data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@world_bp.route('/pois/<poi_id>', methods=['GET'])
@require_auth
def get_poi(poi_id):
    """Get a Point of Interest by ID."""
    try:
        # TODO: Fetch POI from database
        poi_data = {}  # Placeholder
        return jsonify(poi_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@world_bp.route('/pois/<poi_id>', methods=['PUT'])
@require_auth
def update_poi(poi_id):
    """Update a Point of Interest."""
    data = request.get_json()
    schema = POISchema()
    
    try:
        validated_data = schema.load(data)
        # TODO: Update POI in database
        return jsonify(validated_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@world_bp.route('/pois/<poi_id>', methods=['DELETE'])
@require_auth
def delete_poi(poi_id):
    """Delete a Point of Interest."""
    try:
        # TODO: Delete POI from database
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@world_bp.route('/regions/<region_id>/discover', methods=['POST'])
@require_auth
def discover_region(region_id):
    """Mark a region as discovered by a character."""
    data = request.get_json()
    character_id = data.get('character_id')
    
    if not character_id:
        return jsonify({'error': 'Missing character_id'}), 400
        
    try:
        # TODO: Update character's discovered regions in database
        return jsonify({'message': f'Region {region_id} discovered by character {character_id}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@world_bp.route('/regions/<region_id>/weather', methods=['GET'])
@require_auth
def get_weather(region_id):
    """Get the current weather for a region."""
    try:
        # TODO: Implement weather system
        weather_data = {
            'condition': 'clear',
            'temperature': 20,
            'wind_speed': 5,
            'precipitation': 0
        }
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 