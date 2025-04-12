from firebase_admin import db
from datetime import datetime, timedelta
import random

# Tension Engine
def modify_tension(region_id, source, amount):
    tension_ref = db.reference(f"/regions/{region_id}/tension")
    tension_data = tension_ref.get() or {"value": 0, "history": []}

    tension_data["value"] = max(0, min(100, tension_data["value"] + amount))
    tension_data["history"].append({
        "source": source,
        "amount": amount,
        "timestamp": datetime.utcnow().isoformat()
    })

    tension_ref.set(tension_data)
    return tension_data

def get_tension(region_id):
    return db.reference(f"/regions/{region_id}/tension").get() or {"value": 0, "history": []}

def decay_tension(region_id, decay_amount=1):
    return modify_tension(region_id, "decay", -abs(decay_amount))

def reset_tension(region_id):
    tension_ref = db.reference(f"/regions/{region_id}/tension")
    tension_ref.set({"value": 0, "history": []})
    return {"status": "reset"}

# World State Truth Event Logging
def log_world_event(event_data):
    event_id = f"event_{int(datetime.utcnow().timestamp())}"
    event_data["event_id"] = event_id
    event_data["timestamp"] = datetime.utcnow().isoformat()
    db.reference(f"/global_state/world_log/{event_id}").set(event_data)
    return event_data

# NPC Belief Generation
def distort_summary(summary):
    return summary.replace("was", "may have been").replace("at", "near")

def fabricate_alternate(event_data):
    return f"Rumor suggests {event_data.get('summary', 'something mysterious')} occurred."

def generate_npc_belief(npc_name, event_data):
    trust_level = random.randint(1, 5)
    accuracy_roll = random.random()

    if accuracy_roll < trust_level / 5:
        belief_summary = event_data["summary"]
        accuracy = "accurate"
    elif accuracy_roll < 0.8:
        belief_summary = distort_summary(event_data["summary"])
        accuracy = "partial"
    else:
        belief_summary = fabricate_alternate(event_data)
        accuracy = "false"

    return {
        "summary": belief_summary,
        "accuracy": accuracy,
        "trust_level": trust_level,
        "heard_at": event_data.get("poi", "unknown")
    }

# Propagate World Events
def sync_event_beliefs(region_name, event_data):
    pois = db.reference(f"/poi_state/{region_name}").get() or {}
    npc_count = 0

    for poi_id, poi in pois.items():
        npcs = poi.get("npcs_present", [])
        for npc_name in npcs:
            belief = generate_npc_belief(npc_name, event_data)
            db.reference(f"/npc_knowledge/{npc_name}/beliefs/{event_data['event_id']}").set(belief)
            npc_count += 1

    return npc_count

# Debugging Global State
def debug_global_state():
    return db.reference('/global_state').get() or {}

# Updating NPC Memory
def update_npc_memory(npc_name, interaction, timestamp=None):
    timestamp = timestamp or datetime.utcnow().isoformat()
    memory_ref = db.reference(f'/npc_memory/{npc_name.lower()}')
    memory = memory_ref.get() or {"rag_log": [], "summary": ""}

    memory["rag_log"].append({"interaction": interaction, "timestamp": timestamp})
    cutoff = datetime.utcnow() - timedelta(days=3)

    recent_logs = [entry for entry in memory["rag_log"] if datetime.fromisoformat(entry["timestamp"]) >= cutoff]
    expired_logs = [entry for entry in memory["rag_log"] if datetime.fromisoformat(entry["timestamp"]) < cutoff]

    if expired_logs:
        memory["summary"] += " " + " ".join([entry["interaction"] for entry in expired_logs])

    memory["rag_log"] = recent_logs
    memory_ref.set(memory)

    return memory