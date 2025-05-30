
#This module handles procedural world generation tasks, including:
#POI refreshing
#GPT-driven location creation
#Random encounter generation with CR scaling
#Monster selection
#RAM-based combat initiation
#It integrates directly with poi, combat, location, monster rules, gpt, and party systems.

import math
import random
import json
import openai
from uuid import uuid4
from datetime import datetime
from flask import Blueprint, request, jsonify
from firebase_admin import db
from app.combat.combat_utils import initiate_combat
from backend.systems.world_generation.world_generation_utils import refresh_cleared_pois, generate_monsters_for_tile
from app.utils.gpt_class import GPTClient
from app.characters.party_utils import award_xp_to_party
from backend.systems.world_generation.world_generation_utils import generate_region  # Updated import path

worldgen_bp = Blueprint('worldgen', __name__)

@worldgen_bp.route('/refresh_pois', methods=['POST'])
def refresh_pois():
    """
    Checks all POI tiles. If danger level is high and no defenders are present,
    monsters may conquer a POI — unless a faction successfully defends it.
    """
    tile_root = db.reference("/locations").get() or {}
    converted = []

    for coord, tile in tile_root.items():
        danger = tile.get("danger_level", 0)
        poi = tile.get("POI")
        if not poi:
            continue

        region = tile.get("region")
        poi_data = db.reference(f"/poi_state/{region}/{poi}").get() or {}

        # Skip if already hostile
        if poi_data.get("control_status") == "hostile":
            continue

        # Monster attack probability
        attack_chance = danger * 0.1  # 10% per danger point

        # Defensive bonus from faction influence
        influence = poi_data.get("faction_influence", {})
        total_defense = sum(influence.values())
        defense_factor = total_defense * 0.01  # 1% resist per influence point

        adjusted_chance = max(0, attack_chance - defense_factor)

        if random.random() < adjusted_chance:
            # POI is undefended → conquered by ambient monsters
            db.reference(f"/poi_state/{region}/{poi}/control_status").set("hostile")
            db.reference(f"/poi_state/{region}/{poi}/motif_pool/active_motifs").set([
                {"theme": 32, "lifespan": 3, "entropy_tick": 0, "weight": 4}  # chaos
            ])
            db.reference(f"/poi_state/{region}/{poi}/event_log").push({
                "type": "conquered_by_monsters",
                "day": datetime.utcnow().isoformat()
            })
            converted.append({"region": region, "poi": poi, "coord": coord})

        else:
            # POI successfully defended — optionally reward influence
            for faction_id in influence:
                current = db.reference(f"/poi_state/{region}/{poi}/faction_influence/{faction_id}").get() or 0
                db.reference(f"/poi_state/{region}/{poi}/faction_influence/{faction_id}").set(current + 1)

            db.reference(f"/poi_state/{region}/{poi}/event_log").push({
                "type": "faction_defense_success",
                "factions": list(influence.keys()),
                "day": datetime.utcnow().isoformat()
            })

    print(f"[MONSTER ATTACK] {len(converted)} POIs taken over.")
    return converted

@worldgen_bp.route('/monster_spawns/<int:x>/<int:y>', methods=['GET'])
def monster_spawns(x, y):
    monsters = generate_monsters_for_tile(x, y)
    return jsonify({"tile": f"{x}_{y}", "monsters": monsters})


@worldgen_bp.route('/generate_encounter', methods=['POST'])
def generate_encounter():
    data = request.get_json(force=True)
    party_id = data.get("party_id")
    location = data.get("location", "0_0")

    if not party_id:
        return jsonify({"error": "party_id is required"}), 400

    try:
        px, py = map(int, location.split("_"))
    except ValueError:
        px, py = 0, 0

    dist = math.sqrt(px**2 + py**2)
    frac = min(max((dist - 50) / 50, 0.0), 1.0) if dist > 50 else 0.0

    # 🎯 Difficulty scaling logic
    cr_inc, roll = 0.0, random.random()
    for step, chance in [(0.25, 0.05), (0.50, 0.15), (0.75, 0.30), (1.00, 0.50)]:
        if roll < chance * frac:
            cr_inc = step
            break
        roll -= chance * frac

    # 🎯 Pull party
    party = db.reference(f"/parties/{party_id}").get()
    if not party:
        return jsonify({"error": f"Party {party_id} not found"}), 404

    player_party = []
    for pid in party.get("members", []):
        c = db.reference(f"/players/{pid}").get() or {}
        if c:
            player_party.append({**c, "id": pid})

    total_lvl = sum(p.get("level", 1) for p in player_party)
    eff_lvl = total_lvl + cr_inc
    min_cr = max(round(eff_lvl * 0.25 - 0.25, 2), 0)
    max_cr = round(eff_lvl * 0.25 + 0.25, 2)

    # 🎯 Pull enemy monsters
    monsters = db.reference("/rules/monsters").get() or {}
    valid = [m for m in monsters.values() if min_cr <= m.get("challenge_rating", 0) <= max_cr]
    if not valid:
        return jsonify({"error": "No suitable monsters found."}), 500

    enemies = [{
        "id": f"enemy_{uuid4().hex[:8]}",
        "name": m.get("name", "Unknown"),
        "HP": m.get("hp", 20),
        "AC": m.get("ac", 12),
        "DEX": m.get("dex", 10),
        "team": "hostile"
    } for m in random.sample(valid, min(3, len(valid)))]

    # ⚔️ Use RAM-based combat state
    result = initiate_combat(player_party, enemies, battle_name=f"Encounter at {location}")
    xp = sum(m.get("xp", 50) for m in enemies)
    xp_result = award_xp_to_party(party_id, xp)

    return jsonify({
        "message": "RAM-based combat started",
        "battle_id": result["battle_id"],
        "round": result["combat_state"].round,
        "player_party": [p.character_id for p in result["combat_state"].party],
        "enemy_party": [e.character_id for e in result["combat_state"].enemies],
        "xp_awarded": xp_result,
        "distance_fraction": frac,
        "effective_level": eff_lvl
    })

@worldgen_bp.route('/generate_location_gpt', methods=['POST'])
def generate_location_gpt():
    data = request.get_json(force=True)
    x, y = data.get("x"), data.get("y")
    if x is None or y is None:
        return jsonify({"error": "Missing x or y coordinate"}), 400

    prompt = data.get("prompt", "Generate a fantasy location for a D&D-style world.")
    system_prompt = (
        "You are a worldbuilder AI. Generate a JSON object representing a fantasy map location. "
        "Include: name, description, danger_level (0-10), buildings (if any), npcs (if any), tags, and lore_hooks."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Prompt: {prompt}\nCoordinates: ({x},{y})"}
            ],
            temperature=0.8,
            max_tokens=500
        )
        location = json.loads(response.choices[0].message.content.strip())
        location["coordinates"] = {"x": x, "y": y}
        db.reference(f"/locations/{x}_{y}").set(location)
        log_usage("gpt-4.1.1", response.get("usage", {}))  # External function; verify definition.
        return jsonify({"message": "Location generated and saved.", "location": location})
    except Exception as e:
        return jsonify({"error": f"GPT or Firebase error: {str(e)}"}), 500

@worldgen_bp.route("/generate_region", methods=["POST"])
def route_generate_region():
    """
    POST /generate_region
    Optional JSON body: {"seed_x": 0, "seed_y": 0}
    """
    data = request.get_json(force=True) or {}
    seed_x = data.get("seed_x", 0)
    seed_y = data.get("seed_y", 0)

    try:
        result = generate_region(seed_x=seed_x, seed_y=seed_y)
        return jsonify({"message": "Region generated successfully", **result}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500