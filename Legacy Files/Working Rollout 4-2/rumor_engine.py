import random
import openai
from firebase_admin import db

def propagate_beliefs(region_id):
    all_npcs = db.reference("/npcs").get() or {}
    by_poi = {}

    # Group by current POI (Place of Interest)
    for npc_id, npc in all_npcs.items():
        if npc.get("region_id") != region_id:
            continue
        poi = npc.get("mobility", {}).get("current_poi")
        if not poi:
            continue
        by_poi.setdefault(poi, []).append((npc_id, npc))

    results = []

    for poi, npc_group in by_poi.items():
        for sender_id, sender in npc_group:
            sender_beliefs = db.reference(f"/npc_knowledge/{sender_id}/beliefs").get() or {}
            if not sender_beliefs:
                continue

            belief_key = random.choice(list(sender_beliefs.keys()))
            belief = sender_beliefs[belief_key]

            for receiver_id, receiver in npc_group:
                if receiver_id == sender_id:
                    continue

                # Check if they interacted and trust each other
                rel = db.reference(f"/npcs/{receiver_id}/relationships/{sender_id}").get() or {}
                trust = rel.get("trust", 0)
                if trust < 2:
                    continue
                if random.random() > trust / 10:
                    continue  # Didn’t share this time

                # Mutate belief based on trust
                new_belief = mutate_belief_for_receiver(belief, trust_level=trust)
                db.reference(f"/npc_knowledge/{receiver_id}/beliefs/{belief_key}").set(new_belief)
                results.append((sender_id, receiver_id, new_belief["summary"]))

    return results

def mutate_belief_for_receiver(belief, trust_level):
    """
    Ask GPT to rewrite the belief based on trust level (1–5).
    """
    prompt = (
        f"An NPC hears the following rumor: '{belief['summary']}'\n"
        f"They trust the source at level {trust_level}.\n"
        f"Rewrite the belief summary they adopt. Make it less accurate if trust is low.\n"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fantasy NPC adjusting beliefs based on trust."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=100
        )

        summary = response.choices[0].message.content.strip()
        accuracy = min(1.0, 0.4 + 0.15 * trust_level)  # Adjusted for trust

        # Return belief with new summary, accuracy, and tags
        return {
            "summary": summary,
            "source": "rumor",
            "accuracy": accuracy,
            "trust_level": trust_level,
            "tags": belief.get("tags", [])
        }

    except Exception as e:
        return belief  # In case of error, return the original belief

def share_rumors_between_npcs(npc_a, npc_b, strength_threshold=3):
    """Share knowledge or beliefs from npc_a to npc_b, if they're close enough."""
    matrix_ref = db.reference(f"/npc_opinion_matrix/{npc_a}/{npc_b}")
    trust = matrix_ref.get() or 0
    if trust < strength_threshold:
        return {"status": "too_low_trust", "shared": []}

    a_knowledge = db.reference(f"/npc_knowledge/{npc_a}").get() or {}
    b_knowledge = db.reference(f"/npc_knowledge/{npc_b}").get() or {}
    shared = []

    for topic, belief in a_knowledge.items():
        if topic in b_knowledge:
            # Don't override more certain beliefs
            existing_certainty = b_knowledge[topic].get("certainty", 0.5)
            incoming_certainty = belief.get("certainty", 0.5) * 0.8  # degrade a bit
            if incoming_certainty <= existing_certainty:
                continue

        if random.random() < 0.5:  # 50% chance to share
            new_certainty = belief.get("certainty")

            # If no certainty is set, assign based on source
            if new_certainty is None:
                source = belief.get("source", "")
                if source == "global_truth":
                    new_certainty = 1.0
                elif source:
                    new_certainty = round(random.uniform(0.6, 0.9), 2)
                else:
                    new_certainty = round(random.uniform(0.3, 0.6), 2)

            b_knowledge[topic] = {
                "belief": belief.get("belief"),
                "source": npc_a,
                "shared_on": db.SERVER_TIMESTAMP,
                "certainty": round(new_certainty * 0.8, 2)  # small degradation
            }
            shared.append(topic)

    if shared:
        db.reference(f"/npc_knowledge/{npc_b}").set(b_knowledge)

    return {"status": "shared", "shared": shared}