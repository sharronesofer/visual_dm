import random
from firebase_admin import db
from datetime import datetime

# Placeholder functions for summary distortion and fabrication
def share_rumors_between_npcs(npc_a_id, npc_b_id):
    """
    NPC A shares 1–2 rumors (memories) with NPC B, and vice versa.
    Memory logs are stored in /npc_memory/<npc_id_lower>/rag_log.
    """

    def get_memory_log(npc_id):
        ref = db.reference(f"/npc_memory/{npc_id.lower()}/rag_log")
        return ref.get() or []

    def write_memory(npc_id, new_entries):
        ref = db.reference(f"/npc_memory/{npc_id.lower()}/rag_log")
        existing = ref.get() or []
        # Deduplicate by string content
        existing_texts = set(m['interaction'] for m in existing)
        for entry in new_entries:
            if entry["interaction"] not in existing_texts:
                existing.append(entry)
        ref.set(existing)

    def sample_memories(memories, count=2):
        return random.sample(memories, min(len(memories), count))

    shared = []

    a_memory = get_memory_log(npc_a_id)
    b_memory = get_memory_log(npc_b_id)

    a_to_b = sample_memories(a_memory)
    b_to_a = sample_memories(b_memory)

    timestamp = datetime.utcnow().isoformat()
    write_memory(npc_b_id, [{"interaction": m["interaction"], "timestamp": timestamp} for m in a_to_b])
    write_memory(npc_a_id, [{"interaction": m["interaction"], "timestamp": timestamp} for m in b_to_a])

    shared.extend([m["interaction"] for m in a_to_b])
    shared.extend([m["interaction"] for m in b_to_a])

    return {"shared": shared}

def fabricate_alternate(event_data):
    return f"Someone claims {event_data.get('summary', 'something strange')} — but it sounds suspicious."

def distort_summary(summary):
    return summary.replace("was", "may have been").replace("at", "somewhere near")

def distort_summary(original_summary):
    return f"Partially distorted: {original_summary}"

def fabricate_alternate(event_data):
    return "Completely fabricated summary."

def generate_npc_belief(npc_name, event_data):
    trust_level = random.randint(1, 5)
    roll = random.random()
    original_summary = event_data.get("summary", "some event happened")

    if roll < trust_level / 5:
        accuracy = "accurate"
        belief_summary = original_summary
    elif roll < 0.8:
        accuracy = "partial"
        belief_summary = distort_summary(original_summary)
    else:
        accuracy = "false"
        belief_summary = fabricate_alternate(event_data)

    return {
        "belief_summary": belief_summary,
        "accuracy": accuracy,
        "source": "world_log",
        "trust_level": trust_level,
        "heard_at": event_data.get("poi", "unknown")
    }

def sync_event_beliefs(region_name, event_data):
    poi_ref = db.reference(f"/poi_state/{region_name}")
    pois = poi_ref.get() or {}
    npc_belief_count = 0
    for poi_id, poi_data in pois.items():
        npcs = poi_data.get("npcs_present", [])
        for npc_name in npcs:
            belief = generate_npc_belief(npc_name, event_data)
            db.reference(f"/npc_knowledge/{npc_name}/beliefs/{event_data['event_id']}").set(belief)
            npc_belief_count += 1
    return npc_belief_count

def propagate_beliefs(region_id):
    all_npcs = db.reference("/npcs").get() or {}
    by_poi = {}
    for npc_id, npc_data in all_npcs.items():
        if npc_data.get("region_id") != region_id:
            continue
        poi = npc_data.get("mobility", {}).get("current_poi")
        if poi:
            by_poi.setdefault(poi, []).append((npc_id, npc_data))

    results = []

    for poi, npc_group in by_poi.items():
        for sender_id, sender_data in npc_group:
            sender_beliefs = db.reference(f"/npc_knowledge/{sender_id}/beliefs").get() or {}
            if not sender_beliefs:
                continue
            belief_key = random.choice(list(sender_beliefs.keys()))
            belief_record = sender_beliefs[belief_key]

            for receiver_id, receiver_data in npc_group:
                if receiver_id == sender_id:
                    continue
                rel = db.reference(f"/npcs/{receiver_id}/relationships/{sender_id}").get() or {}
                trust = rel.get("trust", 0)
                if trust < 2 or random.random() > trust / 10:
                    continue
                db.reference(f"/npc_knowledge/{receiver_id}/beliefs/{belief_key}").set(belief_record)
                results.append((sender_id, receiver_id, belief_record["belief_summary"]))

    return results

def s_between_npcs(npc_a, npc_b, strength_threshold=3):
    matrix_ref = db.reference(f"/npc_opinion_matrix/{npc_a}/{npc_b}")
    trust = matrix_ref.get() or 0
    if trust < strength_threshold:
        return {"status": "too_low_trust", "shared": []}

    a_knowledge = db.reference(f"/npc_knowledge/{npc_a}").get() or {}
    b_knowledge = db.reference(f"/npc_knowledge/{npc_b}").get() or {}
    shared = []

    for topic, belief in a_knowledge.items():
        if topic in b_knowledge:
            existing_certainty = b_knowledge[topic].get("certainty", 0.5)
            incoming_certainty = belief.get("certainty", 0.5) * 0.8
            if incoming_certainty <= existing_certainty:
                continue
        if random.random() < 0.5:
            certainty = belief.get("certainty", round(random.uniform(0.3, 0.9), 2))
            b_knowledge[topic] = {
                "belief": belief.get("belief"),
                "source": npc_a,
                "shared_on": db.SERVER_TIMESTAMP,
                "certainty": round(certainty * 0.8, 2)
            }
            shared.append(topic)

    if shared:
        db.reference(f"/npc_knowledge/{npc_b}").set(b_knowledge)

    return {"status": "shared", "shared": shared}