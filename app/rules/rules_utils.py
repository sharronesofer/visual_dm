import json
import logging
from app.data.inventory_utils import load_equipment_rules

def calculate_dr(equipment_list, feats=None):
    """
    Calculates total DR based on equipped armor and feat-based bonuses.
    `equipment_list`: list of item names (strings)
    `feats`: optional list of feat dicts or names
    """
    equipment_rules = load_equipment_rules()
    total_dr = 0

    # Equipment-based DR
    for item in equipment_list:
        item_data = equipment_rules.get(item, {})
        total_dr += item_data.get("dr", 0)

    # Feat-based DR (if structured as full dicts with a 'bonus' field)
    if feats:
        for feat in feats:
            if isinstance(feat, dict):
                bonus = feat.get("bonus", {})
                if bonus.get("stat") == "DR":
                    total_dr += bonus.get("value", 0)

    return total_dr

def load_json(path):
    """
    Utility function to load JSON data from a specified file path.
    """
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON from {path}: {e}")
        return {}

# Load equipment data at module initialization
equipment_data = load_json("rules_json/equipment.json")

def validate_equipment_item(item_name):
    """
    Validates if an equipment item exists and returns its details.

    Args:
        item_name (str): The name of the equipment item to validate.

    Returns:
        tuple: (bool, dict or str) Validation status and item details or error message.
    """
    item_details = equipment_data.get(item_name)
    if not item_details:
        return False, f"Equipment '{item_name}' not found."
    
    # Add additional validation logic here if needed

    return True, item_details