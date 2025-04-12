from firebase_admin import db
from datetime import datetime, timedelta
import random

def apply_status_effect(target_id, effect_name, duration, source_id=None):
    ref = db.reference(f"/npcs/{target_id}")
    npc = ref.get()
    if not npc:
        return {"error": f"NPC {target_id} not found."}

    current_effects = npc.get("status_effects", [])
    effect_entry = {
        "name": effect_name,
        "duration": duration,
        "applied_by": source_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    current_effects.append(effect_entry)
    npc["status_effects"] = current_effects
    ref.set(npc)
    return {"status": "applied", "npc_id": target_id, "effect": effect_entry}

def resolve_status_effects(npc_id):
    ref = db.reference(f"/npcs/{npc_id}")
    npc = ref.get()
    if not npc:
        return {"error": f"NPC {npc_id} not found."}

    effects = npc.get("status_effects", [])
    updated_effects = []
    for effect in effects:
        effect["duration"] -= 1
        if effect["duration"] > 0:
            updated_effects.append(effect)

    npc["status_effects"] = updated_effects
    ref.set(npc)
    return {"npc_id": npc_id, "remaining_effects": updated_effects}

def handle_cooldowns(npc_id):
    ref = db.reference(f"/npcs/{npc_id}")
    npc = ref.get()
    if not npc:
        return {"error": f"NPC {npc_id} not found."}

    cooldowns = npc.get("cooldowns", {})
    for key in list(cooldowns.keys()):
        cooldowns[key] = max(0, cooldowns[key] - 1)
        if cooldowns[key] == 0:
            del cooldowns[key]

    npc["cooldowns"] = cooldowns
    ref.set(npc)
    return {"npc_id": npc_id, "cooldowns": cooldowns}

def resolve_saving_throw(stat_mod, dc):
    roll = random.randint(1, 20) + stat_mod
    success = roll >= dc
    return {"roll": roll, "modifier": stat_mod, "dc": dc, "success": success}
