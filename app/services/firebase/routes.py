"""Firebase services routes and endpoints."""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
from app.auth.auth_utils import require_auth
from app.utils.firebase.logging import log_event
from firebase_admin import db

firebase_bp = Blueprint('firebase', __name__)

@firebase_bp.route('/log', methods=['POST'])
@require_auth
def log_firebase_event() -> Dict[str, Any]:
    """
    Log an event to Firebase.
    
    Returns:
        Dict containing log status
    """
    try:
        data = request.get_json()
        if not data or 'event_type' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing event_type parameter'
            }), 400
            
        log_event(
            event_type=data['event_type'],
            event_data=data.get('event_data', {}),
            user_id=request.user_id
        )
        
        return jsonify({
            'success': True,
            'message': 'Event logged successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error logging event: {str(e)}'
        }), 500

@firebase_bp.route('/data/<path:ref_path>', methods=['GET'])
@require_auth
def get_firebase_data(ref_path: str) -> Dict[str, Any]:
    """
    Get data from Firebase at the specified path.
    
    Args:
        ref_path: Firebase reference path
        
    Returns:
        Dict containing requested data
    """
    try:
        data = db.reference(ref_path).get()
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting data: {str(e)}'
        }), 500

@firebase_bp.route('/data/<path:ref_path>', methods=['PUT'])
@require_auth
def update_firebase_data(ref_path: str) -> Dict[str, Any]:
    """
    Update data in Firebase at the specified path.
    
    Args:
        ref_path: Firebase reference path
        
    Returns:
        Dict containing update status
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
            
        db.reference(ref_path).update(data)
        
        return jsonify({
            'success': True,
            'message': 'Data updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating data: {str(e)}'
        }), 500

@firebase_bp.route('/data/<path:ref_path>', methods=['DELETE'])
@require_auth
def delete_firebase_data(ref_path: str) -> Dict[str, Any]:
    """
    Delete data from Firebase at the specified path.
    
    Args:
        ref_path: Firebase reference path
        
    Returns:
        Dict containing deletion status
    """
    try:
        db.reference(ref_path).delete()
        
        return jsonify({
            'success': True,
            'message': 'Data deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error deleting data: {str(e)}'
        }), 500 