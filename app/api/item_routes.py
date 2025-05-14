from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.item import Item
from app.core.database import db
from marshmallow import Schema, fields, ValidationError

item_bp = Blueprint('item', __name__)

# --- Marshmallow Schema ---
class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    item_type = fields.Str(required=True)
    rarity = fields.Str()
    value = fields.Int()
    weight = fields.Float()
    properties = fields.Dict()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

# --- CRUD for Items ---
@item_bp.route('/items', methods=['GET'])
@jwt_required()
def list_items():
    items = Item.query.all()
    return jsonify(ItemSchema(many=True).dump(items)), 200

@item_bp.route('/items', methods=['POST'])
@jwt_required()
def create_item():
    data = request.get_json(force=True)
    schema = ItemSchema()
    try:
        item_data = schema.load(data)
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    item = Item(**item_data)
    db.session.add(item)
    db.session.commit()
    return jsonify(schema.dump(item)), 201

@item_bp.route('/items/<int:item_id>', methods=['GET'])
@jwt_required()
def get_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify(ItemSchema().dump(item)), 200

@item_bp.route('/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    data = request.get_json(force=True)
    schema = ItemSchema()
    try:
        item_data = schema.load(data, partial=True)
    except ValidationError as e:
        return jsonify({'error': e.messages}), 400
    for key, value in item_data.items():
        setattr(item, key, value)
    db.session.commit()
    return jsonify(schema.dump(item)), 200

@item_bp.route('/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'}), 200

# --- Inventory Management (Stub) ---
@item_bp.route('/inventories/<int:inventory_id>/items', methods=['GET'])
@jwt_required()
def list_inventory_items(inventory_id):
    # TODO: Implement inventory model and logic
    return jsonify({'message': 'Not implemented'}), 501

@item_bp.route('/inventories/<int:inventory_id>/items', methods=['POST'])
@jwt_required()
def add_item_to_inventory(inventory_id):
    # TODO: Implement inventory model and logic
    return jsonify({'message': 'Not implemented'}), 501

@item_bp.route('/inventories/<int:inventory_id>/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_inventory_item(inventory_id, item_id):
    # TODO: Implement inventory model and logic
    return jsonify({'message': 'Not implemented'}), 501

@item_bp.route('/inventories/<int:inventory_id>/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_item_from_inventory(inventory_id, item_id):
    # TODO: Implement inventory model and logic
    return jsonify({'message': 'Not implemented'}), 501

# --- Item Enhancement/Modification (Stub) ---
@item_bp.route('/items/<int:item_id>/enhance', methods=['POST'])
@jwt_required()
def enhance_item(item_id):
    # TODO: Implement enhancement logic
    return jsonify({'message': 'Not implemented'}), 501

@item_bp.route('/items/<int:item_id>/modify', methods=['POST'])
@jwt_required()
def modify_item(item_id):
    # TODO: Implement modification logic
    return jsonify({'message': 'Not implemented'}), 501 