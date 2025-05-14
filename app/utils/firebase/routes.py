"""
Flask routes for Firebase operations.
"""

from flask import Blueprint, jsonify, request
from app.utils.firebase.client import (
    firebase_get,
    firebase_set,
    firebase_update,
    firebase_delete
)

firebase_bp = Blueprint('firebase', __name__)

@firebase_bp.route('/api/firebase/<path:path>', methods=['GET'])
def get_data(path):
    """Get data from Firebase."""
    data = firebase_get(path)
    return jsonify(data)

@firebase_bp.route('/api/firebase/<path:path>', methods=['POST'])
def set_data(path):
    """Set data in Firebase."""
    data = request.get_json()
    success = firebase_set(path, data)
    return jsonify({'success': success})

@firebase_bp.route('/api/firebase/<path:path>', methods=['PATCH'])
def update_data(path):
    """Update data in Firebase."""
    data = request.get_json()
    success = firebase_update(path, data)
    return jsonify({'success': success})

@firebase_bp.route('/api/firebase/<path:path>', methods=['DELETE'])
def delete_data(path):
    """Delete data from Firebase."""
    success = firebase_delete(path)
    return jsonify({'success': success}) 