from datetime import datetime
from firebase_admin import db

# Constants
tension_levels = [
    (0, 10, "peaceful"),
    (11, 30, "watchful"),
    (31, 60, "anxious"),
    (61, 80, "violent"),
    (81, 100, "collapsing")
]

# Helper function to get the descriptor based on tension level
def get_tension_descriptor(level):
    for low, high, label in tension_levels:
        if low <= level <= high:
            return label
    return "unknown"

# Retrieve current tension data for a region
def get_tension(region_id):
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {"level": 0, "modifiers": {}}
    level = data.get("level", 0)
    label = get_tension_descriptor(level)
    return {
        "region": region_id,
        "level": level,
        "label": label,
        "modifiers": data.get("modifiers", {})
    }

# Modify the tension level for a region based on a specific source
def modify_tension(region_id, source, amount):
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {"level": 0, "modifiers": {}}

    modifiers = data.get("modifiers", {})
    modifiers[source] = modifiers.get(source, 0) + amount

    level_sum = max(0, min(sum(modifiers.values()), 100))

    data.update({
        "level": level_sum,
        "modifiers": modifiers,
        "last_modified": datetime.utcnow().isoformat()
    })
    ref.set(data)

    return get_tension(region_id)

# Reset tension to default state
def reset_tension(region_id):
    ref = db.reference(f"/regions/{region_id}/tension")
    ref.set({
        "level": 0,
        "modifiers": {},
        "last_modified": datetime.utcnow().isoformat()
    })
    return get_tension(region_id)

# Gradually decay the tension level over time
def decay_tension(region_id, decay_rate=1):
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {}
    if not data:
        return {"error": "No tension data for this region"}

    modifiers = data.get("modifiers", {})
    updated_modifiers = {}
    for k, v in modifiers.items():
        if abs(v) > decay_rate:
            updated_modifiers[k] = v - decay_rate if v > 0 else v + decay_rate

    level_sum = max(0, min(sum(updated_modifiers.values()), 100))

    data.update({
        "level": level_sum,
        "modifiers": updated_modifiers,
        "last_modified": datetime.utcnow().isoformat()
    })
    ref.set(data)

    return get_tension(region_id)

# Placeholder for Flask Routes
# Add your Flask route functions here if integrating directly
