import os
import json
import random
import math
import uuid
import logging
from datetime import datetime, timezone, timedelta
from itertools import combinations
from random import randint

import openai
from openai import ChatCompletion
from flask import Blueprint, request, jsonify, render_template, current_app
from firebase_admin import auth, db

# If referencing local modules:
# from file_gpt_memory import get_npc_response, get_dm_response, store_interaction, ...
# from file_core_logic import generate_npcs_for_poi, create_player, ...

auth_bp = Blueprint('auth', __name__)
basic_bp = Blueprint('basic', __name__)
relationship_bp = Blueprint('relationship', __name__)
gpt_bp = Blueprint('gpt', __name__)

# -----------------------------------------------
# AUTH ROUTES
# -----------------------------------------------

@auth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json(force=True)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    if not email or not password or not username:
        return jsonify({"error": "Missing email, password, or username"}), 400
    try:
        user = auth.create_user(email=email, password=password)
        user_ref = db.reference(f"/users/{user.uid}")
        user_ref.set({
            "username": username,
            "email": email,
            "character_data": {},
            "narrator_style": "Tolkien"
        })
        return jsonify({"message": "User created", "user_id": user.uid}), 201
    except Exception as e:
        current_app.logger.error(f"Error sign_up: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email required"}), 400
    try:
        user = auth.get_user_by_email(email)
        user_ref = db.reference(f"/users/{user.uid}")
        user_data = user_ref.get()
        if not user_data:
            return jsonify({"error": "User data not found"}), 404
        return jsonify({
            "message": "Login ok",
            "user_id": user.uid,
            "username": user_data.get("username"),
            "narrator_style": user_data.get("narrator_style", "Tolkien"),
            "character_data": user_data.get("character_data", {})
        })
    except Exception as e:
        current_app.logger.error(f"Login error: {e}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    return jsonify({"message": "Logout stub"})

# -----------------------------------------------
# BASIC / MAIN ROUTES
# -----------------------------------------------

@basic_bp.route('/')
def index():
    return render_template("index.html")

@basic_bp.route('/generate_location_gpt', methods=['POST'])
def generate_location_gpt():
    data = request.get_json(force=True)
    x = data.get("x")
    y = data.get("y")
    prompt = data.get("prompt", "Generate a fantasy location.")
    if x is None or y is None:
        return jsonify({"error": "x or y missing"}), 400

    system_prompt = (
        "You are a worldbuilder AI. Generate a JSON object representing a fantasy location. "
        "Include: name, description, danger_level, buildings, npcs, tags, lore_hooks."
    )
    full_prompt = f"Prompt: {prompt}\nCoordinates: ({x},{y})\n"

    try:
        response = ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        content = response.choices[0].message.content.strip()
        location_data = json.loads(content)
        location_data["coordinates"] = {"x": x, "y": y}
        location_key = f"{x}_{y}"
        db.reference(f"/locations/{location_key}").set(location_data)

        from file_gpt_memory import log_gpt_usage
        usage = response.get("usage", {})
        log_gpt_usage("gpt-4", usage)

        return jsonify({"message": "Location saved", "location": location_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@basic_bp.route('/move_player', methods=['POST'])
def move_player():
    """
    Moves a player from their current location to new_location, generating POIs as needed.
    """
    data = request.get_json(force=True)
    player_id = data.get("player_id")
    new_loc = data.get("new_location")
    if not player_id or not new_loc:
        return jsonify({"error": "player_id/new_location required"}), 400

    ref = db.reference(f"/players/{player_id}")
    player_state = ref.get() or {}
    old_location = player_state.get("location")

    def parse_coords(loc):
        try:
            sx, sy = loc.split("_")
            return int(sx), int(sy)
        except:
            return None, None

    x1, y1 = parse_coords(old_location)
    x2, y2 = parse_coords(new_loc)
    if None in [x1, y1, x2, y2]:
        return jsonify({"error": "Coords invalid format."}), 400

    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    path = []
    for i in range(1, steps + 1):
        xx = x1 + round(i * dx / steps)
        yy = y1 + round(i * dy / steps)
        path.append((xx, yy))

    # Possibly referencing code from your core logic
    from worldgen import choose_land_type, roll_danger_for_tile, should_generate_poi

    combat_info = None
    for px, py in path:
        key = f"{px}_{py}"
        terrain = db.reference(f"/terrain_map/{key}").get()
        if not terrain:
            region_id = player_state.get("region_id", "default")
            terrain = choose_land_type(px, py, region_id)

        tile_ref = db.reference(f"/locations/{key}")
        tile_data = tile_ref.get() or {}
        if "danger_level" not in tile_data:
            tile_data["danger_level"] = roll_danger_for_tile(px, py)

        if "POI" not in tile_data:
            if should_generate_poi(px, py):
                try:
                    lore_res = ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Generate brief name & description for a fantasy POI."},
                            {"role": "user", "content": f"In a {terrain} biome."}
                        ],
                        temperature=0.8,
                        max_tokens=150
                    )
                    lore = lore_res.choices[0].message.content.strip()
                    tile_data.update({
                        "POI": True,
                        "terrain": terrain,
                        "region_id": player_state.get("region_id","default"),
                        "description": lore
                    })
                    from file_gpt_memory import log_gpt_usage
                    log_gpt_usage("gpt-3.5-turbo", lore_res.get("usage", {}))

                    tag_res = ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "Classify POI tone (friendly/neutral/hostile) & focus (combat/roleplay/exploration)."
                            },
                            {"role": "user", "content": lore}
                        ],
                        temperature=0.7,
                        max_tokens=100
                    )
                    tag_text = tag_res.choices[0].message.content.strip()
                    tile_data["tags"] = {"tone": "neutral","focus":"exploration"}
                    if ":" in tag_text:
                        for line in tag_text.split("\n"):
                            if ":" in line:
                                k, v = line.split(":",1)
                                tile_data["tags"][k.strip().lower()] = v.strip().lower()
                    log_gpt_usage("gpt-3.5-turbo", tag_res.get("usage", {}))

                    bldg_res = ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "Generate a list of buildings for a fantasy POI."},
                            {"role": "user", "content": f"List buildings for a new POI in a {terrain} biome."}
                        ],
                        temperature=0.8,
                        max_tokens=250
                    )
                    tile_data["buildings"] = bldg_res.choices[0].message.content.strip()
                    log_gpt_usage("gpt-3.5-turbo", bldg_res.get("usage",{}))

                    tile_ref.set(tile_data)
                    from file_core_logic import generate_npcs_for_poi
                    generate_npcs_for_poi(px, py)
                    tile_data = tile_ref.get()
                except Exception as e:
                    tile_data["POI_error"] = str(e)

        tile_ref.set(tile_data)

        dl = tile_data["danger_level"]
        c_chance = dl * 7.5
        c_roll = randint(0, 99)
        if c_roll < c_chance:
            player_state["location"] = key
            from file_core_logic import complete_character
            updated_player = complete_character(player_state)
            ref.set(updated_player)
            combat_info = {
                "combat_triggered": True,
                "combat_tile": key,
                "combat_chance_percent": c_chance,
                "combat_roll": c_roll,
                "player_state": updated_player
            }
            break

    if not combat_info:
        player_state["location"] = new_loc
        from file_core_logic import complete_character
        upd_player = complete_character(player_state)
        ref.set(upd_player)
        combat_info = {"combat_triggered": False, "player_state": upd_player}

    return jsonify({
        "message": f"Player {player_id} moved to {combat_info['player_state']['location']}",
        **combat_info
    })

@basic_bp.route('/debug_state', methods=['GET'])
def debug_state():
    try:
        s = db.reference('/global_state').get() or {}
        return jsonify(s)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Additional routes for refreshing POIs, awarding XP, etc. would go here...


# -----------------------------------------------
# Relationship / GPT / Combat Endpoints
# -----------------------------------------------

@basic_bp.route('/daily_world_tick', methods=['POST'])
def daily_world_tick():
    """
    Endpoint for daily world simulation updates.
    """
    from file_core_logic import update_world_state
    update_world_state()
    return jsonify({"status": "Daily world tick completed"})


@gpt_bp.route('/npc_interact', methods=['POST'])
def npc_interact():
    """
    Example route to have an NPC respond to a prompt. 
    Calls your memory logic, GPT, etc.
    """
    data = request.json or {}
    npc_id = data.get("npc_id")
    player_id = data.get("player_id")
    prompt = data.get("prompt","")
    conversation = data.get("conversation_history","")
    flags = data.get("flags",{})
    if not npc_id or not prompt:
        return jsonify({"error": "Missing npc_id or prompt."}), 400

    from file_gpt_memory import score_interaction, get_recent_interactions, store_interaction, summarize_and_clean_memory, gpt_router
    importance = score_interaction(flags)
    rec_mem = get_recent_interactions(npc_id, player_id, limit=5)
    mem_txt = "\n".join(rec_mem)
    final_prompt = f"Memory:\n{mem_txt}\nHistory:\n{conversation}\nPrompt:\n{prompt}"

    model = gpt_router(importance, flags)
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content":"You are an NPC in a persistent fantasy world."},
                {"role": "user", "content": final_prompt}
            ],
            temperature=0.7
        )
        reply = response.choices[0].message.content.strip()
        from file_gpt_memory import log_gpt_usage
        usage = response.get("usage",{})
        log_gpt_usage(model, usage)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    store_interaction(npc_id, player_id, reply, tags={"type": "dialogue"})
    summarize_and_clean_memory(npc_id, player_id)
    return jsonify({"reply": reply, "model_used": model})


@basic_bp.route('/combat_round', methods=['POST'])
def combat_round():
    data = request.get_json(force=True)
    # ... simulate a round of combat
    return jsonify({"message": "Combat round goes here"})


# Relationship blueprint, arcs, etc.

@relationship_bp.route('/update', methods=['POST'])
def relationship_update():
    data = request.json or {}
    npc_id = data.get("npc_id")
    target_id = data.get("target_id")
    if not npc_id or not target_id:
        return jsonify({"error":"Missing npc_id/target_id"}),400
    from relationship_engine import update_relationships
    result = update_relationships(npc_id, target_id)
    return jsonify(result)


@relationship_bp.route('/daily_tick', methods=['POST'])
def relationship_daily_tick():
    from relationship_engine import daily_relationship_tick
    daily_relationship_tick()
    return jsonify({"status": "Daily relationship tick complete"})

# Additional routes for your arcs, quests, etc. can go here
