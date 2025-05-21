"""
Flask routes for DM functionality, including:
- DM responses to player prompts
- Combat narration
- POI enrichment
- Portrait generation
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from firebase_admin import db
import openai
import json
import random
from app.quests.quests_class import QuestManager
from app.pois.dungeon_enrichment_utils import enrich_poi_structure
from backend.systems.dm.dm_core import (
    classify_request, 
    gather_dm_context, 
    narrate_combat_action
)

dm_engine_bp = Blueprint("dm_engine", __name__)


@dm_engine_bp.route('/dm_response', methods=['POST'])
def dm_response():
    """
    Handles all GPT DM interactions.
    Modes:
    - start_game: Generates a quest based on player info and assigns a social POI start
    - normal: Routes prompt to GPT and classifies it
    """
    data = request.get_json()
    prompt = data.get("prompt")
    character_id = data.get("character_id")
    mode = data.get("mode", "normal")
    npc_id = data.get("npc_id", None)

    if not prompt or not character_id:
        return jsonify({"error": "Missing prompt or character_id"}), 400

    # Get context for DM interactions
    context = gather_dm_context(character_id, npc_id)

    # Background prompt mode for character creation
    if mode == "background_prompt":
        gpt_prompt = (
            "Write a fantasy RPG player character background based on the following details. "
            "Limit your response to **no more than 250 words**. Be concise and vivid:\n\n"
            + prompt.strip()
        )
        try:
            reply = openai.ChatCompletion.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are the Dungeon Master narrating a fantasy world."},
                    {"role": "user", "content": gpt_prompt}
                ],
                temperature=0.8,
                max_tokens=175
            ).choices[0].message.content.strip()
            return jsonify({"reply": reply})
        except Exception as e:
            logging.error(f"Error generating background: {str(e)}")
            return jsonify({"error": f"Failed to generate background: {str(e)}"}), 500

    # Start game mode
    if mode == "start_game":
        try:
            # Load player data
            player_ref = db.reference(f"/players/{character_id}")
            player_data = player_ref.get() or {}
            
            # Find a random social POI
            poi_index = db.reference("/poi_state").get() or {}
            social_pois = []
            for region_name, pois in poi_index.items():
                for poi_id, poi_data in pois.items():
                    tags = poi_data.get("state_tags", [])
                    if "settlement" in tags or "camp" in tags or "village" in tags:
                        social_pois.append((region_name, poi_id))

            if not social_pois:
                return jsonify({"error": "No valid starting POIs found."}), 500

            region, poi_id = random.choice(social_pois)

            # Set player location
            player_data["region_id"] = region
            player_data["location"] = poi_id
            player_ref.set(player_data)

            # Generate quest with GPT
            character_name = player_data.get("name") or player_data.get("character_name") or "Unnamed"
            prompt_text = (
                f"This character: {character_name} has arrived at the POI '{poi_id}' in region '{region}'. "
                f"Create a simple quest for them based on their background and current region arc."
            )

            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4.1",
                    messages=[
                        {"role": "system", "content": "You are a quest generator for a fantasy world."},
                        {"role": "user", "content": prompt_text}
                    ],
                    temperature=0.75,
                    max_tokens=200
                )
                quest_data = response.choices[0].message.content.strip()
            except Exception as e:
                logging.error(f"Quest generation failed: {str(e)}")
                quest_data = f"🧭 Fallback quest: Investigate a strange light seen above the old lighthouse in {poi_id}, {region}."

            # Save to quest log
            quest_log_ref = db.reference(f"/quest_log/{character_id}")
            quest_log_ref.push({
                "timestamp": datetime.utcnow().isoformat(),
                "quest": quest_data,
                "region": region,
                "poi": poi_id
            })

            return jsonify({
                "region": region,
                "poi": poi_id,
                "quest": quest_data
            })
            
        except Exception as e:
            logging.error(f"Start game error: {str(e)}")
            return jsonify({"error": f"Start game failed: {str(e)}"}), 500

    # Normal DM mode
    if mode == "normal":
        # Classify the request type
        classification = classify_request(prompt, character_id)

        try:
            model = "gpt-4.1"
            full_prompt = f"Context: {context}\nPrompt: {prompt}"

            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are the Dungeon Master narrating a persistent fantasy world."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )
            gpt_reply = response.choices[0].message.content.strip()

            # Log to NPC memory if applicable
            if npc_id:
                memory_ref = db.reference(f"/npc_memory/{npc_id}")
                current = memory_ref.get() or {"rag_log": [], "summary": ""}
                current["rag_log"].append({
                    "interaction": gpt_reply,
                    "timestamp": datetime.utcnow().isoformat()
                })
                memory_ref.set(current)

            return jsonify({
                "reply": gpt_reply,
                "classified_as": classification
            })
            
        except Exception as e:
            logging.error(f"GPT reply failed: {str(e)}")
            return jsonify({"error": f"GPT reply failed: {str(e)}"}), 500

    return jsonify({"error": "Unknown DM mode."}), 400


@dm_engine_bp.route('/narrate_combat', methods=['POST'])
def generate_combat_narration():
    """
    Converts combat data to narrative prose using the combat narration module.
    """
    try:
        data = request.get_json(force=True)
        actor_name = data.get("actor_name")
        action_data = data.get("action")
        outcome = data.get("outcome")
        
        if not all([actor_name, action_data, outcome]):
            return jsonify({"error": "Missing required combat data"}), 400
            
        narration = narrate_combat_action(actor_name, action_data, outcome)
        return jsonify({"narration": narration}), 200
    except Exception as e:
        logging.error(f"Combat narration error: {str(e)}")
        return jsonify({"error": f"Failed to narrate combat: {str(e)}"}), 500


@dm_engine_bp.route('/gpt/enrich_poi', methods=['POST'])
def enrich_poi():
    """
    Uses GPT to enrich POI structure with details and descriptions.
    """
    try:
        data = request.get_json()
        region = data.get("region")
        poi_id = data.get("poi_id")
        floor_data = data.get("floor_data")

        if not all([region, poi_id, floor_data]):
            return jsonify({"error": "Missing required fields."}), 400

        poi_meta = db.reference(f"/poi_state/{region}/{poi_id}").get() or {}
        poi_meta["region"] = region
        poi_meta["id"] = poi_id

        result = enrich_poi_structure(poi_meta, floor_data)
        return jsonify(result)
    except Exception as e:
        logging.error(f"POI enrichment error: {str(e)}")
        return jsonify({"error": f"Failed to enrich POI: {str(e)}"}), 500


@dm_engine_bp.route('/generate_portrait', methods=['POST'])
def generate_portrait():
    """
    Uses OpenAI DALL-E to generate a character portrait from a description.
    """
    try:
        character_data = request.json.get("character", {})
        name = character_data.get("name", "an adventurer")
        race = character_data.get("race", "humanoid")
        gender = character_data.get("gender", "unspecified")
        background = character_data.get("background", "")
        age_category = character_data.get("age", "adult")

        age_descriptions = {
            "teen": "teenaged",
            "young adult": "young adult",
            "middle aged": "middle-aged",
            "older adult": "older adult",
            "elder": "elderly",
            "ancient": "ancient"
        }
        age_text = age_descriptions.get(age_category.lower(), "adult")

        prompt = (
            f"Detailed pencil-drawing image of a {age_text} {gender} {race} named {name}, in full color, "
            f"drawn on aging parchment paper. Background: {background}"
        )

        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512",
            response_format="url"
        )
        image_url = response['data'][0]['url']
        return jsonify({"url": image_url})

    except Exception as e:
        logging.error(f"Portrait generation error: {str(e)}")
        return jsonify({"error": f"Failed to generate portrait: {str(e)}"}), 500
