from firebase_admin import db
from datetime import datetime
import random

# Sample emotion pool (replace or expand)
EMOTION_POOL = [
    "rage", "melancholy", "anxiety", "hope", "grief", "love", 
    "jealousy", "serenity", "defiance", "regret", "ambition", 
    "happiness", "pride", "shame", "guilt", "fear", "envy", 
    "sorrow", "frustration", "despair", "elation", "embarrassment", 
    "contentment", "insecurity", "compassion", "resentment", "boredom", 
    "nervousness", "gratitude", "excitement", "disgust", "loneliness", 
    "affection", "sympathy", "passion", "righteousness", "hopelessness", 
    "curiosity", "surprise", "anticipation", "exhaustion", "wonder", 
    "doubt", "confusion", "relief", "inspiration", "pragmatism", 
    "melancholy", "nostalgia", "rage", "compromise", "clarity", 
    "rebellion", "stubbornness", "defeat", "bitterness", "fearlessness", 
    "submission", "optimism", "pessimism", "indifference", "disappointment", 
    "tenderness", "vulnerability", "understanding", "admiration", 
    "revulsion", "alienation", "humility", "acquiescence", "peace"
]


def tick_npc_motifs(npc_id):
    npc_ref = db.reference(f"/npcs/{npc_id}")
    npc = npc_ref.get()
    if not npc:
        return {"error": "NPC not found"}

    updated = False

    # --- Tick entropy ---
    entropy = npc.get("motif_entropy", {})
    for motif in npc.get("core_motifs", []):
        entropy[motif] = min(entropy.get(motif, 0) + 1, 5)
    npc["motif_entropy"] = entropy
    updated = True

    # --- Tick emotional flags ---
    emotional_flags = npc.get("emotional_flags", [])
    new_flags = []
    for flag in emotional_flags:
        flag["duration"] -= 1
        if flag["duration"] > 0:
            new_flags.append(flag)
    npc["emotional_flags"] = new_flags
    updated = True

    # --- Add new emotion? 20% chance ---
    if len(new_flags) < 3 and random.random() < 0.2:
        emotion = random.choice(EMOTION_POOL)
        intensity = random.randint(1, 5)
        duration = max(1, 6 - intensity)
        new_flags.append({
            "emotion": emotion,
            "intensity": intensity,
            "duration": duration
        })
        npc["emotional_flags"] = new_flags

    if updated:
        npc["last_motif_tick"] = datetime.utcnow().isoformat()
        npc_ref.set(npc)

    return {
        "npc_id": npc_id,
        "motif_entropy": npc["motif_entropy"],
        "emotional_flags": new_flags
    }

def get_npc_motif_prompt(npc_id):
    npc = db.reference(f"/npcs/{npc_id}").get()
    if not npc:
        return ""

    flags = npc.get("emotional_flags", [])
    phrases = []
    for flag in flags:
        label = f"{flag['emotion']} (intensity {flag['intensity']})"
        phrases.append(label)

    core_motifs = npc.get("core_motifs", [])
    entropy = npc.get("motif_entropy", {})
    motive_tags = [m for m in core_motifs if entropy.get(m, 0) >= 3]

    result = []
    if phrases:
        result.append("Emotional State: " + ", ".join(phrases))
    if motive_tags:
        result.append("Active Motivations: " + ", ".join(motive_tags))
    return " | ".join(result)
