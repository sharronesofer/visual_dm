"""Motif-related routes and endpoints."""

from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime
from typing import Dict, Any
from app.auth.auth_utils import require_auth

motif_bp = Blueprint('motif', __name__)

@motif_bp.route('/create', methods=['POST'])
@require_auth
def create_motif() -> Dict[str, Any]:
    """
    Create a new story motif.
    
    Returns:
        Dict containing motif data
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'description', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Generate motif ID
        motif_id = f"motif_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create motif data
        motif_data = {
            'motif_id': motif_id,
            'name': data['name'],
            'description': data['description'],
            'type': data['type'],
            'strength': data.get('strength', 1),
            'active': True,
            'created_at': datetime.utcnow().isoformat(),
            'last_update': datetime.utcnow().isoformat(),
            'supporting_events': [],
            'opposing_events': [],
            'affected_regions': data.get('affected_regions', []),
            'affected_characters': data.get('affected_characters', []),
            'completion_threshold': data.get('completion_threshold', 10),
            'failure_threshold': data.get('failure_threshold', 0),
            'daily_decay': data.get('daily_decay', 0.1)
        }
        
        # Save motif
        db.reference(f'/motifs/{motif_id}').set(motif_data)
        
        return jsonify({
            'success': True,
            'motif': motif_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creating motif: {str(e)}'
        }), 500

@motif_bp.route('/<motif_id>/event', methods=['POST'])
@require_auth
def add_motif_event(motif_id: str) -> Dict[str, Any]:
    """
    Add an event that affects a motif.
    
    Args:
        motif_id: ID of the motif
        
    Returns:
        Dict containing updated motif data
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['event_type', 'description', 'impact']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }), 400
                
        # Get motif data
        motif_ref = db.reference(f'/motifs/{motif_id}')
        motif = motif_ref.get()
        
        if not motif:
            return jsonify({
                'success': False,
                'message': 'Motif not found'
            }), 404
            
        # Create event data
        event = {
            'type': data['event_type'],
            'description': data['description'],
            'impact': data['impact'],
            'timestamp': datetime.utcnow().isoformat(),
            'location': data.get('location'),
            'characters': data.get('characters', [])
        }
        
        # Add event to appropriate list
        if data['event_type'] == 'supporting':
            motif['supporting_events'].append(event)
            motif['strength'] = min(10, motif['strength'] + event['impact'])
        else:
            motif['opposing_events'].append(event)
            motif['strength'] = max(0, motif['strength'] - event['impact'])
            
        # Update last update time
        motif['last_update'] = datetime.utcnow().isoformat()
        
        # Check for completion or failure
        if motif['strength'] >= motif['completion_threshold']:
            motif['active'] = False
            motif['status'] = 'completed'
        elif motif['strength'] <= motif['failure_threshold']:
            motif['active'] = False
            motif['status'] = 'failed'
            
        # Save changes
        motif_ref.set(motif)
        
        return jsonify({
            'success': True,
            'motif': motif
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error adding event: {str(e)}'
        }), 500

@motif_bp.route('/active', methods=['GET'])
@require_auth
def list_active_motifs() -> Dict[str, Any]:
    """
    List all active motifs.
    
    Returns:
        Dict containing list of active motifs
    """
    try:
        # Get all motifs
        motifs_ref = db.reference('/motifs')
        motifs = motifs_ref.get() or {}
        
        # Filter active motifs
        active_motifs = {
            motif_id: motif_data
            for motif_id, motif_data in motifs.items()
            if motif_data.get('active', False)
        }
        
        return jsonify({
            'success': True,
            'motifs': active_motifs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error listing motifs: {str(e)}'
        }), 500

@motif_bp.route('/<motif_id>/resolve', methods=['POST'])
@require_auth
def resolve_motif(motif_id: str) -> Dict[str, Any]:
    """
    Manually resolve a motif.
    
    Args:
        motif_id: ID of the motif
        
    Returns:
        Dict containing resolved motif data
    """
    try:
        data = request.get_json()
        resolution_type = data.get('resolution_type', 'completed')
        
        # Get motif data
        motif_ref = db.reference(f'/motifs/{motif_id}')
        motif = motif_ref.get()
        
        if not motif:
            return jsonify({
                'success': False,
                'message': 'Motif not found'
            }), 404
            
        # Update motif status
        motif.update({
            'active': False,
            'status': resolution_type,
            'resolution_notes': data.get('notes'),
            'resolved_at': datetime.utcnow().isoformat()
        })
        
        # Save changes
        motif_ref.set(motif)
        
        return jsonify({
            'success': True,
            'motif': motif
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error resolving motif: {str(e)}'
        }), 500 