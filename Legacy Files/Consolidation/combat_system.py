import random
import uuid
from datetime import datetime
import openai
import json
from firebase_admin import db

def roll_initiative(DEX):
    return random.randint(1, 20) + ((DEX - 10) // 2)

def start_combat(encounter_name, player_party, enemy_party, battle_map=None):
    battle_id = str(uuid.uuid4())
    participants = {}

    for pc in player_party:
        participants[pc["id"]] = {"name": pc["name"], "team": "party", "HP": pc.get("HP", 20), "AC": pc.get("AC", 12), "initiative": roll_initiative(pc.get("DEX", 10))}

    for npc in enemy_party:
        participants[npc["id"]] = {"name": npc["name"], "team": "hostile", "HP": npc.get("HP", 20), "AC": npc.get("AC", 12), "initiative": roll_initiative(npc.get("DEX", 10))}

    turn_order = sorted(participants.items(), key=lambda kv: kv[1]["initiative"], reverse=True)

    combat_state = {
        "battle_id": battle_id,
        "name": encounter_name,
        "participants": participants,
        "turn_order": [pid for pid, _ in turn_order],
        "current_turn": 0,
        "started_at": datetime.utcnow().isoformat(),
        "log": []
    }

    db.reference(f"/combat_state/{battle_id}").set(combat_state)
    return battle_id, combat_state

def combat_tick(battle_id):
    ref = db.reference(f"/combat_state/{battle_id}")
    combat_data = ref.get()

    current_turn = combat_data["turn_order"][combat_data["current_turn"]]
    actor = combat_data["participants"][current_turn]

    if actor["team"] == "party":
        combat_data["log"].append(f"It's {actor['name']}'s turn.")
        combat_data["current_turn"] = (combat_data["current_turn"] + 1) % len(combat_data["turn_order"])
        ref.set(combat_data)
        return

    context = "\n".join([f"{p['name']} (HP: {p['HP']}, AC: {p['AC']})" for p in combat_data["participants"].values()])

    prompt = f"NPC {actor['name']} decides an action in combat. Combatants:\n{context}\nReturn JSON with action, target, roll, value."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150
    )

    decision = json.loads(response.choices[0].message.content.strip())

    apply_combat_action(battle_id, current_turn, decision["target"], decision["action"], decision["roll"], decision["value"])

def apply_combat_action(battle_id, actor_id, target_id, action_type, roll, value):
    ref = db.reference(f"/combat_state/{battle_id}")
    combat_data = ref.get()

    actor = combat_data["participants"][actor_id]
    target = combat_data["participants"][target_id]

    narration = f"{actor['name']} {action_type}s {target['name']}"

    if action_type == "attack" and roll >= target["AC"]:
        target["HP"] = max(0, target["HP"] - value)
        narration += f" and hits for {value} damage!"
    else:
        narration += " but misses."

    combat_data["log"].append(narration)

    combat_data["current_turn"] = (combat_data["current_turn"] + 1) % len(combat_data["turn_order"])
    ref.set(combat_data)

def resolve_combat_action(attacker, defender, roll):
    attack_total = roll + attacker.get("base_attack_bonus", 0) + attacker.get("strength_modifier", 0)
    hit = attack_total >= defender.get("armor_class", 10)
    return {"roll": roll, "attack_total": attack_total, "hit": hit}