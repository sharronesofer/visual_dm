"""
Faction routes for managing political entities and their relationships.
"""

from flask import Blueprint, jsonify, request
from typing import Dict, List, Optional
from app.core.utils.error_utils import ValidationError, NotFoundError
from app.core.faction import faction_system

faction_bp = Blueprint('faction', __name__)

@faction_bp.route('/create', methods=['POST'])
def create_faction():
    """Create a new faction."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['name', 'description', 'goals', 'values', 'alignment']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
                
        faction_id = faction_system.create_faction(
            name=data['name'],
            description=data['description'],
            goals=data['goals'],
            values=data['values'],
            alignment=data['alignment']
        )
        
        return jsonify({
            'success': True,
            'faction_id': faction_id,
            'message': 'Faction created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@faction_bp.route('/<faction_id>', methods=['GET'])
def get_faction(faction_id: str):
    """Get a faction by ID."""
    try:
        faction = faction_system.get_faction(faction_id)
        if not faction:
            return jsonify({'error': 'Faction not found'}), 404
            
        return jsonify({
            'success': True,
            'faction': faction
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@faction_bp.route('/<faction_id>/add_member', methods=['POST'])
def add_member(faction_id: str):
    """Add a member to a faction."""
    try:
        data = request.get_json()
        if not data or 'npc_id' not in data or 'role' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        faction_system.add_member(
            faction_id=faction_id,
            npc_id=data['npc_id'],
            role=data['role']
        )
        
        return jsonify({
            'success': True,
            'message': 'Member added successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@faction_bp.route('/<faction_id>/update_relationship', methods=['POST'])
def update_relationship(faction_id: str):
    """Update relationship with another faction."""
    try:
        data = request.get_json()
        if not data or 'target_faction_id' not in data or 'change' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
            
        faction_system.update_faction_relationship(
            faction_id=faction_id,
            target_faction_id=data['target_faction_id'],
            change=data['change']
        )
        
        return jsonify({
            'success': True,
            'message': 'Relationship updated successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 