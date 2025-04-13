from datetime import datetime
from firebase_admin import db

def apply_status(combatant, effect_name, duration=3, source=None):
    effect = {
        "name": effect_name,
        "duration": duration,
        "applied_by": source,
        "timestamp": datetime.utcnow().isoformat()
    }

    combatant.status_effects.append(effect)
    combatant.stats["status_effects"] = combatant.status_effects

    if duration > 20:
        db.reference(f"/npcs/{combatant.character_id}/status_effects").push(effect)


def tick_status_effects(combatant):
    updated = []
    for effect in combatant.status_effects:
        effect["duration"] -= 1
        if effect["duration"] > 0:
            updated.append(effect)
    combatant.status_effects = updated
    combatant.stats["status_effects"] = updated
