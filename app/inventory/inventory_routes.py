"""
Inventory-related API routes.
Provides endpoints for item management and interaction.
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any, List, Optional
from sqlalchemy.orm.exc import NoResultFound
from app.core.database import db
from app.core.models.inventory import InventoryItem
from app.core.utils.error_utils import ValidationError, DatabaseError, NotFoundError
from fastapi import APIRouter, HTTPException

inventory_bp = Blueprint('inventory', __name__)

# === Item Routes ===
@inventory_bp.route('/items', methods=['GET'])
def get_items():
    """Get all items."""
    items = db.session.query(InventoryItem).all()
    return jsonify([item.to_dict() for item in items]), 200

@inventory_bp.route('/items', methods=['POST'])
def create_item():
    """Create a new item."""
    data = request.get_json()
    item = InventoryItem(
        name=data['name'],
        description=data.get('description'),
        type=data.get('type'),
        weight=data.get('weight', 0),
        value=data.get('value', 0),
        properties=data.get('properties', {})
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@inventory_bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get a specific item."""
    item = db.session.query(InventoryItem).get_or_404(item_id)
    return jsonify(item.to_dict()), 200

@inventory_bp.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Update an item."""
    item = db.session.query(InventoryItem).get_or_404(item_id)
    data = request.get_json()
    
    for key, value in data.items():
        if hasattr(item, key):
            setattr(item, key, value)
    
    db.session.commit()
    return jsonify(item.to_dict()), 200

@inventory_bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Delete an item."""
    item = db.session.query(InventoryItem).get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return '', 204

# === Character Inventory Routes ===
@inventory_bp.route('/characters/<int:character_id>/items', methods=['GET'])
def get_character_items(character_id):
    """Get all items in a character's inventory."""
    items = db.session.query(InventoryItem).filter_by(character_id=character_id).all()
    return jsonify([item.to_dict() for item in items]), 200

@inventory_bp.route('/characters/<int:character_id>/items', methods=['POST'])
def add_item_to_character(character_id):
    """Add an item to a character's inventory."""
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    item = db.session.query(InventoryItem).get_or_404(item_id)
    # Add logic to handle item addition to character inventory
    return jsonify({"message": "Item added to inventory"}), 201

@inventory_bp.route('/characters/<int:character_id>/items/<int:item_id>', methods=['DELETE'])
def remove_item_from_character(character_id, item_id):
    """Remove an item from a character's inventory."""
    # Add logic to handle item removal from character inventory
    return '', 204 