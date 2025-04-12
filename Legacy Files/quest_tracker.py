import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from firebase_admin import db


def create_quest_log_entry(
    player_id: str,
    npc_name: str,
    summary: str,
    region: Optional[str] = None,
    poi: Optional[str] = None,
    status: str = "unresolved",
    priority: int = 4
) -> Dict[str, Any]:
    """
    Creates a new quest log entry for the given player.

    Args:
        player_id (str): The player's unique identifier.
        npc_name (str): The name (or ID) of the NPC that provided the quest info.
        summary (str): A short summary or note of what was said.
        region (str, optional): The region context for the quest. Defaults to "unknown".
        poi (str, optional): The POI context for the quest. Defaults to "unknown".
        status (str, optional): The status of the quest. Defaults to "unresolved".
        priority (int, optional): The current priority level. Defaults to 4.

    Returns:
        dict: The newly created log entry data.
    """
    note_id = str(uuid.uuid4())
    now_str = datetime.utcnow().isoformat()

    log_data = {
        "note_id": note_id,
        "origin_npc": npc_name,
        "region": region if region else "unknown",
        "poi": poi if poi else "unknown",
        "first_heard": now_str,
        "last_updated": now_str,
        "status": status,
        "notes": [summary],
        "current_priority": priority,
    }

    ref = db.reference(f"/quest_log/{player_id}/{note_id}")
    ref.set(log_data)

    return log_data


def append_to_existing_log(player_id: str, npc_name: str, summary: str) -> Dict[str, Any]:
    """
    Appends a new note (summary) to an existing unresolved quest log from the same NPC,
    incrementing the priority. If no existing log is found, creates a new one.

    Args:
        player_id (str): The player's unique identifier.
        npc_name (str): The NPC from whom the quest note originates.
        summary (str): A short summary or note to add to the quest log.

    Returns:
        dict: The updated or newly created quest log entry data.
    """
    quest_ref = db.reference(f"/quest_log/{player_id}")
    existing_logs = quest_ref.get() or {}

    # Look for an existing unresolved log from this NPC
    for log_entry in existing_logs.values():
        if (
            log_entry.get("origin_npc") == npc_name
            and log_entry.get("status") == "unresolved"
        ):
            # Found a match; append the note and increment priority
            notes = log_entry.setdefault("notes", [])
            notes.append(summary)

            new_priority = log_entry.get("current_priority", 4) + 1
            log_entry["last_updated"] = datetime.utcnow().isoformat()

            # Use update to avoid accidentally overwriting other fields if new ones appear
            quest_ref.child(log_entry["note_id"]).update({
                "notes": notes,
                "current_priority": new_priority,
                "last_updated": log_entry["last_updated"]
            })
            return log_entry

    # No existing unresolved log found; create a new one
    return create_quest_log_entry(player_id, npc_name, summary)
