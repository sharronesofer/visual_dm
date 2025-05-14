
#This utility defines the canonical motif vocabulary, motif generation logic, and lifecycle rule for rotation. It’s a key backbone for NPC identity, chaos progression, and narrative theme escalation.
#It supports the motif, npc, chaos, and narrative systems.

from random import randint
from datetime import datetime

CANONICAL_MOTIFS = [
    "Ascension", "Betrayal", "Chaos", "Collapse", "Compulsion", "Control",
    "Death", "Deception", "Defiance", "Desire", "Destiny", "Echo", "Expansion",
    "Faith", "Fear", "Futility", "Grief", "Guilt", "Hope", "Hunger", "Innocence",
    "Invention", "Isolation", "Justice", "Loyalty", "Madness", "Obsession",
    "Paranoia", "Power", "Pride", "Protection", "Rebirth", "Redemption",
    "Regret", "Revelation", "Ruin", "Sacrifice", "Silence", "Shadow",
    "Stagnation", "Temptation", "Time", "Transformation", "Truth", "Unity",
    "Vengeance", "Worship"
]

def roll_new_motif(exclude=None, chaos_source=False):
    exclude = exclude or []
    options = [m for m in CANONICAL_MOTIFS if m not in exclude]
    theme = random.choice(options)
    lifespan = random.randint(2, 4)
    motif = {
        "theme": theme,
        "lifespan": lifespan,
        "entropy_tick": 0,
        "weight": 6 - lifespan
    }
    if chaos_source:
        motif["chaos_source"] = True
    return motif

def motif_needs_rotation(motif):
    return motif["entropy_tick"] <= 0


def generate_motif():
    life = randint(2, 4)
    return {
        "theme": randint(1, 50),
        "lifespan": life,
        "entropy_tick": 0,
        "weight": 6 - life
    }

def init_motif_pool(n=3):
    return {
        "active_motifs": [generate_motif() for _ in range(n)],
        "motif_history": [],
        "last_rotated": datetime.utcnow().isoformat()
    }

def rotate_expired_motifs(pool):
    rotated = False
    now = datetime.utcnow().isoformat()
    active = []

    for motif in pool.get("active_motifs", []):
        motif["entropy_tick"] += 1
        if motif["entropy_tick"] < motif["lifespan"]:
            active.append(motif)
        else:
            rotated = True
            pool.setdefault("motif_history", []).append(motif["theme"])

    while len(active) < 3:
        active.append(generate_motif())

    if rotated:
        pool["last_rotated"] = now

    pool["active_motifs"] = active
    return pool