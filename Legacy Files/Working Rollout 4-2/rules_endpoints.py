from flask import Blueprint, request, jsonify
from rules_engine import (
    validate_character_creation,
    resolve_skill_check,
    resolve_combat_action,
    lookup_rule,
    lookup_spell
)

rules_bp = Blueprint('rules', __name__)

@rules_bp.route('/validate_character_creation', methods=['POST'])
def validate_character():
    data = request.json
    if not data:
        return jsonify({"error": "Missing character data"}), 400
    result = validate_character_creation(data)
    return jsonify(result)

@rules_bp.route('/resolve_skill_check', methods=['POST'])
def resolve_skill():
    data = request.json
    skill = data.get("skill")
    ability_score = data.get("ability_score", 10)
    modifiers = data.get("modifiers", [])
    dc = data.get("dc", 10)

    if not skill:
        return jsonify({"error": "Missing skill name"}), 400

    result = resolve_skill_check(skill, ability_score, modifiers, dc)
    return jsonify(result)

@rules_bp.route('/resolve_combat_action', methods=['POST'])
def resolve_combat():
    data = request.json
    attacker = data.get("attacker", {})
    defender = data.get("defender", {})
    roll = data.get("roll", 10)

    result = resolve_combat_action(attacker, defender, roll)
    return jsonify(result)

@rules_bp.route('/lookup_rule', methods=['GET'])
def rule_lookup():
    category = request.args.get("category")
    name = request.args.get("name")

    if not category or not name:
        return jsonify({"error": "Missing category or name"}), 400

    result = lookup_rule(category, name)
    if not result:
        return jsonify({"error": f"{name} not found in {category}"}), 404
    return jsonify(result)

@rules_bp.route('/lookup_spell', methods=['GET'])
def spell_lookup():
    level = request.args.get("level")
    name = request.args.get("name")

    if not level or not name:
        return jsonify({"error": "Missing spell level or name"}), 400

    result = lookup_spell(level, name)
    if not result:
        return jsonify({"error": f"{name} not found at level {level}"}), 404
    return jsonify(result)

@rules_bp.route('/log_event_and_notify_npcs', methods=['POST'])
def log_event_and_notify():
    from rules_engine import log_world_event, sync_event_beliefs

    data = request.json
    if not data:
        return jsonify({"error": "Missing event data"}), 400

    region = data.get("region")
    if not region:
        return jsonify({"error": "Missing region name"}), 400

    try:
        event = log_world_event(data)
        count = sync_event_beliefs(region, event)
        return jsonify({
            "message": f"Event logged and shared with {count} NPCs.",
            "event_id": event["event_id"],
            "region": region
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ Properly defined, clean, non-duplicate route
@rules_bp.route('/start_combat', methods=['POST'])
def api_start_combat():
    from combat_engine import start_combat

    data = request.json
    encounter_name = data.get("encounter_name", "Unnamed Encounter")
    player_party = data.get("player_party", [])
    enemy_party = data.get("enemy_party", [])
    battle_map = data.get("battle_map", {})

    if not player_party or not enemy_party:
        return jsonify({"error": "Both player_party and enemy_party are required"}), 400

    battle_id, combat_data = start_combat(encounter_name, player_party, enemy_party, battle_map)
    return jsonify({"battle_id": battle_id, "combat": combat_data})

@rules_bp.route('/combat_action', methods=['POST'])
def api_combat_action():
    from combat_engine import apply_combat_action

    data = request.json
    battle_id = data.get("battle_id")
    actor_id = data.get("actor_id")
    target_id = data.get("target_id")
    action_type = data.get("action", "attack")
    roll = data.get("roll", 10)
    value = data.get("value", 0)
    notes = data.get("notes", "")
    status_effect = data.get("status_effect")  # NEW
    spell_name = data.get("spell_name")        # NEW
    spell_level = data.get("spell_level")      # NEW

    if not all([battle_id, actor_id, target_id]):
        return jsonify({"error": "Missing required fields."}), 400

    result, status = apply_combat_action(
        battle_id, actor_id, target_id, action_type, roll, value,
        notes, status_effect, spell_name, spell_level
    )
    return jsonify(result), status

@rules_bp.route('/long_rest/<player_id>', methods=['POST'])
def long_rest(player_id):
    ref = db.reference(f"/players/{player_id}")
    data = ref.get()

    if not data or "spell_slots" not in data:
        return jsonify({"error": "Character not found or has no spell slots"}), 404

    for level, slot in data["spell_slots"].items():
        slot["used"] = 0

    ref.set(data)

    return jsonify({
        "message": f"{data.get('character_name', 'Character')} has completed a long rest.",
        "spell_slots": data["spell_slots"]
    })

@rules_bp.route('/request_rest', methods=['POST'])
def request_rest():
    import openai

    data = request.json
    player_id = data.get("player_id")
    location_description = data.get("location_description", "")
    current_threats = data.get("threats", [])
    narrative_context = data.get("narrative_context", "")

    if not player_id:
        return jsonify({"error": "Missing player_id"}), 400

    prompt = (
        f"The player is attempting to take a long rest.\n"
        f"Location: {location_description}\n"
        f"Threats nearby: {', '.join(current_threats) if current_threats else 'None'}\n"
        f"Context: {narrative_context}\n\n"
        f"Reply in the following format:\n"
        f"{{\"decision\": \"yes\" or \"no\", \"narration\": \"a short narrative describing why\"}}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fantasy RPG narrator deciding if a rest is safe."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=100
        )

        content = response.choices[0].message.content.strip()

        # Safe fallback
        import json
        try:
            result = json.loads(content)
            decision = result.get("decision", "").lower()
            narration = result.get("narration", "No narration provided.")
        except:
            decision = "no"
            narration = "You try to rest, but the forest feels uneasy..."

        if "yes" in decision:
            # Grant rest
            from firebase_admin import db
            ref = db.reference(f"/players/{player_id}")
            data = ref.get()

            if not data or "spell_slots" not in data:
                return jsonify({"error": "Character not found or has no spell slots"}), 404

            for level, slot in data["spell_slots"].items():
                slot["used"] = 0
            ref.set(data)

            return jsonify({
                "result": "Long rest granted.",
                "narration": narration,
                "spell_slots": data["spell_slots"]
            })

        else:
            return jsonify({
                "result": "Rest denied",
                "narration": narration
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rules_bp.route('/recruit_npc', methods=['POST'])
def recruit_npc():
    from party_engine import create_party, add_to_party

    data = request.json
    player_id = data.get("player_id")
    npc_id = data.get("npc_id")

    player_ref = db.reference(f"/players/{player_id}")
    npc_ref = db.reference(f"/npcs/{npc_id}")

    player = player_ref.get()
    npc = npc_ref.get()

    if not player or not npc:
        return jsonify({"error": "Invalid player or NPC ID"}), 400

    existing_party = player.get("party_id")
    if existing_party:
        success = add_to_party(existing_party, npc_id)
    else:
        existing_party = create_party(player_id, [npc_id])

    return jsonify({
        "message": f"{npc['character_name']} has joined your party!",
        "party_id": existing_party
    })

@rules_bp.route('/npc_loyalty_tick', methods=['POST'])
def npc_loyalty_tick():
    from loyalty_engine import loyalty_tick

    data = request.json
    npc_id = data.get("npc_id")
    player_id = data.get("player_id")
    cha_score = data.get("cha", 10)

    if not npc_id or not player_id:
        return jsonify({"error": "Missing npc_id or player_id"}), 400

    result = loyalty_tick(npc_id, player_id, cha_score=cha_score)
    return jsonify(result)

@rules_bp.route('/tension/<region_id>', methods=['GET'])
def api_get_tension(region_id):
    from tension_engine import get_tension
    return jsonify(get_tension(region_id))

@rules_bp.route('/tension/modify', methods=['POST'])
def api_modify_tension():
    from tension_engine import modify_tension
    data = request.json
    region_id = data.get("region_id")
    source = data.get("source")
    amount = data.get("amount", 0)

    if not region_id or not source:
        return jsonify({"error": "Missing region_id or source"}), 400

    return jsonify(modify_tension(region_id, source, amount))

@rules_bp.route('/tension/reset/<region_id>', methods=['POST'])
def api_reset_tension(region_id):
    from tension_engine import reset_tension
    return jsonify(reset_tension(region_id))

@rules_bp.route('/tension/decay/<region_id>', methods=['POST'])
def api_decay_tension(region_id):
    from tension_engine import decay_tension
    return jsonify(decay_tension(region_id))

@rules_bp.route('/npc/travel/<npc_id>', methods=['POST'])
def npc_travel(npc_id):
    from mobility_engine import update_npc_location
    return jsonify(update_npc_location(npc_id))

@rules_bp.route('/propagate_beliefs/<region_id>', methods=['POST'])
def rumor_propagation(region_id):
    from rumor_engine import propagate_beliefs
    result = propagate_beliefs(region_id)
    return jsonify({"messages": result, "region": region_id})

@rules_bp.route('/npc_motif_tick/<npc_id>', methods=['POST'])
def tick_motifs(npc_id):
    from motif_engine import tick_npc_motifs
    return jsonify(tick_npc_motifs(npc_id))

@rules_bp.route('/npc_relationship_tick', methods=['POST'])
def api_npc_relationship_tick():
    from relationship_engine import daily_relationship_tick
    daily_relationship_tick()
    return jsonify({"status": "NPC relationships updated"})