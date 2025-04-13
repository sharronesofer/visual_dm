import random

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
    return motif["entropy_tick"] >= motif["lifespan"]
