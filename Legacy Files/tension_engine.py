from firebase_admin import db
from datetime import datetime

TENSION_LEVELS = [
    (0, 10, "peaceful"),
    (11, 30, "watchful"),
    (31, 60, "anxious"),
    (61, 80, "violent"),
    (81, 100, "collapsing")
]

def get_tension_descriptor(level):
    for min_val, max_val, label in TENSION_LEVELS:
        if min_val <= level <= max_val:
            return label
    return "unknown"

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

def modify_tension(region_id, source, amount):
    """
    Adjust regional tension by a numeric amount (positive or negative).
    Records the source modifier.
    """
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get() or {"level": 0, "modifiers": {}}

    modifiers = data.get("modifiers", {})
    modifiers[source] = modifiers.get(source, 0) + amount
    level = sum(modifiers.values())
    level = max(0, min(level, 100))  # clamp

    data.update({
        "level": level,
        "modifiers": modifiers,
        "last_modified": datetime.utcnow().isoformat()
    })
    ref.set(data)

    return get_tension(region_id)

def reset_tension(region_id):
    ref = db.reference(f"/regions/{region_id}/tension")
    ref.set({
        "level": 0,
        "modifiers": {},
        "last_modified": datetime.utcnow().isoformat()
    })
    return get_tension(region_id)

def decay_tension(region_id, decay_rate=1):
    """
    Gradually reduce tension modifiers over time.
    """
    ref = db.reference(f"/regions/{region_id}/tension")
    data = ref.get()
    if not data:
        return {"error": "Region not found"}

    modifiers = data.get("modifiers", {})
    updated = {}
    for k, v in modifiers.items():
        if abs(v) > decay_rate:
            updated[k] = v - decay_rate if v > 0 else v + decay_rate

    level = sum(updated.values())
    level = max(0, min(level, 100))

    data.update({
        "level": level,
        "modifiers": updated,
        "last_modified": datetime.utcnow().isoformat()
    })
    ref.set(data)

    return get_tension(region_id)
