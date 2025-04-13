import math
import random
import json
import openai
from uuid import uuid4
from flask import Blueprint, request, jsonify
from firebase_admin import db

from app.regions.worldgen_utils import refresh_cleared_pois, generate_monsters_for_tile
from app.utils.gpt_utils import log_gpt_usage

from app.combat.combat_utils import start_combat
from app.data.party_utils import award_xp_to_party

worldgen_bp = Blueprint('worldgen', __name__)

@worldgen_bp.route('/refresh_pois', methods=['POST'])
def refresh_pois():
    cnt = refresh_cleared_pois()
    return jsonify({"message": f"Refreshed {cnt} POIs."})

@worldgen_bp.route('/monster_spawns/<int:x>/<int:y>', methods=['GET'])
def monster_spawns(x, y):
    monsters = generate_monsters_for_tile(x, y)
    return jsonify({"tile": f"{x}_{y}", "monsters": monsters})

@worldgen_bp.route('/generate_encounter_v2', methods=['POST'])
def generate_encounter_v2():
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

    cr_inc, roll = 0.0, random.random()
    for step, chance in [(0.25, 0.05), (0.50, 0.15), (0.75, 0.30), (1.00, 0.50)]:
        if roll < chance * frac:
            cr_inc = step
            break
        roll -= chance * frac

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

    battle_id, combat_data = start_combat(f"Encounter at {location}", player_party, enemies)
    xp = sum(m.get("xp", 50) for m in enemies)
    xp_result = award_xp_to_party(party_id, xp)

    return jsonify({
        "message": "Combat started with distance-based CR scaling",
        "battle_id": battle_id,
        "player_party": player_party,
        "enemy_party": enemies,
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
            model="gpt-4o",
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
        _usage("gpt-4o", response.get("usage", {}))  # External function; verify definition.
        return jsonify({"message": "Location generated and saved.", "location": location})
    except Exception as e:
        return jsonify({"error": f"GPT or Firebase error: {str(e)}"}), 500
