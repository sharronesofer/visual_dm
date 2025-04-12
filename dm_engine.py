# dm_engine.py

import json
import logging
import openai
from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime

from player_routes import generate_ability_scores, finalize_character_creation, save_partial_character_data

dm_engine_bp = Blueprint("dm_engine", __name__)
__all__ = ["dm_engine_bp"]

# --------------------------
# Classify Prompt Function
# --------------------------

def classify_request(user_prompt: str) -> str:
    """
    Returns 'mechanical' if the text seems to involve game rules or stats,
    otherwise 'narrative'.
    """
    mechanics_keywords = [
        "roll", "damage", "armor class", "ac", "hp", "level up", "xp", 
        "skill check", "feats", "proficiency", "saving throw", "dc", 
        "bonus action", "initiative", "spell slot"
    ]
    text_lower = user_prompt.lower()
    for kw in mechanics_keywords:
        if kw in text_lower:
            return "mechanical"
    return "narrative"

# --------------------------
# Main Route
# --------------------------

@dm_engine_bp.route('/dm_response', methods=['POST'])
def dm_response():
    data = request.get_json(force=True)
    mode = data.get("mode", "normal")
    user_prompt = data.get("prompt", "")
    user_id = data.get("user_id", "anonymous")

    if not user_prompt:
        return jsonify({"reply": "No prompt provided"}), 400

    user_ref = db.reference(f"/users/{user_id}")
    user_data = user_ref.get() or {}
    dm_mode = user_data.get("dm_mode", "normal")

    lowered = user_prompt.lower()

    # ----------------------
    # Character Creation Mode
    # ----------------------

    if "create" in lowered and "character" in lowered:
        dm_mode = "character_creation"
        user_data["dm_mode"] = dm_mode
        user_ref.set(user_data)

        temp_ref = db.reference(f"/temp_characters/{user_id}")
        temp_data = {
            "creation_started": datetime.utcnow().isoformat(),
            "name": None,
            "race": None,
            "class": None,
            "ability_scores": {},
            "background": None
        }
        temp_ref.set(temp_data)

        scores = generate_ability_scores()
        save_partial_character_data(user_id, "ability_scores", scores)

    if "finish" in lowered or "done" in lowered:
        result = finalize_character_creation(user_id)
        dm_mode = "normal"
        user_data["dm_mode"] = dm_mode
        user_ref.set(user_data)
        return jsonify(result)

    if dm_mode == "character_creation":
        if "race" in lowered:
            if "dwarf" in lowered:
                save_partial_character_data(user_id, "race", "Dwarf")
            elif "elf" in lowered:
                save_partial_character_data(user_id, "race", "Elf")

        if "class" in lowered:
            if "wizard" in lowered:
                save_partial_character_data(user_id, "class", "Wizard")
            elif "fighter" in lowered:
                save_partial_character_data(user_id, "class", "Fighter")

        if "background" in lowered:
            if "noble" in lowered:
                save_partial_character_data(user_id, "background", "Noble")
            elif "soldier" in lowered:
                save_partial_character_data(user_id, "background", "Soldier")

        if "name is" in lowered:
            try:
                proposed_name = user_prompt.split("name is", 1)[1].strip()
                save_partial_character_data(user_id, "name", proposed_name)
            except Exception:
                pass

    # ----------------------
    # Start Game Mode
    # ----------------------

    if mode == "start_game":
        world_state = db.reference("/world_state").get() or {}
        character_id = data.get("character_id")

        if not character_id:
            return jsonify({"reply": "Missing character_id."}), 400

        character_data = db.reference(f"/players/{character_id}").get()
        if not character_data:
            return jsonify({"reply": f"No character found for ID {character_id}."}), 404

        prompt_content = (
            "Generate a detailed world overview for this fantasy RPG including the following sections:\n"
            "1) World Description\n"
            "2) Major Factions\n"
            "3) Religions\n"
            "4) Current Tensions\n"
            "5) A personalized starting quest hook for the character\n\n"
            "World Context:\n" + json.dumps(world_state, indent=2) + "\n\n"
            "Character Details:\n" + json.dumps(character_data, indent=2)
        )
        system_content = (
            "You are a worldbuilding assistant for a fantasy RPG. Produce output with clear section labels "
            "('World Description', 'Factions', 'Religions', 'Current Tensions', 'Quest Hook'), each on a new line."
        )
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt_content}
        ]

    # ----------------------
    # Default GPT Narrative/Mechanical
    # ----------------------

    else:
        try:
            classification_prompt = [
                {"role": "system", "content": (
                    "You are a text classifier. Respond ONLY with valid JSON: "
                    "{\"style\": \"mechanical\"} or {\"style\": \"narrative\"}. "
                    "Use 'mechanical' for rules, stats, or mechanics; otherwise 'narrative'."
                )},
                {"role": "user", "content": user_prompt}
            ]
            classification_resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=classification_prompt,
                temperature=0
            )
            classification_text = classification_resp.choices[0].message.content.strip()
            classification_data = json.loads(classification_text)
            user_style = classification_data.get("style", "narrative")
        except Exception as e:
            logging.error(f"Classification error: {e}")
            user_style = "narrative"

        system_content = (
            "You are a D&D rules assistant. Respond succinctly with mechanics and rules."
            if user_style == "mechanical"
            else "You are the Dungeon Master in a fantasy RPG. Respond immersively with detailed narrative."
        )
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_prompt}
        ]

    # ----------------------
    # Final GPT Call
    # ----------------------

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        reply_text = response.choices[0].message.content.strip()
    except Exception as e:
        reply_text = f"Error calling GPT: {e}"

    return jsonify({"reply": reply_text})
