from app.quests.quests_class import QuestLogEntry
from firebase_admin import db
from datetime import datetime

def create_quest_log_entry(region, poi, summary, tags, source, player_id):
    entry = QuestLogEntry(
        region=region,
        poi=poi,
        timestamp=datetime.utcnow().isoformat(),
        summary=summary,
        tags=tags,
        source=source,
        player_id=player_id
    )

    ref = db.reference(f"/quests/{player_id}").push()
    ref.set(entry.to_dict())
    return ref.key

def list_quests_for_player(player_id):
    ref = db.reference(f"/quests/{player_id}")
    return ref.get() or {}

def get_quest_log_entry(player_id, entry_id):
    ref = db.reference(f"/quests/{player_id}/{entry_id}")
    return ref.get()
