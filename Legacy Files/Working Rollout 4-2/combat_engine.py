from firebase_admin import db
from datetime import datetime
import uuid
import random
from openai import ChatCompletion

def roll_initiative(DEX):
    return random.randint(1, 20) + ((DEX - 10) // 2)

def start_combat(encounter_name, player_party, enemy_party, battle_map=None):
    battle_id = str(uuid.uuid4())
    all_participants = {}

    # Add players
    for pc in player_party:
        all_participants[pc["id"]] = {
            "name": pc["name"],
            "team": "party",
            "HP": pc.get("HP", 20),
            "AC": pc.get("AC", 12),
            "DEX": pc.get("DEX", 10),
            "initiative": roll_initiative(pc.get("DEX", 10)),
            "status_effects": [],
        }

    # Add enemies
    for npc in enemy_party:
        all_participants[npc["id"]] = {
            "name": npc["name"],
            "team": "hostile",
            "HP": npc.get("HP", 20),
            "AC": npc.get("AC", 12),
            "DEX": npc.get("DEX", 10),
            "initiative": roll_initiative(npc.get("DEX", 10)),
            "status_effects": [],
        }

    # Sort turn order
    turn_order = sorted(all_participants.items(), key=lambda kv: kv[1]["initiative"], reverse=True)
    turn_order_ids = [pid for pid, _ in turn_order]

    combat_state = {
        "battle_id": battle_id,
        "name": encounter_name,
        "participants": all_participants,
        "turn_order": turn_order_ids,
        "current_turn": 0,
        "battle_map": battle_map or {"type": "open", "lighting": "normal"},
        "started_at": datetime.utcnow().isoformat(),
        "log": []
    }

    db.reference(f"/combat_state/{battle_id}").set(combat_state)
    return battle_id, combat_state

def combat_tick(battle_id):
    import openai
    import json

    ref = db.reference(f"/combat_state/{battle_id}")
    combat_data = ref.get()

    if not combat_data:
        return {"error": "Battle not found."}, 404

    turn_order = combat_data["turn_order"]
    current_index = combat_data.get("current_turn", 0)
    acting_id = turn_order[current_index]
    actor = combat_data["participants"].get(acting_id)

    if not actor:
        return {"error": "Invalid actor ID."}, 400

    # === PLAYER TURN ===
    if actor["team"] == "party":
        combat_data["log"].append(f"It is now {actor['name']}'s turn.")
        combat_data["current_turn"] = (current_index + 1) % len(turn_order)
        ref.set(combat_data)

        return {
            "acting_id": acting_id,
            "action": f"Waiting for player action ({actor['name']})",
            "log": combat_data["log"][-5:]
        }, 200

    # === NPC TURN → GPT DECISION ===
    participants = combat_data["participants"]
    context_lines = [
        f"{p['name']} (HP: {p['HP']}, Team: {p['team']})"
        for p in participants.values()
    ]
    context = "\n".join(context_lines)

    prompt = (
        f"You are controlling the NPC named {actor['name']} in a turn-based fantasy RPG battle.\n"
        f"Here are the combatants:\n{context}\n\n"
        f"Choose a reasonable action as JSON like:\n"
        f"{{\"action\": \"attack\", \"target\": \"player_1\", \"roll\": 17, \"value\": 9, \"notes\": \"slashes with scimitar\"}}\n\n"
        f"ONLY return the JSON."
    )

    try:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an NPC tactician in a fantasy battle."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        content = gpt_response.choices[0].message.content.strip()
        parsed = json.loads(content)

        # Extract values from GPT's structured response
        action_type = parsed.get("action", "attack")
        target_id = parsed.get("target")
        roll = parsed.get("roll", 10)
        value = parsed.get("value", 0)
        notes = parsed.get("notes", "")
        status_effect = parsed.get("status_effect")
        spell_name = parsed.get("spell_name")
        spell_level = parsed.get("spell_level")

        from combat_engine import apply_combat_action
        result, status = apply_combat_action(
            battle_id, acting_id, target_id, action_type, roll, value,
            notes, status_effect, spell_name, spell_level
        )
        return result, status

    except Exception as e:
        # Fallback: NPC hesitates
        fallback_log = f"{actor['name']} hesitates, unsure what to do. ({str(e)})"
        combat_data["log"].append(fallback_log)
        combat_data["current_turn"] = (current_index + 1) % len(turn_order)
        ref.set(combat_data)

        return {
            "acting_id": acting_id,
            "action": fallback_log,
            "log": combat_data["log"][-5:]
        }, 200


def apply_combat_action(battle_id, actor_id, target_id, action_type, roll, value, notes="", status_effect=None, spell_name=None):
    ref = db.reference(f"/combat_state/{battle_id}")
    combat_data = ref.get()

    if not combat_data:
        return {"error": "Battle not found."}, 404

    current_index = combat_data.get("current_turn", 0)
    turn_order = combat_data.get("turn_order", [])
    if turn_order[current_index] != actor_id:
        return {"error": "It's not this character's turn."}, 400

    participants = combat_data["participants"]

    if actor_id not in participants or target_id not in participants:
        return {"error": "Invalid actor or target ID."}, 400

    actor = participants[actor_id]
    target = participants[target_id]

    narration = f"{actor['name']} uses {action_type}"
    if spell_name:
        narration = f"{actor['name']} casts {spell_name}"

    # === Handle result logic ===
    if action_type == "attack" and roll >= target.get("AC", 10):
        target["HP"] = max(0, target["HP"] - value)
        narration += f" and hits {target['name']} for {value} damage!"
    elif action_type == "heal":
        target["HP"] = target.get("HP", 0) + value
        narration += f" and heals {target['name']} for {value} HP!"
    else:
        narration += " but it fails."

    # === Handle status effect ===
    if status_effect:
        effect_obj = {"type": status_effect, "duration": 2}
        target.setdefault("status_effects", []).append(effect_obj)
        narration += f" {target['name']} is now {status_effect}!"

    if notes:
        narration += f" ({notes})"

    combat_data["participants"][target_id] = target
    combat_data.setdefault("log", []).append(narration)

    # === Tick status effects for all participants ===
    for p_id, pdata in participants.items():
        updated = []
        expired = []
        for effect in pdata.get("status_effects", []):
            effect["duration"] -= 1
            if effect["duration"] > 0:
                updated.append(effect)
            else:
                expired.append(effect["type"])
        pdata["status_effects"] = updated
        if expired:
            combat_data["log"].append(f"{pdata['name']} is no longer affected by {', '.join(expired)}.")

    # Advance turn
    combat_data["current_turn"] = (current_index + 1) % len(turn_order)
    ref.set(combat_data)

    return {
        "result": narration,
        "updated_target": target,
        "turn_advanced_to": combat_data["turn_order"][combat_data["current_turn"]],
        "log": combat_data["log"][-5:]
    }, 200
