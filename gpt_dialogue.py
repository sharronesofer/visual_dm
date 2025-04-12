"""
Central module for GPT-driven interactions and dialogue management.
Handles GPT-based decision-making for resting, NPC belief mutation,
and emotional motif summaries.
"""

import json
import logging
import openai
from firebase_admin import db
from datetime import datetime
from random import random

__all__ = [
    "call_gpt", "request_rest", "mutate_belief_for_receiver",
    "get_npc_motif_prompt", "log_gpt_usage"
]

# -----------------------
# Central GPT Call Helper
# -----------------------

def call_gpt(system_prompt, user_prompt, model="gpt-4o", temperature=0.7, max_tokens=150):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content) if content.startswith('{') else content
    except Exception as e:
        logging.error(f"GPT call failed: {e}")
        return {"error": str(e)}

# -----------------------
# GPT: Resting Logic
# -----------------------

def request_rest(character_id, location_description, current_threats, narrative_context):
    prompt = (
        f"The player wants to rest. Location: {location_description}.\n"
        f"Threats: {', '.join(current_threats) if current_threats else 'None'}.\n"
        f"Context: {narrative_context}\n"
        "Can they safely rest? Respond in JSON: {\"decision\":\"yes/no\", \"narration\":\"...\"}"
    )

    response = call_gpt(
        system_prompt="You are a fantasy RPG narrator deciding if a rest is safe.",
        user_prompt=prompt
    )

    if response.get("decision", "no").lower() == "yes":
        ref = db.reference(f"/players/{character_id}")
        char_data = ref.get()
        if char_data and "spell_slots" in char_data:
            for level_info in char_data["spell_slots"].values():
                level_info["used"] = 0
            ref.update({"spell_slots": char_data["spell_slots"]})
            return {
                "result": "Rest granted.",
                "narration": response["narration"],
                "spell_slots": char_data["spell_slots"]
            }

    return {
        "result": "Rest denied",
        "narration": response.get("narration", "Unable to rest safely.")
    }

# -----------------------
# GPT: Belief Mutation
# -----------------------

def mutate_belief_for_receiver(belief_summary, trust_level):
    prompt = (
        f"An NPC hears a rumor: '{belief_summary}'. They trust the source at level {trust_level}/5.\n"
        "Rewrite the rumor accordingly."
    )

    mutated_summary = call_gpt(
        system_prompt="You are adjusting beliefs based on trust in a fantasy setting.",
        user_prompt=prompt
    )

    accuracy = min(1.0, 0.4 + 0.15 * trust_level)
    return {
        "summary": mutated_summary,
        "accuracy": accuracy,
        "trust_level": trust_level
    }

# -----------------------
# GPT: Motif Summary
# -----------------------

def get_npc_motif_prompt(npc_id):
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = npc_ref.get()
    motifs = npc_data.get("narrative_motif_pool", {}).get("active", [])

    formatted_motifs = ", ".join(f"{m['theme']} (intensity {m['weight']})" for m in motifs)

    prompt = (
        f"Summarize the emotional and motif state for NPC '{npc_data.get('character_name', 'NPC')}':\n"
        f"Motifs: {formatted_motifs}\n"
        "Provide a brief, evocative summary for dialogue purposes."
    )

    summary = call_gpt(
        system_prompt="You summarize NPC emotional states for fantasy roleplaying dialogue.",
        user_prompt=prompt
    )

    return summary

# -----------------------
# GPT Usage Logging
# -----------------------

def log_gpt_usage(model, usage_details):
    try:
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        log_ref = db.reference(f'/gpt_usage/{model}/{timestamp}')
        log_ref.set(usage_details)
    except Exception as e:
        logging.error(f"Failed to log GPT usage: {e}")
