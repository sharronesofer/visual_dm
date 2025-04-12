from flask import Blueprint, request, jsonify
from firebase_admin import db
from datetime import datetime, timedelta, timezone
import random
import json

from party_engine import create_party, add_to_party
from loyalty_engine import loyalty_tick
from mobility_engine import update_npc_location
from motif_engine import tick_npc_motifs
from relationship_engine import daily_relationship_tick as run_daily_relationship_tick

npc_relationship_bp = Blueprint('npc_relationships', __name__)
__all__ = ["npc_relationship_bp"]

# ----------------- GPT Routing -----------------

def gpt_router(score=5, flags=None):
    flags = flags or {}
    if flags.get("plot") or flags.get("secret") or flags.get("emotional") or flags.get("force_gpt4"):
        return "gpt-4o"
    if score <= 3:
        return "gpt-4o-mini"
    return "gpt-4o"

def score_interaction(flags: dict) -> int:
    if not flags:
        return 5
    score = 5
    if flags.get("emotionally_charged"):
        score += 2
    if flags.get("conflict_type") in ["loyalty", "morality", "betrayal"]:
        score += 2
    if flags.get("scope") == "regional":
        score += 1
    elif flags.get("scope") == "global":
        score += 2
    if flags.get("force_gpt4"):
        return 10
    return min(score, 10)

# ----------------- Rumor & Belief Logic -----------------

def fabricate_alternate(event_data):
    return f"Someone claims {event_data.get('summary', 'something strange')} — but it sounds suspicious."

def distort_summary(summary):
    return summary.replace("was", "may have been").replace("at", "somewhere near")

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

def share_rumors_between_npcs(npc_a, npc_b, strength_threshold=3):
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

# ----------------- Basic Test Routes -----------------

@npc_relationship_bp.route("/debug_routes")
def debug_routes():
    from flask import current_app
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "rule": rule.rule
        })
    return jsonify(routes)

@npc_relationship_bp.route("/basic_routes")
def basic_routes():
    from flask import current_app
    return jsonify([
        {"endpoint": rule.endpoint, "methods": list(rule.methods), "rule": rule.rule}
        for rule in current_app.url_map.iter_rules()
        if rule.endpoint.startswith('basic.')
    ])

@npc_relationship_bp.route('/simulate_npc_interactions', methods=['POST'])
def simulate_npc_interactions():
    """
    Simulates interactions between NPCs present in a specified POI.
    Uses GPT to generate a short summary, updates NPC memory and relationship scores.
    """
    data = request.get_json(force=True)
    region_name = data.get("region_name", "")
    poi_id = data.get("poi_id", "")
    if not region_name or not poi_id:
        return jsonify({"error": "Both region_name and poi_id are required."}), 400

    poi_ref = db.reference(f'/poi_state/{region_name}/{poi_id}')
    poi_state = poi_ref.get()
    if not poi_state:
        return jsonify({"error": f"POI '{poi_id}' in region '{region_name}' not found."}), 404

    npcs = poi_state.get("npcs_present", [])
    if len(npcs) < 2:
        return jsonify({"message": "Not enough NPCs present to simulate interactions."}), 200

    from rumor_engine import share_rumors_between_npcs
    interaction_log = []
    for npc in npcs:
        others = [o for o in npcs if o != npc]
        if not others or random.random() > 0.6:
            continue
        partner = random.choice(others)
        matrix_ref = db.reference(f'/npc_opinion_matrix/{npc}/{partner}')
        score = matrix_ref.get() or 0

        if score >= 5:
            tone = "friendly"
        elif score <= -5:
            tone = "hostile"
        else:
            tone = "neutral"

        system_prompt = "You are narrating social encounters between NPCs in a persistent fantasy world.Please structure your response in multiple paragraphs, separated by blank lines. Do not combine everything into a single paragraph."
        user_prompt = (
            f"NPC A ({npc}) and NPC B ({partner}) are having a {tone} interaction at a POI called '{poi_id}'. "
            f"You are the Dungeon Master in a fantasy RPG setting. Narrate with an epic, immersive tone inspired by A mix between Cormac McCarthy, Lovecraft, and Herman Melville. Balance these elements fluidly to enhance immersion, intrigue, and emotional engagement for the players."
        )
        try:
            response = ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=60
            )
            summary = response.choices[0].message.content.strip()
            usage = response.get("usage", {})
            log_gpt_usage("gpt-4o-mini", usage)
        except Exception as e:
            summary = f"{npc} and {partner} interact (GPT failed)."

        for id_ in [npc, partner]:
            mem_ref = db.reference(f"/npc_memory/{id_.lower()}")
            memory = mem_ref.get() or {"rag_log": [], "summary": ""}
            memory["rag_log"].append({
                "interaction": summary,
                "timestamp": datetime.utcnow().isoformat()
            })
            mem_ref.set(memory)

        rumor_result = share_rumors_between_npcs(npc, partner)
        score_delta = {"friendly": +2, "neutral": 0, "hostile": -2}[tone]
        new_score = score + score_delta
        matrix_ref.set(new_score)
        interaction_log.append({
            "npc": npc,
            "partner": partner,
            "tone": tone,
            "summary": summary,
            "shared_rumors": rumor_result.get("shared", []),
            "new_score": new_score
        })

    return jsonify({
        "message": f"Simulated interactions at POI '{poi_id}' in region '{region_name}'.",
        "interactions": interaction_log
    })

@npc_relationship_bp.route('/npc_interact', methods=['POST'])
def npc_interact():
    """
    Endpoint to handle a conversation prompt with an NPC.
    Potentially runs skill checks, stores interaction memory, 
    logs quest hooks, etc.
    """
    data = request.get_json(force=True)
    npc_id = data.get("npc_id")
    player_id = data.get("character_id")
    prompt = data.get("prompt", "")
    conversation_history = data.get("conversation_history", "")
    flags = data.get("flags", {})
    player_memory = data.get("player_memory", "")
    player_state = data.get("player_state", {})

    if not npc_id or not prompt:
        return jsonify({"error": "npc_id and prompt are required"}), 400

    importance_score = score_interaction(flags)

    # Extra context: if player_memory is provided
    extra_context = ""
    if player_memory:
        extra_context += f"Player Memory: {player_memory}. "

    # Load NPC's current motifs, if present
    npc_data = db.reference(f"/npcs/{npc_id}").get() or {}
    motifs = npc_data.get("narrative_motif_pool", {}).get("active", [])
    if motifs:
        formatted = ", ".join(f"{m['theme']} (intensity {m['weight']})" for m in motifs)
        extra_context += f"NPC Emotional State: {formatted}. "

    # Fetch recent short-term memory
    recent_memory = get_recent_interactions(npc_id, player_id, limit=5)
    memory_context = "\n".join(recent_memory)
    extra_context += f"Short-Term Memory:\n{memory_context}"

    # Combine with NPC memory + knowledge
    try:
        npc_memory = db.reference(f'/npc_memory/{npc_id.lower()}').get() or {}
        npc_knowledge = db.reference(f'/npc_knowledge/{npc_id.lower()}').get() or {}
    except Exception:
        npc_memory, npc_knowledge = {}, {}

    npc_context = f"NPC Memory: {json.dumps(npc_memory)}; NPC Knowledge: {json.dumps(npc_knowledge)}; {extra_context}"

    # Detect skill check intent
    skill_context = ""
    skill = detect_skill_action(prompt)
    if skill:
        # Example: map skill to a single ability
        stat_map = {
            "intimidate": "CHA",
            "diplomacy": "CHA",
            "stealth": "DEX",
            "pickpocket": "DEX"
        }
        ability = stat_map.get(skill, "CHA")
        ability_score = player_state.get(ability, 10)
        modifiers = player_state.get("modifiers", [])
        dc = 15
        result = resolve_skill_check(skill, ability_score, modifiers, dc)
        skill_context = (
            f"Skill Check Result: {skill.title()} Roll = {result['roll']} "
            f"vs DC {dc} → {'SUCCESS' if result['success'] else 'FAILURE'}\n"
        )

    full_prompt = (
        f"{skill_context}"
        f"NPC Context: {npc_context}\n"
        f"Conversation History: {conversation_history}\n"
        f"Prompt: {prompt}"
    )

    # Decide which GPT model to use
    model = gpt_router(score=importance_score, flags=flags)
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an NPC in a persistent fantasy world simulation.Please structure your response in multiple paragraphs, separated by blank lines. Do not combine everything into a single paragraph."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        reply = response.choices[0].message.content.strip()
        usage = response.get("usage", {})
        log_gpt_usage(model, usage)
    except Exception as e:
        logging.error(f"[NPC INTERACT ERROR] {e}")
        return jsonify({"error": str(e)}), 500

    # Extract quest hook if present
    hook = extract_quest_from_reply(npc_id, player_id, reply)
    if hook.get("quest") and player_id:
        append_to_existing_log(
            player_id=player_id,
            npc_name=npc_id,
            summary=f"[Quest: {hook['quest']['title']}] {hook['quest']['summary']}"
        )

    # Store the interaction in memory
    store_interaction(npc_id, character_id, reply, tags={"type": "dialogue"})

    # Summarize and clean memory
    summarize_and_clean_memory(npc_id, character_id)

    return jsonify({
        "npc_id": npc_id,
        "reply": reply,
        "skill_used": skill,
        "model_used": model,
        "roll_context": skill_context.strip()
    })

@npc_relationship_bp.route('/relationships/update', methods=['POST'])
def update_relationships():
    data = request.get_json(force=True)
    npc_id = data["npc_id"]
    target_id = data["target_id"]

    relationship_ref = db.reference(f'/npc_opinion_matrix/{npc_id}/{target_id}')
    current_score = relationship_ref.get() or 0
    delta = random.choice([-2, -1, 0, 1, 2])
    relationship_ref.set(current_score + delta)

    return jsonify({"message": "Relationship updated", "new_score": current_score + delta}), 200

@npc_relationship_bp.route('/recruit_npc', methods=['POST'])
def recruit_npc():
    data = request.json
    character_id = data.get("character_id")
    npc_id = data.get("npc_id")

    player_data = db.reference(f"/players/{character_id}").get()
    npc_data = db.reference(f"/npcs/{npc_id}").get()

    if not player_data or not npc_data:
        return jsonify({"error": "Invalid player or NPC ID"}), 400

    existing_party = player_data.get("party_id")
    if existing_party:
        add_to_party(existing_party, npc_id)
    else:
        existing_party = create_party(character_id, [npc_id])

    return jsonify({
        "message": f"{npc_data['character_name']} has joined your party!",
        "party_id": existing_party
    })

@npc_relationship_bp.route('/npc_loyalty_tick', methods=['POST'])
def npc_loyalty_tick():
    data = request.json
    npc_id = data.get("npc_id")
    character_id = data.get("character_id")
    cha_score = data.get("cha", 10)

    if not npc_id or not character_id:
        return jsonify({"error": "Missing npc_id or character_id"}), 400

    result = loyalty_tick(npc_id, character_id, cha_score=cha_score)
    return jsonify(result)

@npc_relationship_bp.route('/npc_relationship_tick', methods=['POST'])
def npc_relationship_tick_route():
    run_daily_relationship_tick()
    return jsonify({"status": "NPC relationships updated"})

@npc_relationship_bp.route('/npc/travel/<npc_id>', methods=['POST'])
def npc_travel(npc_id):
    result = update_npc_location(npc_id)
    return jsonify(result)

@npc_relationship_bp.route('/npc_motif_tick/<npc_id>', methods=['POST'])
def npc_motif_tick(npc_id):
    result = tick_npc_motifs(npc_id)
    return jsonify(result)

@npc_relationship_bp.route('/update_npc_memory', methods=['POST'])
def update_npc_memory():
    """
    Records an interaction in the named NPC's 'rag_log', and 
    summarizes older interactions after 3 days.
    """
    data = request.get_json(force=True)
    npc_name = data.get("npc_name", "").lower()
    interaction = data.get("interaction", "")
    timestamp = data.get("timestamp", datetime.utcnow().isoformat())
    if not npc_name or not interaction:
        return jsonify({"error": "npc_name and interaction are required"}), 400

    ref = db.reference(f'/npc_memory/{npc_name}')
    memory = ref.get() or {"rag_log": [], "summary": ""}
    memory["rag_log"].append({
        "interaction": interaction,
        "timestamp": timestamp
    })

    cutoff = datetime.now(timezone.utc) - timedelta(days=3)
    new_rag = []
    expired_interactions = []
    for entry in memory["rag_log"]:
        try:
            timestamp_str = entry.get("timestamp")
            if timestamp_str.endswith("Z"):
                timestamp_str = timestamp_str.replace("Z", "+00:00")
            entry_ts = datetime.fromisoformat(timestamp_str)
            if entry_ts.tzinfo is None:
                entry_ts = entry_ts.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if entry_ts < cutoff:
            expired_interactions.append(entry["interaction"])
        else:
            new_rag.append(entry)

    memory["rag_log"] = new_rag
    if expired_interactions:
        current_summary = memory.get("summary", "")
        new_summary = current_summary + " " + " ".join(expired_interactions)
        memory["summary"] = new_summary.strip()

    ref.set(memory)
    return jsonify({
        "message": f"Memory updated for {npc_name}",
        "memory": memory
    })