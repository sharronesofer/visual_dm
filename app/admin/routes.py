"""
Admin routes.
"""

from flask import jsonify, request
from app.admin import admin_bp

@admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Admin dashboard endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Admin dashboard'
    })

@admin_bp.route('/users', methods=['GET'])
def list_users():
    """List users endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Users list'
    })

@admin_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """Admin settings endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Admin settings'
    }) 