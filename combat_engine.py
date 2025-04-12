# combat_engine.py

from flask import Blueprint, request, jsonify
from firebase_admin import db
import random
from datetime import datetime

combat_bp = Blueprint("combat_bp", __name__)
__all__ = ["combat_bp", "start_combat", "apply_status_effect", "resolve_status_effects", "handle_cooldowns", "resolve_saving_throw"]

# -------------------------------
# Status Effects & Utilities
# -------------------------------

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
        return {"error": "NPC not found."}
    cooldowns = npc.get("cooldowns", {})
    for key in list(cooldowns.keys()):
        cooldowns[key] = max(0, cooldowns[key] - 1)
        if cooldowns[key] == 0:
            del cooldowns[key]
    npc["cooldowns"] = cooldowns
    ref.set(npc)
    return cooldowns

def resolve_saving_throw(stat_mod, dc):
    roll = random.randint(1, 20) + stat_mod
    return {"roll": roll, "modifier": stat_mod, "dc": dc, "success": roll >= dc}

def roll_initiative(dexterity):
    return random.randint(1, 20) + ((dexterity - 10) // 2)

# -------------------------------
# Core Combat Functions
# -------------------------------

def choose_action(attacker, targets):
    role = attacker.get("role", "fighter")
    hp = attacker.get("HP", 10)

    if hp < 5 and role != "tank":
        return "flee"

    if role == "healer":
        low_hp_allies = [t for t in targets if t["team"] == attacker["team"] and t["HP"] < 6]
        return "heal" if low_hp_allies else "support"

    if role == "caster":
        return random.choice(["cast", "blast", "defend"])

    if role == "rogue":
        return random.choice(["stab", "hide", "backstab"])

    return random.choice(["strike", "defend", "cleave"])

def apply_combat_action(
    battle_id, actor_id, target_id, action_type, roll, value, notes="",
    status_effect=None, spell_name=None, spell_level=None
):
    ref = db.reference(f"/combat_state/{battle_id}")
    combat_data = ref.get()
    if not combat_data:
        return {"error": "Battle not found."}, 404

    current_index = combat_data.get("current_turn", 0)
    turn_order = combat_data.get("turn_order", [])
    if turn_order[current_index] != actor_id:
        return {"error": "It's not this character's turn."}, 400

    participants = combat_data["participants"]
    actor = participants.get(actor_id)
    target = participants.get(target_id)

    if not actor or not target:
        return {"error": "Invalid actor or target ID."}, 400

    narration = f"{actor['name']} uses {action_type}"
    if spell_name:
        narration = f"{actor['name']} casts {spell_name}"

    if action_type == "attack" and roll >= target.get("AC", 10):
        target["HP"] = max(0, target["HP"] - value)
        narration += f" and hits {target['name']} for {value} damage!"
    elif action_type == "heal":
        target["HP"] += value
        narration += f" and heals {target['name']} for {value} HP!"
    else:
        narration += " but it fails."

    if status_effect:
        apply_status_effect(target_id, status_effect, 2, actor_id)
        narration += f" {target['name']} is now {status_effect}!"

    if notes:
        narration += f" ({notes})"

    combat_data["participants"][target_id] = target
    combat_data.setdefault("log", []).append(narration)

    for p_id in participants:
        resolve_status_effects(p_id)

    combat_data["current_turn"] = (current_index + 1) % len(turn_order)
    ref.set(combat_data)

    return {
        "result": narration,
        "updated_target": target,
        "turn_advanced_to": turn_order[combat_data["current_turn"]],
        "log": combat_data["log"][-5:]
    }, 200

def simulate_tactical_combat_round(combatants):
    sorted_combatants = sorted(combatants, key=lambda c: roll_initiative(c.get("DEX", 10)), reverse=True)
    combat_log = []

    for attacker in sorted_combatants:
        if attacker.get("HP", 0) <= 0:
            continue

        targets = [c for c in sorted_combatants if c["team"] != attacker["team"] and c.get("HP", 0) > 0]
        if not targets:
            combat_log.append(f"{attacker['name']} has no targets.")
            continue

        target = random.choice(targets)
        action = "attack"
        log = apply_combat_action("demo", attacker["id"], target["id"], action, random.randint(1, 20), random.randint(4, 12))[0]["result"]
        combat_log.append(log)

    return {"combatants": sorted_combatants, "combat_log": combat_log}

def start_combat(encounter_name, player_party, enemy_party, battle_map=None):
    battle_id = str(random.randint(100000, 999999))
    participants = {}

    for pc in player_party:
        participants[pc["id"]] = {
            "name": pc["name"],
            "team": "party",
            "HP": pc.get("HP", 20),
            "AC": pc.get("AC", 12),
            "DEX": pc.get("DEX", 10),
            "initiative": roll_initiative(pc.get("DEX", 10)),
            "status_effects": [],
        }

    for npc in enemy_party:
        participants[npc["id"]] = {
            "name": npc["name"],
            "team": "hostile",
            "HP": npc.get("HP", 20),
            "AC": npc.get("AC", 12),
            "DEX": npc.get("DEX", 10),
            "initiative": roll_initiative(npc.get("DEX", 10)),
            "status_effects": [],
        }

    turn_order = sorted(participants.items(), key=lambda kv: kv[1]["initiative"], reverse=True)
    turn_order_ids = [pid for pid, _ in turn_order]

    combat_state = {
        "battle_id": battle_id,
        "name": encounter_name,
        "participants": participants,
        "turn_order": turn_order_ids,
        "current_turn": 0,
        "battle_map": battle_map or {"type": "open", "lighting": "normal"},
        "started_at": datetime.utcnow().isoformat(),
        "log": []
    }
    db.reference(f"/combat_state/{battle_id}").set(combat_state)
    return battle_id, combat_state

# -------------------------------
# Flask Routes
# -------------------------------

@combat_bp.route('/combat_round', methods=['POST'])
def combat_round():
    data = request.get_json(force=True)
    combatants = data.get("combatants", [])
    if not combatants or not isinstance(combatants, list):
        return jsonify({"error": "A combatants list is required."}), 400
    result = simulate_tactical_combat_round(combatants)
    return jsonify(result)

@combat_bp.route('/long_rest/<character_id>', methods=['POST'])
def route_long_rest(character_id):
    ref = db.reference(f"/players/{character_id}")
    data = ref.get()

    if not data or "spell_slots" not in data:
        return jsonify({"error": "Character not found or has no spell slots"}), 404

    for level_info in data["spell_slots"].values():
        level_info["used"] = 0

    ref.update({"spell_slots": data["spell_slots"]})
    return jsonify({
        "message": f"{data.get('character_name', 'Character')} has completed a long rest.",
        "spell_slots": data["spell_slots"]
    })
