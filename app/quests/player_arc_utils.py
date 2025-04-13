from app.quests.arcs_class import PlayerArc
from firebase_admin import db

def load_player_arc(character_id):
    ref = db.reference(f"/arcs/{character_id}")
    data = ref.get()
    if not data:
        return None
    return PlayerArc(character_id, data.get("arc_data"), data.get("progress_state"))

def save_player_arc(arc: PlayerArc):
    payload = arc.finalize()
    ref = db.reference(f"/arcs/{arc.character_id}")
    ref.set(payload)

def update_arc_with_event(character_id, event):
    arc = load_player_arc(character_id)
    if not arc:
        raise ValueError("No arc found for character.")

    arc.update_progress(event)
    save_player_arc(arc)
    return arc
