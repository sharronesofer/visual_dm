import openai
import json
import logging
from firebase_admin import db

# General GPT interaction
def log_gpt_usage(model_name: str, usage: dict):
    """
    Logs GPT token usage statistics for monitoring or debugging purposes.
    """
    if usage:
        logging.info(f"[GPT USAGE] model={model_name} | prompt_tokens={usage.get('prompt_tokens')} | "
                     f"completion_tokens={usage.get('completion_tokens')} | total_tokens={usage.get('total_tokens')}")
    else:
        logging.info(f"[GPT USAGE] model={model_name} | no usage data provided.")
        
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

# Select GPT model based on context
def gpt_router(score=5, flags=None):
    flags = flags or {}
    if flags.get("plot") or flags.get("secret") or flags.get("emotional") or flags.get("force_gpt4"):
        return "gpt-4o"
    return "gpt-4o-mini" if score <= 3 else "gpt-4o"

# Scoring interactions based on flags
def score_interaction(flags: dict) -> int:
    if not flags:
        return 5
    score = 5
    if flags.get("emotionally_charged"):
        score += 2
    if flags.get("conflict_type") in ["loyalty", "morality", "betrayal"]:
        score += 2
    scope = flags.get("scope")
    if scope == "regional":
        score += 1
    elif scope == "global":
        score += 2
    if flags.get("force_gpt4"):
        return 10
    return min(score, 10)

# Handling rest requests
def request_rest(character_id, location_description, current_threats, narrative_context):
    threats_formatted = ', '.join(current_threats) if current_threats else 'None'
    prompt = (
        f"The player wants to rest. Location: {location_description}.\n"
        f"Threats: {threats_formatted}.\n"
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

# Belief mutation using GPT
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

# Summarize NPC motif/emotional state
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

def detect_skill_action(prompt):
    skills = {
        "intimidate": ["threaten", "intimidate", "scare", "bully"],
        "diplomacy": ["persuade", "convince", "negotiate", "talk down"],
        "stealth": ["sneak", "hide", "creep", "shadow"],
        "pickpocket": ["steal", "lift", "pickpocket", "snatch"]
    }

    prompt_lower = prompt.lower()
    for skill, keywords in skills.items():
        if any(keyword in prompt_lower for keyword in keywords):
            return skill
    return None
