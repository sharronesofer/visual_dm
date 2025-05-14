"""
Routes for building generation and management.
"""

from flask import Blueprint, jsonify, request
from app.core.mesh.async_building_generator import building_generator
import asyncio

building_routes = Blueprint('building_routes', __name__)

@building_routes.route('/api/buildings/generate', methods=['POST'])
async def generate_buildings():
    """
    Generate multiple buildings asynchronously.
    
    Expected JSON format:
    {
        "buildings": [
            {
                "id": "building_1",
                "type": "residential",
                "rooms": [...],
                "materials": {...},
                "texture_paths": {...},
                "lod": 2,
                "priority": 1
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        buildings = data.get('buildings', [])
        
        # Queue all buildings for generation
        for building in buildings:
            building_generator.queue_building(
                building_id=building['id'],
                building_type=building['type'],
                rooms=building['rooms'],
                materials=building['materials'],
                texture_paths=building['texture_paths'],
                lod=building.get('lod', 2),
                priority=building.get('priority', 1)
            )
        
        # Process the queue and get results
        results = await building_generator.process_queue()
        
        return jsonify({
            'status': 'success',
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@building_routes.route('/api/buildings/status', methods=['GET'])
def get_generation_status():
    """Get the status of the building generation queue."""
    try:
        queue = building_generator.generation_queue
        return jsonify({
            'status': 'success',
            'queue_size': queue.task_queue.qsize(),
            'workers': len(queue.workers),
            'running': queue.running
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 