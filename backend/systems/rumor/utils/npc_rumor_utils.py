#This module simulates NPC-to-NPC rumor propagation, belief evolution, and memory exchange using Firebase, GPT summaries, and trust mechanics. It's central to organic knowledge distribution and narrative diffusion.
#It connects with npc, memory, belief, world_log, region, and relationship systems.

"""
NPC Rumor Utilities
Handles rumor propagation, decay, and truth scoring for NPCs. Integrates with faction-level rumor logic.
See docs/stubs_needs_consolidation_qna.md for requirements.
"""

import random
# from firebase_admin import db  # TODO: Replace with proper database integration
from datetime import datetime

# --- Rumor Propagation ---
def propagate_rumor_between_npcs(npc_a_id, npc_b_id):
    """
    Propagate 1–2 rumors between two NPCs, updating their memory logs.
    Q&A: Rumors are shared, decayed, and distorted as they propagate.
    """
    def get_memory_log(npc_id):
        ref = db.reference(f"/npc_memory/{npc_id.lower()}/rag_log")
        return ref.get() or []

    def write_memory(npc_id, new_entries):
        ref = db.reference(f"/npc_memory/{npc_id.lower()}/rag_log")
        existing = ref.get() or []
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

# --- Rumor Decay ---
def decay_npc_rumors(npc_id: str, max_rumors=20):
    """
    Decay and prune rumors for an NPC over time. Remove oldest/least credible rumors.
    Q&A: Rumors deteriorate over time using the same system as memories.
    """
    ref = db.reference(f"/npc_memory/{npc_id.lower()}/rag_log")
    rumors = ref.get() or []
    # Remove oldest if more than max_rumors
    if len(rumors) > max_rumors:
        rumors = rumors[-max_rumors:]
    # Decay credibility if present
    for rumor in rumors:
        if isinstance(rumor, dict) and "credibility" in rumor:
            rumor["credibility"] = max(0, rumor["credibility"] - 1)
    ref.set(rumors)
    return rumors

# --- Truth Scoring ---
def score_npc_rumor_truth(rumor: dict, ground_truth: dict) -> float:
    """
    Score the truth of a rumor using fuzzy logic (direct comparison).
    Q&A: Truth score is calculated by direct comparison with fuzzy logic.
    """
    score = 0.0
    for k, v in rumor.items():
        if k in ground_truth and ground_truth[k] == v:
            score += 1.0
    return score / max(1, len(rumor))

# --- Belief Generation ---
def generate_npc_belief(npc_name, event_data):
    """
    Generate a belief summary for an NPC about an event, with accuracy based on trust.
    Q&A: Beliefs can be accurate, partial, or false, and are used for rumor propagation.
    """
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

# --- Utility: Distort/Fabricate ---
def fabricate_alternate(event_data):
    return f"Someone claims {event_data.get('summary', 'something strange')} — but it sounds suspicious."

def distort_summary(summary):
    return summary.replace("was", "may have been").replace("at", "somewhere near")

# --- Propagate Beliefs ---
def propagate_beliefs(region_id):
    """
    Propagate beliefs (rumors) among NPCs in a region, based on trust and proximity.
    Q&A: Rumors are shared among NPCs, with trust affecting propagation.
    """
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

def share_between_npcs(npc_a, npc_b, strength_threshold=3):
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

def drift_faction_from_rumors(npc_id, rumor_text):
    """
    If a rumor mentions a known faction, increase bias slightly toward that faction.
    """
    factions = db.reference("/factions").get() or {}
    matched = []

    for fid, fdata in factions.items():
        name = fdata.get("name", "").lower()
        if name and name in rumor_text.lower():
            matched.append(fid)

    if not matched:
        return

    ref = db.reference(f"/npc_opinion_matrix/{npc_id}/{npc_id}")
    data = ref.get() or {"faction_bias": {}}
    for fid in matched:
        data["faction_bias"][fid] = data["faction_bias"].get(fid, 0) + 1

    ref.set(data)

def distort_rumors_if_needed():
    npc_root = db.reference("/npc_knowledge").get() or {}
    distortions = []

    for npc_id, data in npc_root.items():
        rumors = data.get("rumors", [])
        mutated = False
        new_rumors = []

        for rumor in rumors:
            if isinstance(rumor, dict):
                text = rumor.get("text")
            else:
                text = rumor

            if text and random.random() < 0.05:
                # Distort the rumor via GPT
                prompt = f"Rewrite this rumor with a slight distortion, as if passed along inaccurately: '{text}'"
                new_version = call(prompt, system_prompt="You are a fantasy gossip NPC.")
                new_rumors.append(new_version)
                distortions.append({"npc": npc_id, "original": text, "distorted": new_version})
                mutated = True
            else:
                new_rumors.append(text)

        if mutated:
            db.reference(f"/npc_knowledge/{npc_id}/rumors").set(new_rumors)

    return distortions

def fabricate_false_rumors():
    npc_root = db.reference("/npc_memory").get() or {}
    new_fakes = []

    for npc_id, memory in npc_root.items():
        if random.random() > 0.01:
            continue

        rag_log = memory.get("rag_log", [])
        if not rag_log:
            continue

        recent_events = [entry["interaction"] for entry in rag_log[-3:] if "interaction" in entry]
        base_context = " ".join(recent_events[-3:])

        prompt = f"""Create a fictional but believable rumor that an NPC might invent after witnessing or hearing the following: {base_context}.
It should sound like something they might spread to others, even if it's not true."""
        
        rumor = call(prompt, system_prompt="You are a gossiping tavern-goer in a fantasy world.")
        if not rumor:
            continue

        # Append to their rumors
        old_rumors = db.reference(f"/npc_knowledge/{npc_id}/rumors").get() or []
        updated_rumors = old_rumors + [rumor]
        db.reference(f"/npc_knowledge/{npc_id}/rumors").set(updated_rumors)

        new_fakes.append({"npc": npc_id, "fabricated": rumor, "based_on": recent_events})

    return new_fakes
