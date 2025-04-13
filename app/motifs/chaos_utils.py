import random
from firebase_admin import db
from datetime import datetime
from app.motifs.motif_utils import roll_new_motif
from app.motifs.motif_engine_class import MotifEngine
from app.npc.npc_rumor_utils import sync_event_beliefs

NARRATIVE_CHAOS_TABLE = [
    "NPC betrays a faction or personal goal",
    "Player receives a divine omen",
    "NPC vanishes mysteriously",
    "Corrupted prophecy appears in a temple or vision",
    "Artifact or item changes hands unexpectedly",
    "NPC's child arrives with a claim",
    "Villain resurfaces (real or false)",
    "Time skip or memory blackout (~5 minutes)",
    "PC is blamed for a crime in a new city",
    "Ally requests an impossible favor",
    "Magical item begins to misbehave",
    "Enemy faction completes objective offscreen",
    "False flag sent from another region",
    "NPC becomes hostile based on misinformation",
    "Rumor spreads about a player betrayal",
    "PC has a surreal dream altering perception",
    "Secret faction is revealed through slip-up",
    "NPC becomes obsessed with the PC",
    "Town leader is assassinated",
    "Prophecy misidentifies the chosen one"
]

def roll_chaos_event():
    return random.choice(NARRATIVE_CHAOS_TABLE)

def inject_chaos_event(event_type, region=None, context=None):
    context = context or {}
    event_id = f"chaos_{int(datetime.utcnow().timestamp())}"
    summary = f"[CHAOS EVENT] {event_type}"

    event_data = {
        "event_id": event_id,
        "summary": summary,
        "type": "narrative_chaos",
        "timestamp": datetime.utcnow().isoformat(),
        "context": context
    }

    db.reference(f"/global_state/world_log/{event_id}").set(event_data)

    if region:
        sync_event_beliefs(region, event_data)

    return event_data

def trigger_chaos_if_needed(npc_id, region=None):
    engine = MotifEngine(npc_id)
    threshold = engine.check_aggression_threshold()
    if not threshold:
        return {"message": "No chaos triggered"}

    chaos_type = roll_chaos_event()
    event = inject_chaos_event(chaos_type, region, context={"npc_id": npc_id, "threshold": threshold})
    return {"chaos_triggered": True, "event": event}

def force_chaos(npc_id, region=None):
    engine = MotifEngine(npc_id)
    pool = engine.get_pool()

    new_motif = roll_new_motif(
        exclude=[m["theme"] for m in pool.get("active_motifs", [])],
        chaos_source=True
    )
    pool["active_motifs"].append(new_motif)
    pool["motif_history"].append(new_motif["theme"])
    pool["last_rotated"] = datetime.utcnow().isoformat()

    db.reference(f"/npcs/{npc_id}/narrative_motif_pool").set(pool)

    chaos_type = roll_chaos_event()
    event = inject_chaos_event(chaos_type, region, context={"npc_id": npc_id, "forced": True})
    return {"forced_motif": new_motif, "event": event}
