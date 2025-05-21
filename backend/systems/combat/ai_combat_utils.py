
#This module handles combat AI logic, including action selection (via GPT), validation against MP and feat requirements, and deterministic resolution of those actions. It interfaces deeply with gpt, combat rules, and asset logic, and lightly touches on character attributes and battlefield context.

import json
from app.rules.character_gen_rules_utils import load_feat_data
import random  # if needed by helper logic
import openai
from firebase_admin import db

with open("rules_json/feats.json") as f:
    ALL_FEATS = {feat["name"]: feat for feat in json.load(f)}

def lookup_actions_for_combatant(feats, combatant, battlefield_context):
    all_feats = load_feat_data()
    mp = combatant.get("MP", 0)
    attributes = combatant.get("attributes", {})
    has_weapon = "equipment" in combatant and len(combatant["equipment"]) > 0

    actions = []

    for feat_name in feats:
        feat = all_feats.get(feat_name)
        if not feat:
            continue

        # Safely handle null MP cost
        mp_cost = feat.get("mp_cost") or 0
        if mp_cost > mp:
            continue

        # Weapon requirement check
        if feat.get("requires_weapon") and not has_weapon:
            continue

        # Add basic info for GPT
        actions.append({
            "name": feat_name,
            "mp_cost": mp_cost,
            "requires_weapon": feat.get("requires_weapon", False),
            "description": feat.get("effect", feat.get("description", "")),
            "damage": feat.get("parsed_mechanics", {}).get("damage", False),
            "category": feat.get("category"),
            "tags": feat.get("tags", []),
            "action_type": feat.get("action_type", "Action")
        })

    from app.rules.rules_utils import load_core_actions

    # Always include a fallback
    actions.append({
        "name": "basic_attack",
        "mp_cost": 0,
        "requires_weapon": False,
        "description": "Simple physical strike using equipped weapon or unarmed attack.",
        "damage": True,
        "category": "attack",
        "tags": ["fallback"],
        "action_type": "Action"
    })

    actions += load_core_actions()

    return actions



def choose_action_gpt(npc, opponents, battlefield_context):
    npc_id = npc.get("id") or npc.get("npc_id")
    npc_faction = npc.get("faction", "Unaffiliated")
    npc_name = npc.get("name", npc_id)

    # 🔍 Load traits and trust
    npc_data = db.reference(f"/npcs/{npc_id}").get() or {}
    npc_traits = npc_data.get("traits", [])  # Expecting a list: ["cowardly", "loyal", "reckless"]
    trait_summary = ", ".join(npc_traits) if npc_traits else "no strong personality traits"

    # 🧠 Load opinion matrix
    opinion_data = db.reference(f"/npc_opinion_matrix/{npc_id}").get() or {}

    # 🧩 Opponent summary
    opponent_descriptions = []
    for opp in opponents:
        opp_id = opp.get("id")
        opp_faction = opp.get("faction", "Unaffiliated")
        trust_score = opinion_data.get(opp_id, 0)
        line = f"{opp.get('name', opp_id)} (Faction: {opp_faction}, Trust: {trust_score})"
        opponent_descriptions.append(line)
    opponent_summary = "\n".join(opponent_descriptions)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an intelligent NPC combat AI in a fantasy RPG."},
                {"role": "user", "content": (
                    f"{npc_name} belongs to the faction '{npc_faction}' and has the traits: {trait_summary}.\n"
                    f"Opponents:\n{opponent_summary}\n\n"
                    f"Battlefield context: {json.dumps(battlefield_context)}\n\n"
                    "Choose an action that aligns with their traits and current situation. Respond with JSON like:\n"
                    '{"type": "Attack", "target": "npc_1234", "mp_cost": 0, "damage": 12}'
                )}
            ],
            temperature=0.65,
            max_tokens=150
        )
        action_json = response.choices[0].message.content.strip()
        return json.loads(action_json)

    except Exception as e:
        print(f"[GPT FAIL] {e}")
        return fallback_combat_action(npc, opponents)

def fallback_combat_action(actor, opponents):
    target = random.choice(opponents)
    return {
        "type": "Attack",
        "target": target["id"],
        "mp_cost": 0,
        "damage": actor.get("attributes", {}).get("STR", 3) + 1
    }

def resolve_combat_action(attacker, action_data, battlefield_context):
    """
    Resolves a basic attack or ability from a combatant.
    Args:
        attacker (dict): The acting NPC or player
        action_data (dict): The GPT-decided action (intent, ability, target)
        battlefield_context (dict): Battlefield attributee

    Returns:
        dict: outcome with hit, damage, and description
    """
    target_id = action_data.get("target")
    ability = action_data.get("ability", "basic_attack")

    target = next((e for e in battlefield_context.get("enemies", []) if e["id"] == target_id), None)
    if not target:
        return {"hit": False, "error": f"Target {target_id} not found"}

    # Calculate attack roll
    attribute_used = "STR" if attacker["attributes"].get("STR", 10) >= attacker["attributes"].get("DEX", 10) else "DEX"
    attribute_mod = (attacker["attributes"].get(attribute_used, 10) - 10) // 2
    roll = random.randint(1, 20)
    attack_total = roll + attribute_mod

    # Check if hit
    hit = attack_total >= target.get("AC", 10)

    # Damage
    if hit:
        base_damage = random.randint(1, 8)
        damage = base_damage + attribute_mod
    else:
        damage = 0

    return {
        "attacker": attacker["name"],
        "target": target["name"],
        "ability": ability,
        "roll": roll,
        "attack_total": attack_total,
        "hit": hit,
        "damage": damage,
        "damage_type": "slashing" if "cleave" in ability.lower() else "bludgeoning",
        "target_hp": max(0, target["HP"] - damage)
    }