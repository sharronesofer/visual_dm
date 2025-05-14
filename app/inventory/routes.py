from flask import jsonify, request
from app.core.database import db
from app.core.models.inventory import InventoryItem
from . import inventory_bp

@inventory_bp.route('/items', methods=['GET'])
def get_items():
    items = db.session.query(InventoryItem).all()
    return jsonify([item.to_dict() for item in items]), 200

@inventory_bp.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    item = InventoryItem(
        name=data['name'],
        description=data.get('description'),
        weight=data.get('weight', 0),
        value=data.get('value', 0),
        type=data.get('type', 'misc'),
        properties=data.get('properties', {})
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201

@inventory_bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = db.session.query(InventoryItem).get_or_404(item_id)
    return jsonify(item.to_dict()), 200

@inventory_bp.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = db.session.query(InventoryItem).get_or_404(item_id)
    data = request.get_json()
    
    for key, value in data.items():
        if hasattr(item, key):
            setattr(item, key, value)
    
    db.session.commit()
    return jsonify(item.to_dict()), 200

@inventory_bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = db.session.query(InventoryItem).get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return '', 204 