from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from firebase_admin import db
import openai
import json

from app.characters.character_utils import (
    generate_ability_scores,
    save_partial_character_data,
    finalize_character_creation,
)
from app.dm_engine.dm_utils import classify_request, gpt_call

dm_engine_bp = Blueprint("dm_engine", __name__)


def gpt_call(system_prompt, user_prompt, temperature=0.7, max_tokens=600):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"GPT call failed: {e}")
        return f"Error calling GPT: {e}"


@dm_engine_bp.route('/dm_response', methods=['POST'])
def dm_response():
    data = request.get_json(force=True)
    user_prompt = data.get("prompt", "")
    user_id = data.get("user_id", "anonymous")
    mode = data.get("mode", "normal")

    if not user_prompt:
        return jsonify({"reply": "No prompt provided."}), 400

    user_ref = db.reference(f"/users/{user_id}")
    user_data = user_ref.get() or {}
    dm_mode = user_data.get("dm_mode", "normal")
    lowered_prompt = user_prompt.lower()

    # Character Creation Mode
    if "create" in lowered_prompt and "character" in lowered_prompt:
        user_data["dm_mode"] = "character_creation"
        user_ref.set(user_data)

        temp_data = {
            "creation_started": datetime.utcnow().isoformat(),
            "name": None,
            "race": None,
            "class": None,
            "ability_scores": generate_ability_scores(),
            "background": None
        }
        db.reference(f"/temp_characters/{user_id}").set(temp_data)
        return jsonify({"reply": "Character creation started."}), 200

    elif "finish" in lowered_prompt or "done" in lowered_prompt:
        result = finalize_character_creation(user_id)
        user_data["dm_mode"] = "normal"
        user_ref.set(user_data)
        return jsonify(result), 200

    elif dm_mode == "character_creation":
        if "race" in lowered_prompt:
            for race_option in ["dwarf", "elf", "human", "halfling"]:
                if race_option in lowered_prompt:
                    save_partial_character_data(user_id, "race", race_option.capitalize())

        if "class" in lowered_prompt:
            for class_option in ["wizard", "fighter", "rogue", "cleric"]:
                if class_option in lowered_prompt:
                    save_partial_character_data(user_id, "class", class_option.capitalize())

        if "background" in lowered_prompt:
            for bg_option in ["noble", "soldier", "sage", "criminal"]:
                if bg_option in lowered_prompt:
                    save_partial_character_data(user_id, "background", bg_option.capitalize())

        if "name is" in lowered_prompt:
            proposed_name = user_prompt.split("name is", 1)[1].strip()
            save_partial_character_data(user_id, "name", proposed_name)

        return jsonify({"reply": "Character data updated."}), 200

    # Start Game Mode
    elif mode == "start_game":
        character_id = data.get("character_id")

        if not character_id:
            return jsonify({"reply": "Missing character_id."}), 400

        world_state = db.reference("/world_state").get() or {}
        character_data = db.reference(f"/players/{character_id}").get()

        if not character_data:
            return jsonify({"reply": f"No character found for ID {character_id}."}), 404

        system_content = (
            "You are a worldbuilding assistant for a fantasy RPG. Produce output with clear section labels: "
            "World Description, Factions, Religions, Current Tensions, Quest Hook."
        )
        user_content = (
            "Generate a detailed world overview for this fantasy RPG including sections: "
            "World Description, Major Factions, Religions, Current Tensions, and a personalized starting quest hook.\n\n"
            f"World Context:\n{json.dumps(world_state, indent=2)}\n\n"
            f"Character Details:\n{json.dumps(character_data, indent=2)}"
        )

        reply = gpt_call(system_content, user_content)
        return jsonify({"reply": reply}), 200

    # Default Mode (Narrative/Mechanical)
    else:
        user_style = classify_request(user_prompt)

        system_content = (
            "You are a rules assistant. Respond succinctly with mechanics and rules."
            if user_style == "mechanical"
            else "You are the Dungeon Master in a fantasy RPG. Respond immersively with detailed narrative."
        )

        reply = gpt_call(system_content, user_prompt)
        return jsonify({"reply": reply}), 200