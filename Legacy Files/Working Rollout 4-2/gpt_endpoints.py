from flask import Blueprint, request, jsonify
import json
import openai
from firebase_admin import db
import logging
from datetime import datetime
from rules_engine import lookup_rule  # ← Added for rule context
import random
from quest_tracker import append_to_existing_log

gpt_bp = Blueprint('gpt', __name__)
basic_bp = Blueprint('basic', __name__)

# --- Helper Functions for Arc Management ---
def update_arc_progress(entity_type, entity_id, arc_name, progress, status="active"):
    """ Update arc progress for an entity (player, npc, or region) """
    entity_ref = db.reference(f"/{entity_type}s/{entity_id}")
    entity_data = entity_ref.get()

    if not entity_data:
        return {"error": f"{entity_type} not found"}

    current_arcs = entity_data.get("current_arcs", [])
    updated = False
    for arc in current_arcs:
        if arc["arc_name"] == arc_name:
            arc["progress"] = progress
            arc["status"] = status
            updated = True
            break

    if not updated:
        current_arcs.append({
            "arc_name": arc_name,
            "status": status,
            "progress": progress,
            "quests": [],
            "npc_reaction": "neutral"
        })

    entity_ref.update({"current_arcs": current_arcs})
    return {"status": f"{arc_name} arc updated for {entity_type}", "entity_id": entity_id}


def complete_arc_and_trigger_next(player_id, arc_name, new_arc_name=None):
    """ Mark arc as completed and trigger the next arc """
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    if not player_data:
        return {"error": "Player not found"}

    current_arc = player_data.get("current_arc", "")
    if current_arc == arc_name:
        player_ref.update({"current_arc_status": "completed"})
        if new_arc_name:
            update_player_arc(player_id, new_arc_name, arc_choices=[], arc_progress=0, npc_reactions={})
            return {"status": f"Arc '{arc_name}' completed, and '{new_arc_name}' triggered."}

    return {"status": f"Arc '{arc_name}' is already completed or not found."}


def generate_quests_for_active_arc(player_id, arc_name, arc_progress):
    """ Generate quests based on active arc progress """
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    if not player_data:
        return {"error": "Player not found"}

    if arc_name == player_data.get("current_arc") and arc_progress < 100:
        quests = []
        if arc_name == "The Fallen Noble":
            if arc_progress < 50:
                quests = ["recover_lost_legacy", "find_allies_in_exile"]
            elif arc_progress >= 50 and arc_progress < 100:
                quests = ["seek_revenge", "infiltrate_the_royal_palace"]

        for quest in quests:
            append_to_existing_log(player_id, npc_name="NPC", summary=f"Quest generated: {quest}")

        return {"status": "New quests generated based on current arc.", "quests": quests}

    return {"status": "Arc is not active or progress is complete."}

def update_player_arc(player_id, arc_name, arc_choices, arc_progress, npc_reactions):
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    if not player_data:
        return {"error": "Player not found"}

    # Update the player's arc data
    player_ref.update({
        "current_arc": arc_name,
        "arc_choices": arc_choices,
        "arc_progress": arc_progress,
        "npc_reactions": npc_reactions
    })

    # Optionally trigger a new arc after completing an old one
    # Example: Player finishes "The Fallen Noble" arc, trigger "Revenge of the Exiled"
    if arc_progress >= 100:
        # Trigger new arc logic here
        pass

    return {"status": "Player arc updated", "player_id": player_id}

def handle_event_and_progress_arc(entity_type, entity_id, event_name):
    # Handle specific event
    if event_name == "kingdom_falls":
        # If the player or NPC triggers the fall of a kingdom
        update_arc_progress(entity_type, entity_id, "The Kingdom's Fall", 100, "completed")
        # Trigger the next arc
        if entity_type == "player":
            new_arc_name = "Rebuild the Kingdom"
            update_arc_progress(entity_type, entity_id, new_arc_name, 0, "active")

    elif event_name == "rebellion_succeeds":
        # Another example event
        update_arc_progress(entity_type, entity_id, "Revolutionary Victory", 100, "completed")
        if entity_type == "player":
            new_arc_name = "The Rise of a New Order"
            update_arc_progress(entity_type, entity_id, new_arc_name, 0, "active")

    return {"status": f"Event '{event_name}' processed and arc progress updated."}

def generate_npc_response_with_arc_context(npc_id, player_id, prompt):
    # Fetch NPC and Player Arc Data
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = npc_ref.get()

    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()

    # Fetch the current arcs of both NPC and Player
    npc_arc = npc_data.get("current_arcs", [])
    player_arc = player_data.get("current_arc", "")

    # Add arc context to GPT prompt
    arc_context = f"NPC is currently involved in the arc: {npc_arc[-1]['arc_name']} (Status: {npc_arc[-1]['status']})"
    player_context = f"Player is currently in the arc: {player_arc}."

    full_prompt = f"{arc_context} {player_context} {prompt}"

    # Send the prompt to GPT with arc context
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=150
    )

    return response.choices[0].message.content.strip()

# --- Existing Code ---
def build_dm_context():
    try:
        global_state = db.reference('/global_state').get() or {}
    except Exception as e:
        logging.error("Error fetching global state for DM context: %s", str(e))
        global_state = {}
    return f"Global State: {json.dumps(global_state)}"

def build_npc_context(npc_id, extra_context=""):
    try:
        npc_memory = db.reference(f'/npc_memory/{npc_id.lower()}').get() or {}
        npc_knowledge = db.reference(f'/npc_knowledge/{npc_id.lower()}').get() or {}
    except Exception as e:
        logging.error("Error fetching NPC data for context: %s", str(e))
        npc_memory, npc_knowledge = {}, {}
    context = f"NPC Memory: {json.dumps(npc_memory)}; NPC Knowledge: {json.dumps(npc_knowledge)}"
    if extra_context:
        context += f"; {extra_context}"
    return context

def gpt_router(importance_score, flags=None):
    if flags is None:
        flags = {}
    if importance_score >= 7 or flags.get("force_gpt4", False):
        return "gpt-4"
    else:
        return "gpt-3.5-turbo"

def log_gpt_usage(model, usage):
    try:
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        log_ref = db.reference(f'/gpt_usage/{model}/{timestamp}')
        log_ref.set(usage)
    except Exception as e:
        logging.error("Error logging GPT usage: %s", str(e))

@basic_bp.route('/generate_location_gpt', methods=['POST'])
def generate_location_gpt():
    data = request.json
    x = data.get("x")
    y = data.get("y")
    prompt = data.get("prompt", "Generate a fantasy location for a D&D-style world.")
    
    if x is None or y is None:
        return jsonify({"error": "Missing x or y coordinate"}), 400

    system_prompt = (
        "You are a worldbuilder AI. Generate a JSON object representing a fantasy map location. "
        "It should include: name, description, danger_level (0-10), buildings (if any), npcs (if any), tags, and lore_hooks. "
        "Use JSON formatting only."
    )

    full_prompt = f"Prompt: {prompt}\nCoordinates: ({x},{y})\n"

    try:
        response = openai.ChatCompletion.create(
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

        return jsonify({"message": "Location generated and saved.", "location": location_data})

    except Exception as e:
        return jsonify({"error": f"GPT or Firebase error: {str(e)}"}), 500

@gpt_bp.route('/npc_interact', methods=['POST'])
def npc_interact():
    from rules_engine import resolve_skill_check
    from utils.intent_utils import detect_skill_action
    from quest_tracker import append_to_existing_log  # ✅ NEW

    data = request.json
    npc_id = data.get("npc_id", "")
    conversation_history = data.get("conversation_history", "")
    prompt = data.get("prompt", "")
    importance_score = data.get("importance_score", 5)
    flags = data.get("flags", {})
    player_memory = data.get("player_memory", "")
    npc_motifs = data.get("npc_motifs", "")
    player_state = data.get("player_state", {})  # Pass this from frontend if possible
    player_id = data.get("player_id", "")  # ✅ REQUIRED for quest logging

    if not npc_id or not prompt:
        return jsonify({"error": "npc_id and prompt are required"}), 400

    # NPC context
    extra_context = ""
    if player_memory:
        extra_context += f"Player Memory: {player_memory}. "
    if npc_motifs:
        extra_context += f"NPC Motifs: {npc_motifs}. "

    npc_context = build_npc_context(npc_id, extra_context)

    # Skill detection
    skill_context = ""
    skill = detect_skill_action(prompt)
    if skill:
        stat_map = {
            "intimidate": "CHA",
            "diplomacy": "CHA",
            "stealth": "DEX",
            "pickpocket": "DEX"
        }
        ability = stat_map.get(skill, "CHA")
        ability_score = player_state.get(ability, 10)
        modifiers = player_state.get("modifiers", [])
        dc = 15

        skill_result = resolve_skill_check(skill, ability_score, modifiers, dc)
        skill_context = (
            f"Skill Check Result: {skill.title()} Roll = {skill_result['roll']} "
            f"vs DC {dc} → {'SUCCESS' if skill_result['success'] else 'FAILURE'}\n"
        )

    # Build prompt
    full_prompt = (
        f"{skill_context}"
        f"NPC Context: {npc_context}\n"
        f"Conversation History: {conversation_history}\n"
        f"Prompt: {prompt}"
    )

    model_to_use = gpt_router(importance_score, flags)

    response = openai.ChatCompletion.create(
        model=model_to_use,
        messages=[
            {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=150
    )

    reply = response.choices[0].message.content.strip()
    usage = response.get("usage", {})
    log_gpt_usage(model_to_use, usage)

    # ✅ QUEST HOOK DETECTION
    system_note = response.choices[0].message.get("function_call", {}).get("name", "")
    if "quest" in system_note.lower() and player_id:
        append_to_existing_log(
            player_id=player_id,
            npc_name=npc_id,
            summary=reply
        )

    # Update NPC Arc after interaction (if needed)
    # Example: If a certain action happens, trigger arc progression
    update_arc_progress('npc', npc_id, "The Fallen Noble", 50)  # You may replace this with dynamic logic

    return jsonify({
        "npc_id": npc_id,
        "reply": reply,
        "skill_used": skill,
        "model_used": model_to_use,
        "roll_context": skill_context.strip()
    })

@gpt_bp.route('/quest_log/<player_id>', methods=['GET'])
def get_quest_log(player_id):
    ref = db.reference(f"/quest_log/{player_id}")
    log = ref.get() or {}
    return jsonify(log)

@gpt_bp.route('/dm_response', methods=['POST'])
def dm_response():
    import re
    import random
    from datetime import datetime

    data = request.json
    prompt = data.get("prompt", "")
    importance_score = data.get("importance_score", 5)
    flags = data.get("flags", {})

    if not prompt:
        return jsonify({"error": "prompt is required"}), 400

    # --- Dice Roller ---
    def roll_expression(expr):
        expr = expr.lower().strip().replace(" ", "")
        match = re.match(r"(\d*)d(\d+)([+-]\d+)?", expr)
        if not match:
            return f"Invalid: {expr}"
        num = int(match.group(1)) if match.group(1) else 1
        die = int(match.group(2))
        mod = int(match.group(3)) if match.group(3) else 0
        rolls = [random.randint(1, die) for _ in range(num)]
        total = sum(rolls) + mod
        breakdown = f"{' + '.join(map(str, rolls))}"
        if mod != 0:
            breakdown += f" {'+' if mod > 0 else '-'} {abs(mod)}"
        return f"{total} ({breakdown})"

    # --- Basic combat keyword detection ---
    def needs_combat_roll(text):
        combat_keywords = ["attack", "strike", "hit", "shoot", "swing", "stab", "slash", "cleave", "punch", "bash", "smash"]
        text = text.lower()
        return any(word in text for word in combat_keywords)

    # --- Create roll context based on intent ---
    roll_context = ""
    if needs_combat_roll(prompt):
        attack_result = roll_expression("1d20+5")
        damage_result = roll_expression("1d12+3")
        roll_context = f"Dice Results:\nAttack Roll = {attack_result}\nDamage Roll = {damage_result}"

    # --- System prompt ---
    system_instruction = (
        "You are the Dungeon Master narrating a persistent fantasy world.\n"
        "The player has declared an action. The system has rolled any required dice.\n"
        "You will receive those results as 'Dice Results', and you must narrate the outcome based on them.\n"
        "Include ONLY the outcome of the damage roll, if applicable."
    )

    # --- Global context ---
    dm_context = build_dm_context()
    full_prompt = f"DM Context: {dm_context}\n{roll_context}\nPrompt: {prompt}"
    model_to_use = gpt_router(importance_score, flags)

    # --- Send to GPT ---
    response = openai.ChatCompletion.create(
        model=model_to_use,
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.8,
        max_tokens=200
    )

    raw_reply = response.choices[0].message.content.strip()
    reply = raw_reply

    # --- Log token usage (with sanitized path) ---
    usage = response.get("usage", {})
    try:
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        log_gpt_usage(model_to_use, usage)
    except Exception as e:
        import logging
        logging.error("Error logging GPT usage: %s", str(e))

    return jsonify({"reply": reply, "model_used": model_to_use})
