from flask import Blueprint, request, jsonify
import json
import openai
import logging
from datetime import datetime
import random

from firebase_admin import db
from rules_engine import lookup_rule, resolve_skill_check
from quest_tracker import append_to_existing_log
from gpt_integration import get_dm_response as dm_response, get_npc_response as npc_response, gpt_router, log_gpt_usage
from short_term_memory import store_interaction, get_recent_interactions
from memory_cleanup import summarize_and_clean_memory
from quest_hooks import extract_quest_from_reply
from importance_utils import score_interaction
from utils.intent_utils import detect_skill_action

# === Blueprints ===
gpt_bp = Blueprint('gpt', __name__)
basic_bp = Blueprint('basic', __name__)

# === Arc Management ===

def gpt_router(importance_score, flags=None):
    """
    Decide which GPT model to use based on importance score and override flags.
    """
    flags = flags or {}
    return "gpt-4" if importance_score >= 7 or flags.get("force_gpt4") else "gpt-3.5-turbo"

def log_gpt_usage(model, usage):
    """
    Log GPT API usage data to Firebase for monitoring purposes.
    """
    try:
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        db.reference(f"/gpt_usage/{model}/{timestamp}").set(usage)
    except Exception as e:
        logging.error(f"[GPT LOGGING ERROR] {e}")

def call_gpt_model(model, messages, temperature=0.7, max_tokens=150):
    """
    Call the GPT API and return parsed JSON if possible, otherwise fallback to raw string.
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        usage = response.get("usage", {})
        log_gpt_usage(model, usage)

        content = response.choices[0].message.content.strip()
        try:
            return json.loads(content)
        except Exception:
            return content

    except Exception as e:
        logging.error(f"[GPT ERROR] Failed with model {model}: {e}")
        return None

def get_dm_response(context, prompt, importance_score=5, flags=None, temperature=0.7, max_tokens=150):
    """
    Generate a Dungeon Master narration or ruling.
    """
    model = gpt_router(importance_score, flags)
    messages = [
        {"role": "system", "content": "You are a Dungeon Master managing a persistent fantasy world."},
        {"role": "user", "content": f"Context: {context}\nPrompt: {prompt}"}
    ]
    return call_gpt_model(model, messages, temperature, max_tokens)

def get_npc_response(npc_context, conversation_history, prompt, importance_score=5, flags=None, temperature=0.7, max_tokens=150):
    """
    Generate an NPC dialogue response in context.
    """
    model = gpt_router(importance_score, flags)
    messages = [
        {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation."},
        {"role": "user", "content": f"NPC Context: {npc_context}\nConversation History: {conversation_history}\nPrompt: {prompt}"}
    ]
    return call_gpt_model(model, messages, temperature, max_tokens)

def update_arc_progress(entity_type, entity_id, arc_name, progress, status="active", branch=None):
    """
    Update or add an arc for an entity (player or NPC).
    """
    ref = db.reference(f"/{entity_type}s/{entity_id}")
    data = ref.get() or {}
    current_arcs = data.get("current_arcs", [])
    updated = False

    for arc in current_arcs:
        if arc.get("arc_name") == arc_name:
            arc["progress"] = progress
            arc["status"] = status
            if branch:
                arc["branch"] = branch
            updated = True
            break

    if not updated:
        current_arcs.append({
            "arc_name": arc_name,
            "status": status,
            "progress": progress,
            "branch": branch or "default",
            "quests": [],
            "npc_reaction": "neutral",
            "is_primary": entity_type == "player",
            "hidden": False
        })

    ref.update({"current_arcs": current_arcs})
    return {"status": "updated", "arc": arc_name, "branch": branch, "progress": progress}

def complete_arc_and_trigger_next(player_id, arc_name, new_arc_name=None):
    """
    Complete a current arc for a player and trigger the next arc if specified.
    """
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

def update_player_arc(player_id, arc_name, arc_choices, arc_progress, npc_reactions):
    """
    Update a player's current arc details.
    """
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()
    if not player_data:
        return {"error": "Player not found"}
    player_ref.update({
        "current_arc": arc_name,
        "arc_choices": arc_choices,
        "arc_progress": arc_progress,
        "npc_reactions": npc_reactions
    })
    return {"status": "Player arc updated", "player_id": player_id}

def generate_quests_for_active_arc(player_id, arc_name, arc_progress):
    """
    Generate quests based on a player's active arc and its progress.
    """
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()
    if not player_data:
        return {"error": "Player not found"}
    if arc_name == player_data.get("current_arc") and arc_progress < 100:
        quests = []
        if arc_name == "The Fallen Noble":
            if arc_progress < 50:
                quests = ["recover_lost_legacy", "find_allies_in_exile"]
            elif arc_progress >= 50:
                quests = ["seek_revenge", "infiltrate_the_royal_palace"]
        for quest in quests:
            append_to_existing_log(player_id, npc_name="NPC", summary=f"Quest generated: {quest}")
        return {"status": "New quests generated", "quests": quests}
    return {"status": "Arc not active or complete."}

def handle_event_and_progress_arc(entity_type, entity_id, event_name):
    """
    Update arc progress based on a game event.
    """
    if event_name == "kingdom_falls":
        update_arc_progress(entity_type, entity_id, "The Kingdom's Fall", 100, "completed")
        if entity_type == "player":
            update_arc_progress(entity_type, entity_id, "Rebuild the Kingdom", 0, "active")
    elif event_name == "rebellion_succeeds":
        update_arc_progress(entity_type, entity_id, "Revolutionary Victory", 100, "completed")
        if entity_type == "player":
            update_arc_progress(entity_type, entity_id, "The Rise of a New Order", 0, "active")
    return {"status": f"Event '{event_name}' processed."}

def trigger_arc_branch(player_id, arc_name, new_branch):
    """
    Trigger a new branch for an active arc.
    """
    ref = db.reference(f"/players/{player_id}")
    player = ref.get() or {}
    current_arcs = player.get("current_arcs", [])
    for arc in current_arcs:
        if arc.get("arc_name") == arc_name and arc.get("status") == "active":
            arc["branch"] = new_branch
            arc["npc_reaction"] = "shifted"
            ref.update({"current_arcs": current_arcs})
            return {"status": "branch triggered", "arc": arc_name, "branch": new_branch}
    return {"error": "Arc not found or inactive"}

def generate_npc_response_with_arc_context(npc_id, player_id, prompt):
    """
    Generate an NPC response using arc context from both NPC and player.
    """
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc_data = npc_ref.get()
    player_ref = db.reference(f"/players/{player_id}")
    player_data = player_ref.get()
    npc_arc = npc_data.get("current_arcs", [])
    player_arc = player_data.get("current_arc", "")
    arc_context = f"NPC Arc: {npc_arc[-1]['arc_name']} ({npc_arc[-1]['status']})" if npc_arc else ""
    player_context = f"Player Arc: {player_arc}"
    prompt = f"{arc_context} {player_context}\n{prompt}"
    return get_dm_response("Arc Context", prompt, importance_score=7)

# === Context Builders ===

def build_dm_context():
    """
    Build and return a string representation of the global state for DM context.
    """
    try:
        global_state = db.reference('/global_state').get() or {}
    except Exception as e:
        logging.error("Error fetching global state: %s", str(e))
        global_state = {}
    return f"Global State: {json.dumps(global_state)}"

def build_npc_context(npc_id, extra_context=""):
    """
    Build NPC context from memory and knowledge stored in Firebase.
    """
    try:
        memory = db.reference(f'/npc_memory/{npc_id.lower()}').get() or {}
        knowledge = db.reference(f'/npc_knowledge/{npc_id.lower()}').get() or {}
    except Exception:
        memory, knowledge = {}, {}
    context = f"Memory: {json.dumps(memory)}; Knowledge: {json.dumps(knowledge)}"
    if extra_context:
        context += f"; {extra_context}"
    return context

# === Key Endpoint: npc_interact ===

@gpt_bp.route('/npc_interact', methods=['POST'])
def npc_interact():
    data = request.get_json(force=True)
    npc_id = data.get("npc_id")
    player_id = data.get("player_id")
    prompt = data.get("prompt", "")
    conversation_history = data.get("conversation_history", "")
    flags = data.get("flags", {})
    player_memory = data.get("player_memory", "")
    player_state = data.get("player_state", {})
    importance_score = score_interaction(flags)

    if not npc_id or not prompt:
        return jsonify({"error": "npc_id and prompt are required"}), 400

    # 🧠 Initialize extra context
    extra_context = ""
    if player_memory:
        extra_context += f"Player Memory: {player_memory}. "

    # 🎭 Load NPC motifs and emotion
    npc_data = db.reference(f"/npcs/{npc_id}").get() or {}
    motifs = npc_data.get("narrative_motif_pool", {}).get("active", [])
    if motifs:
        formatted = ", ".join(f"{m['theme']} (intensity {m['weight']})" for m in motifs)
        extra_context += f"NPC Emotional State: {formatted}. "

    # 🧠 Fetch recent short-term memory
    recent_memory = get_recent_interactions(npc_id, player_id, limit=5)
    memory_context = "\n".join(recent_memory)
    extra_context += f"Short-Term Memory:\n{memory_context}"

    # 📚 Build full NPC context from Firebase + memory
    try:
        npc_memory = db.reference(f'/npc_memory/{npc_id.lower()}').get() or {}
        npc_knowledge = db.reference(f'/npc_knowledge/{npc_id.lower()}').get() or {}
    except Exception:
        npc_memory, npc_knowledge = {}, {}
    npc_context = f"NPC Memory: {json.dumps(npc_memory)}; NPC Knowledge: {json.dumps(npc_knowledge)}; {extra_context}"

    # 🎲 Detect skill check intent and resolve it
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
        result = resolve_skill_check(skill, ability_score, modifiers, dc)
        skill_context = (
            f"Skill Check Result: {skill.title()} Roll = {result['roll']} "
            f"vs DC {dc} → {'SUCCESS' if result['success'] else 'FAILURE'}\n"
        )

    # 🧠 Compose full prompt
    full_prompt = (
        f"{skill_context}"
        f"NPC Context: {npc_context}\n"
        f"Conversation History: {conversation_history}\n"
        f"Prompt: {prompt}"
    )

    # 🔁 Route to the correct GPT model
    model = gpt_router(importance_score, flags)

    # 📡 Call GPT
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=150
    )

    reply = response.choices[0].message.content.strip()

    # 🧩 Extract quest hook if present
    hook = extract_quest_from_reply(npc_id, player_id, reply)
    if hook.get("quest") and player_id:
        append_to_existing_log(
            player_id=player_id,
            npc_name=npc_id,
            summary=f"[Quest: {hook['quest']['title']}] {hook['quest']['summary']}"
        )

    # 📈 Log GPT usage
    usage = response.get("usage", {})
    log_gpt_usage(model, usage)

    # 🧠 Store reply in memory
    store_interaction(npc_id, player_id, reply, tags={"type": "dialogue"})
    summarize_and_clean_memory(npc_id, player_id)

    return jsonify({
        "npc_id": npc_id,
        "reply": reply,
        "skill_used": skill,
        "model_used": model,
        "roll_context": skill_context.strip()
    })
