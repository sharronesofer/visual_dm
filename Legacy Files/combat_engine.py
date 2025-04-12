from firebase_admin import db
from datetime import datetime
import uuid
import random
import json
from openai import ChatCompletion
from character_utils import apply_status_effect, resolve_status_effects  # ✅ New

def roll_initiative(DEX):
    return random.randint(1, 20) + ((DEX - 10) // 2)

def choose_action(attacker, targets):
    role = attacker.get("role", "fighter")
    hp = attacker.get("HP", 10)

    if hp < 5 and role != "tank":
        return "flee"

    if role == "healer":
        low_hp_allies = [t for t in targets if t["team"] == attacker["team"] and t["HP"] < 6]
        if low_hp_allies:
            return "heal"
        return "support"

    if role == "caster":
        return random.choice(["cast", "blast", "defend"])

    if role == "rogue":
        return random.choice(["stab", "hide", "backstab"])

    return random.choice(["strike", "defend", "cleave"])

def apply_action(attacker, target, action):
    log = ""
    if action in ["strike", "cleave", "stab", "blast", "backstab"]:
        attack_roll = random.randint(1, 20) + attacker.get("ATK", 3)
        defense = target.get("AC", 10)
        if attack_roll >= defense:
            damage = random.randint(4, 12)
            target["HP"] = max(target["HP"] - damage, 0)
            log = f"{attacker['id']} used {action} on {target['id']} for {damage} dmg. [{target['HP']} HP left]"
        else:
            log = f"{attacker['id']} missed {target['id']} with {action}."

    elif action == "heal":
        heal_amount = random.randint(5, 10)
        target["HP"] += heal_amount
        log = f"{attacker['id']} healed {target['id']} for {heal_amount}. [{target['HP']} HP]"

    elif action == "flee":
        log = f"{attacker['id']} attempts to flee the fight!"

    else:
        log = f"{attacker['id']} holds position with {action}."

    return log

def simulate_tactical_combat_round(combatants):
    combat_log = []
    combatants = sorted(combatants, key=lambda c: roll_initiative(c.get("DEX", 0)), reverse=True)

    for attacker in combatants:
        if attacker.get("HP", 0) <= 0:
            continue

        targets = [c for c in combatants if c["id"] != attacker["id"] and c.get("HP", 0) > 0]
        if not targets:
            combat_log.append(f"{attacker['id']} has no targets.")
            continue

        enemies = [t for t in targets if t["team"] != attacker["team"]]
        target = random.choice(enemies if enemies else targets)

        action = choose_action(attacker, targets)
        log = apply_action(attacker, target, action)
        combat_log.append(log)

    return {
        "combatants": combatants,
        "combat_log": combat_log
    }

def start_combat(encounter_name, player_party, enemy_party, battle_map=None):
    battle_id = str(uuid.uuid4())
    all_participants = {}

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

    # === NPC TURN (GPT-driven) ===
    context_lines = [
        f"{p['name']} (HP: {p['HP']}, Team: {p['team']})"
        for p in combat_data["participants"].values()
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
        gpt_response = ChatCompletion.create(
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

        action_type = parsed.get("action", "attack")
        target_id = parsed.get("target")
        roll = parsed.get("roll", 10)
        value = parsed.get("value", 0)
        notes = parsed.get("notes", "")
        status_effect = parsed.get("status_effect")
        spell_name = parsed.get("spell_name")
        spell_level = parsed.get("spell_level")

        result, status = apply_combat_action(
            battle_id, acting_id, target_id, action_type, roll, value,
            notes, status_effect, spell_name, spell_level
        )
        return result, status

    except Exception as e:
        fallback_log = f"{actor['name']} hesitates. ({str(e)})"
        combat_data["log"].append(fallback_log)
        combat_data["current_turn"] = (current_index + 1) % len(turn_order)
        ref.set(combat_data)
        return {
            "acting_id": acting_id,
            "action": fallback_log,
            "log": combat_data["log"][-5:]
        }, 200

def apply_combat_action(battle_id, actor_id, target_id, action_type, roll, value, notes="", status_effect=None, spell_name=None, spell_level=None):
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

    # === Action outcome ===
    if action_type == "attack" and roll >= target.get("AC", 10):
        target["HP"] = max(0, target["HP"] - value)
        narration += f" and hits {target['name']} for {value} damage!"
    elif action_type == "heal":
        target["HP"] = target.get("HP", 0) + value
        narration += f" and heals {target['name']} for {value} HP!"
    else:
        narration += " but it fails."

    # === Status effect ===
    if status_effect:
        apply_status_effect(target_id, status_effect, 2, actor_id)
        narration += f" {target['name']} is now {status_effect}!"

    if notes:
        narration += f" ({notes})"

    combat_data["participants"][target_id] = target
    combat_data.setdefault("log", []).append(narration)

    # Tick and resolve effects
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
