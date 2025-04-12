# inventory.py

import json
from flask import Blueprint, request, jsonify
from firebase_admin import db

inventory_bp = Blueprint("inventory", __name__)
__all__ = ["inventory_bp"]

# ----------------------------
# Equipment Rule Loader
# ----------------------------

def load_equipment_rules():
    try:
        with open("rules/equipment.json", "r") as f:
            return {item["name"]: item for item in json.load(f)}
    except Exception as e:
        print("Error loading equipment.json:", e)
        return {}

equipment_rules = load_equipment_rules()

# ----------------------------
# Get Inventory
# ----------------------------

@inventory_bp.route("/inventory/<character_id>", methods=["GET"])
def get_inventory(character_id):
    ref = db.reference(f"/players/{character_id}")
    char = ref.get() or {}
    return jsonify({
        "inventory": char.get("inventory", []),
        "equipment": char.get("equipment", []),
        "gold": char.get("gold", 0),
        "dr": char.get("dr", 0)
    })

# ----------------------------
# Equip Item
# ----------------------------

@inventory_bp.route("/inventory/equip", methods=["POST"])
def equip_item():
    data = request.json
    character_id = data.get("character_id")
    item_name = data.get("item")

    if not character_id or not item_name:
        return jsonify({"error": "Missing character_id or item"}), 400

    ref = db.reference(f"/players/{character_id}")
    char = ref.get() or {}
    inventory = char.get("inventory", [])
    equipment = char.get("equipment", [])

    if item_name not in inventory:
        return jsonify({"error": "Item not in inventory"}), 400

    if item_name not in equipment:
        equipment.append(item_name)
        char["equipment"] = equipment

    dr_total = sum(equipment_rules.get(e, {}).get("dr", 0) for e in equipment)
    char["dr"] = dr_total

    ref.set(char)
    return jsonify({"message": f"{item_name} equipped", "dr": dr_total})

# ----------------------------
# Unequip Item
# ----------------------------

@inventory_bp.route("/inventory/unequip", methods=["POST"])
def unequip_item():
    data = request.json
    character_id = data.get("character_id")
    item_name = data.get("item")

    if not character_id or not item_name:
        return jsonify({"error": "Missing character_id or item"}), 400

    ref = db.reference(f"/players/{character_id}")
    char = ref.get() or {}
    equipment = char.get("equipment", [])

    if item_name in equipment:
        equipment.remove(item_name)
        char["equipment"] = equipment

    dr_total = sum(equipment_rules.get(e, {}).get("dr", 0) for e in equipment)
    char["dr"] = dr_total
    ref.set(char)
    return jsonify({"message": f"{item_name} unequipped", "dr": dr_total})

# ----------------------------
# Use Item
# ----------------------------

@inventory_bp.route("/inventory/use", methods=["POST"])
def use_item():
    data = request.json
    character_id = data.get("character_id")
    item_name = data.get("item")

    if not character_id or not item_name:
        return jsonify({"error": "Missing character_id or item"}), 400

    ref = db.reference(f"/players/{character_id}")
    char = ref.get() or {}
    inventory = char.get("inventory", [])

    if item_name not in inventory:
        return jsonify({"error": "Item not found in inventory"}), 400

    inventory.remove(item_name)
    char["inventory"] = inventory
    ref.set(char)

    return jsonify({"message": f"{item_name} used and removed from inventory"})

# ----------------------------
# Drop Item
# ----------------------------

@inventory_bp.route("/inventory/drop", methods=["POST"])
def drop_item():
    data = request.json
    character_id = data.get("character_id")
    item_name = data.get("item")

    if not character_id or not item_name:
        return jsonify({"error": "Missing character_id or item"}), 400

    ref = db.reference(f"/players/{character_id}")
    char = ref.get() or {}
    inventory = char.get("inventory", [])

    if item_name in inventory:
        inventory.remove(item_name)
        char["inventory"] = inventory
        ref.set(char)
        return jsonify({"message": f"{item_name} dropped"})

    return jsonify({"error": f"{item_name} not found"}), 400

# ----------------------------
# Reorder Inventory
# ----------------------------

@inventory_bp.route("/inventory/reorder", methods=["POST"])
def reorder_inventory():
    data = request.json
    character_id = data.get("character_id")
    new_order = data.get("new_order")

    if not character_id or not new_order:
        return jsonify({"error": "Missing character_id or new_order data"}), 400

    ref = db.reference(f"/players/{character_id}")
    char = ref.get() or {}
    current_inventory = char.get("inventory", [])

    if set(new_order) != set(current_inventory):
        return jsonify({"error": "New order must match existing inventory"}), 400

    char["inventory"] = new_order
    ref.set(char)

    return jsonify({"message": "Inventory reordered", "new_inventory": new_order})

# ----------------------------
# Debug: Standalone Testing
# ----------------------------

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.run(debug=True)
