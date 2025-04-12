"""
quest_engine.py
Consolidated from quest_tracker.py and quest_hooks.py
Manages quest logs, quest hooking logic, and GPT-based quest extraction.
"""

import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Any
import openai
from firebase_admin import db

# If referencing GPT usage:
try:
    from gpt_endpoints import log_gpt_usage
except ImportError:
    def log_gpt_usage(*args, **kwargs): pass

__all__ = [
    "complete_arc_and_trigger_next", "update_player_arc", "generate_quests_for_active_arc",
    "handle_event_and_progress_arc", "trigger_arc_branch", "update_arc_progress",
    "create_quest_log_entry", "append_to_existing_log", "extract_quest_from_reply"
]


def complete_arc_and_trigger_next(character_id, arc_name, new_arc_name=None):
    player_ref = db.reference(f"/players/{character_id}")
    player_data = player_ref.get()
    if not player_data:
        return {"error": "Player not found"}
    current_arc = player_data.get("current_arc", "")
    if current_arc == arc_name:
        player_ref.update({"current_arc_status": "completed"})
        if new_arc_name:
            update_player_arc(character_id, new_arc_name, arc_choices=[], arc_progress=0, npc_reactions={})
            return {"status": f"Arc '{arc_name}' completed, and '{new_arc_name}' triggered."}
    return {"status": f"Arc '{arc_name}' is already completed or not found."}

def update_player_arc(character_id, arc_name, arc_choices, arc_progress, npc_reactions):
    """
    Update a player's current arc details.
    """
    player_ref = db.reference(f"/players/{character_id}")
    player_data = player_ref.get()
    if not player_data:
        return {"error": "Player not found"}
    player_ref.update({
        "current_arc": arc_name,
        "arc_choices": arc_choices,
        "arc_progress": arc_progress,
        "npc_reactions": npc_reactions
    })
    return {"status": "Player arc updated", "character_id": character_id}

def generate_quests_for_active_arc(character_id, arc_name, arc_progress):
    """
    Generate quests based on a player's active arc and its progress.
    """
    player_ref = db.reference(f"/players/{character_id}")
    player_data = player_ref.get()
    if not player_data:
        return {"error": "Player not found"}
    if arc_name == player_data.get("current_arc") and arc_progress < 100:
        quests = []
        if arc_name == "The Fallen Noble":
            if arc_progress < 50:
                quests = ["recover_lost_legacy", "find_allies_in_exile"]
            else:
                quests = ["seek_revenge", "infiltrate_the_royal_palace"]
        for quest in quests:
            append_to_existing_log(character_id, npc_name="NPC", summary=f"Quest generated: {quest}")
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

def trigger_arc_branch(character_id, arc_name, new_branch):
    """
    Trigger a new branch for an active arc.
    """
    ref = db.reference(f"/players/{character_id}")
    player = ref.get() or {}
    current_arcs = player.get("current_arcs", [])
    for arc in current_arcs:
        if arc.get("arc_name") == arc_name and arc.get("status") == "active":
            arc["branch"] = new_branch
            arc["npc_reaction"] = "shifted"
            ref.update({"current_arcs": current_arcs})
            return {"status": "branch triggered", "arc": arc_name, "branch": new_branch}
    return {"error": "Arc not found or inactive"}

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
            "is_primary": (entity_type == "player"),
            "hidden": False
        })

    ref.update({"current_arcs": current_arcs})
    return {"status": "updated", "arc": arc_name, "branch": branch, "progress": progress}

def create_quest_log_entry(
    character_id: str,
    npc_name: str,
    summary: str,
    region: str = "unknown",
    poi: str = "unknown",
    status: str = "unresolved",
    priority: int = 4
) -> Dict[str, Any]:
    """
    Creates a new quest log entry for the given player, storing it under /quest_log/{character_id}.

    Args:
        character_id (str): The unique identifier for the player.
        npc_name (str): The NPC providing the quest information.
        summary (str): A brief summary of the quest or note.
        region (str): The region context for the quest. Defaults to "unknown".
        poi (str): The Point of Interest context for the quest. Defaults to "unknown".
        status (str): The status of the quest (unresolved, completed, etc.).
        priority (int): Numerical priority; higher might be more urgent.

    Returns:
        Dict[str, Any]: The newly created log entry data.
    """
    note_id = str(uuid.uuid4())
    now_str = datetime.utcnow().isoformat()

    log_data = {
        "note_id": note_id,
        "origin_npc": npc_name,
        "region": region,
        "poi": poi,
        "first_heard": now_str,
        "last_updated": now_str,
        "status": status,
        "notes": [summary],
        "current_priority": priority,
    }

    db.reference(f"/quest_log/{character_id}/{note_id}").set(log_data)
    return log_data

def append_to_existing_log(character_id: str, npc_name: str, summary: str) -> Dict[str, Any]:
    """
    Appends a note to an existing unresolved quest log from the same NPC,
    or creates a new one if none is found.

    Args:
        character_id (str): The player's unique identifier.
        npc_name (str): The NPC providing the new note.
        summary (str): A brief summary of what was said or discovered.

    Returns:
        Dict[str, Any]: The updated or newly created quest log entry data.
    """
    quest_ref = db.reference(f"/quest_log/{character_id}")
    existing_logs = quest_ref.get() or {}

    # Look for an existing unresolved log with matching NPC.
    for log_id, log_entry in existing_logs.items():
        if log_entry.get("origin_npc") == npc_name and log_entry.get("status") == "unresolved":
            notes = log_entry.setdefault("notes", [])
            notes.append(summary)
            log_entry["last_updated"] = datetime.utcnow().isoformat()
            new_priority = log_entry.get("current_priority", 4) + 1

            quest_ref.child(log_id).update({
                "notes": notes,
                "current_priority": new_priority,
                "last_updated": log_entry["last_updated"]
            })
            return log_entry

    # No match found; create a brand new log entry.
    return create_quest_log_entry(character_id, npc_name, summary)

# =========================
# Quest Hook Extraction
# =========================
def extract_quest_from_reply(npc_id: str, character_id: str, reply_text: str) -> Dict[str, Any]:
    """
    Checks an NPC reply for a quest hook. If found, returns {"quest": {...}}, 
    else {"quest": null}. On error, returns {"error": "..."}.

    The "quest" object typically includes:
    {
      "title": "...",
      "summary": "...",
      "tags": {
        "danger": "...",
        "location": "...",
        "emotion": "...",
        "theme": "..."
      }
    }

    Args:
        npc_id (str): The NPC's identifier.
        character_id (str): The player's identifier.
        reply_text (str): The text of the NPC's reply.

    Returns:
        Dict[str, Any]: A dictionary containing either a "quest" or "error" key.
    """
    system_prompt = (
        "You are a D&D quest parser. The user message is NPC dialogue. "
        "If there's a quest, return JSON with 'quest': {title, summary, tags{danger,location,emotion,theme}}. "
        "Otherwise, return {\"quest\": null}."
    )
    user_prompt = f"NPC ({npc_id}) to Player ({character_id}):\n\n{reply_text}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        usage = response.get("usage", {})
        log_gpt_usage("gpt-4", usage)
    except Exception as e:
        logging.error(f"[extract_quest_from_reply] OpenAI call failed: {e}")
        return {"error": f"Failed to extract quest hook: {str(e)}"}

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return {"error": "Failed to parse quest JSON from NPC reply."}

    if "quest" not in parsed:
        parsed["quest"] = None
    return parsed
