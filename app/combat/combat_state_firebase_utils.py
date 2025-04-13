from datetime import datetime
from firebase_admin import db
from app.combat.ai_combat_utils import roll_initiative
from app.combat.status_effects_utils import apply_status_effect, resolve_status_effects
import random

def apply_combat_action(
    battle_id, actor_id, target_id, action_type, roll, value, notes="",
    status_effect=None, spell_name=None
):
    ref = db.reference(f"/combat_state/{battle_id}")
    combat_data = ref.get()

    if not combat_data:
        return {"error": "Battle not found."}, 404

    current_turn = combat_data.get("current_turn", 0)
    turn_order = combat_data.get("turn_order", [])
    if turn_order[current_turn] != actor_id:
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
        damage = max(0, value)
        target["HP"] = max(0, target["HP"] - damage)
        narration += f" and hits {target['name']} for {damage} damage!"
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

    combat_data["current_turn"] = (current_turn + 1) % len(turn_order)
    ref.set(combat_data)

    return {
        "result": narration,
        "updated_target": target,
        "next_turn": turn_order[combat_data["current_turn"]],
        "log": combat_data["log"][-5:]
    }, 200


def start_firebase_combat(encounter_name, player_party, enemy_party, battle_map=None):
    battle_id = str(random.randint(100000, 999999))
    participants = {}

    for char in player_party + enemy_party:
        participants[char["id"]] = {
            "name": char["name"],
            "team": "party" if char in player_party else "hostile",
            "HP": char.get("HP", 20),
            "AC": char.get("AC", 12),
            "DEX": char.get("DEX", 10),
            "initiative": roll_initiative(char.get("DEX", 10)),
            "status_effects": []
        }

    sorted_order = sorted(participants, key=lambda pid: participants[pid]["initiative"], reverse=True)

    combat_state = {
        "battle_id": battle_id,
        "name": encounter_name,
        "participants": participants,
        "turn_order": sorted_order,
        "current_turn": 0,
        "battle_map": battle_map or {"type": "open", "lighting": "normal"},
        "started_at": datetime.utcnow().isoformat(),
        "log": []
    }

    db.reference(f"/combat_state/{battle_id}").set(combat_state)

    return battle_id, combat_state
