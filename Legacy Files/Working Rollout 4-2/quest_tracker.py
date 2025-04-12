from firebase_admin import db
from datetime import datetime
import uuid

def create_quest_log_entry(player_id, npc_name, summary, region=None, poi=None):
    note_id = str(uuid.uuid4())
    log_ref = db.reference(f"/quest_log/{player_id}/{note_id}")
    log_data = {
        "note_id": note_id,
        "origin_npc": npc_name,
        "region": region or "unknown",
        "poi": poi or "unknown",
        "first_heard": datetime.utcnow().isoformat(),
        "status": "unresolved",
        "notes": [summary],
        "current_priority": 4
    }
    log_ref.set(log_data)
    return log_data

def append_to_existing_log(player_id, npc_name, summary):
    # Optional: if you want to group repeated notes from the same NPC
    ref = db.reference(f"/quest_log/{player_id}")
    logs = ref.get() or {}
    for log in logs.values():
        if log["origin_npc"] == npc_name and log["status"] == "unresolved":
            log["notes"].append(summary)
            log["current_priority"] += 1
            ref.child(log["note_id"]).set(log)
            return log
    return create_quest_log_entry(player_id, npc_name, summary)
