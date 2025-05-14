"""Region-related routes and endpoints."""

from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime
from typing import Dict, Any, List
from app.auth.auth_utils import require_auth
from app.utils.world_tick_utils import (
    process_world_tick,
    tick_all_motifs,
    tick_all_loyalty,
    tick_npc_emotions
)

region_bp = Blueprint('region', __name__)

@region_bp.route('/create', methods=['POST'])
@require_auth
def create_region() -> Dict[str, Any]:
    """
    Create a new region.
    
    Returns:
        Dict containing region data
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'type', 'size']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Generate region ID
        region_id = f"region_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create region data
        region_data = {
            'region_id': region_id,
            'name': data['name'],
            'type': data['type'],
            'size': data['size'],
            'description': data.get('description', ''),
            'climate': data.get('climate', 'temperate'),
            'resources': data.get('resources', []),
            'locations': data.get('locations', []),
            'npcs': data.get('npcs', []),
            'factions': data.get('factions', []),
            'events': [],
            'weather': {
                'current': 'clear',
                'temperature': 20,
                'last_updated': datetime.utcnow().isoformat()
            },
            'created_at': datetime.utcnow().isoformat(),
            'last_tick': datetime.utcnow().isoformat()
        }
        
        # Save region
        db.reference(f'/regions/{region_id}').set(region_data)
        
        return jsonify({
            'success': True,
            'region': region_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating region: {str(e)}'
        }), 500

@region_bp.route('/<region_id>/tick', methods=['POST'])
@require_auth
def tick_region(region_id: str) -> Dict[str, Any]:
    """
    Process a world tick for a region.
    
    Args:
        region_id: ID of the region
        
    Returns:
        Dict containing tick results
    """
    try:
        # Get region data
        region_ref = db.reference(f'/regions/{region_id}')
        region = region_ref.get()
        
        if not region:
            return jsonify({
                'success': False,
                'message': 'Region not found'
            }), 404
            
        # Process world tick
        world_state = {
            'current_time': datetime.fromisoformat(region['last_tick']),
            'weather': region['weather'],
            'npcs': region['npcs'],
            'active_effects': region.get('active_effects', []),
            'motifs': region.get('motifs', {}),
            'tick_duration': 3600  # 1 hour in seconds
        }
        
        # Process main tick
        updated_state = process_world_tick(world_state)
        
        # Process additional systems
        updated_state = tick_all_motifs(updated_state)
        
        # Update NPC states
        for npc_id in region['npcs']:
            tick_npc_emotions(npc_id)
            
        # Process faction loyalty
        updated_state = tick_all_loyalty(updated_state)
        
        # Update region data
        region.update({
            'weather': updated_state['weather'],
            'npcs': updated_state['npcs'],
            'active_effects': updated_state['active_effects'],
            'motifs': updated_state['motifs'],
            'last_tick': datetime.utcnow().isoformat()
        })
        
        # Save changes
        region_ref.set(region)
        
        return jsonify({
            'success': True,
            'region': region,
            'tick_results': {
                'time_passed': (datetime.utcnow() - world_state['current_time']).total_seconds(),
                'weather_changed': updated_state['weather'] != world_state['weather'],
                'npc_updates': len(updated_state['npcs']),
                'active_effects': len(updated_state['active_effects'])
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing tick: {str(e)}'
        }), 500

@region_bp.route('/<region_id>/events', methods=['GET'])
@require_auth
def list_region_events(region_id: str) -> Dict[str, Any]:
    """
    List events in a region.
    
    Args:
        region_id: ID of the region
        
    Returns:
        Dict containing list of events
    """
    try:
        # Get region data
        region_ref = db.reference(f'/regions/{region_id}')
        region = region_ref.get()
        
        if not region:
            return jsonify({
                'success': False,
                'message': 'Region not found'
            }), 404
            
        # Get events with optional filtering
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        event_type = request.args.get('type')
        
        events = region.get('events', [])
        
        # Apply filters
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
            events = [e for e in events if datetime.fromisoformat(e['timestamp']) >= start_dt]
            
        if end_time:
            end_dt = datetime.fromisoformat(end_time)
            events = [e for e in events if datetime.fromisoformat(e['timestamp']) <= end_dt]
            
        if event_type:
            events = [e for e in events if e.get('type') == event_type]
        
        return jsonify({
            'success': True,
            'events': events
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error listing events: {str(e)}'
        }), 500

@region_bp.route('/<region_id>/resources', methods=['PUT'])
@require_auth
def update_resources(region_id: str) -> Dict[str, Any]:
    """
    Update resources in a region.
    
    Args:
        region_id: ID of the region
        
    Returns:
        Dict containing updated resource data
    """
    try:
        data = request.get_json()
        resources = data.get('resources')
        
        if not resources:
            return jsonify({
                'success': False,
                'message': 'Missing resources data'
            }), 400
            
        # Get region data
        region_ref = db.reference(f'/regions/{region_id}')
        region = region_ref.get()
        
        if not region:
            return jsonify({
                'success': False,
                'message': 'Region not found'
            }), 404
            
        # Update resources
        region['resources'] = resources
        region_ref.update({'resources': resources})
        
        # Log resource change event
        event = {
            'type': 'resource_update',
            'timestamp': datetime.utcnow().isoformat(),
            'changes': {
                'old_resources': region.get('resources', []),
                'new_resources': resources
            }
        }
        
        events = region.get('events', [])
        events.append(event)
        region_ref.update({'events': events})
        
        return jsonify({
            'success': True,
            'resources': resources,
            'event': event
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating resources: {str(e)}'
        }), 500

@region_bp.route('/<region_id>/weather', methods=['PUT'])
@require_auth
def update_weather(region_id: str) -> Dict[str, Any]:
    """
    Update weather in a region.
    
    Args:
        region_id: ID of the region
        
    Returns:
        Dict containing updated weather data
    """
    try:
        data = request.get_json()
        weather = data.get('weather')
        
        if not weather:
            return jsonify({
                'success': False,
                'message': 'Missing weather data'
            }), 400
            
        # Validate weather data
        required_weather_fields = ['current', 'temperature']
        for field in required_weather_fields:
            if field not in weather:
                return jsonify({
                    'success': False,
                    'message': f'Missing weather field: {field}'
                }), 400
                
        # Get region data
        region_ref = db.reference(f'/regions/{region_id}')
        region = region_ref.get()
        
        if not region:
            return jsonify({
                'success': False,
                'message': 'Region not found'
            }), 404
            
        # Update weather
        weather['last_updated'] = datetime.utcnow().isoformat()
        region['weather'] = weather
        region_ref.update({'weather': weather})
        
        # Log weather change event
        event = {
            'type': 'weather_change',
            'timestamp': datetime.utcnow().isoformat(),
            'changes': {
                'old_weather': region.get('weather', {}),
                'new_weather': weather
            }
        }
        
        events = region.get('events', [])
        events.append(event)
        region_ref.update({'events': events})
        
        return jsonify({
            'success': True,
            'weather': weather,
            'event': event
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating weather: {str(e)}'
        }), 500 