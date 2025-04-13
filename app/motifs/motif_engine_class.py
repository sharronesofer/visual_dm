from datetime import datetime
from firebase_admin import db
import random
from app.utils.motif_utils import (
    CANONICAL_MOTIFS, roll_new_motif,
    motif_needs_rotation
)

class MotifEngine:
    def __init__(self, npc_id):
        self.npc_id = npc_id
        self.ref = db.reference(f"/npcs/{npc_id}/narrative_motif_pool")
        self.pool = self.ref.get() or {
            "active_motifs": [],
            "motif_history": [],
            "last_rotated": datetime.utcnow().isoformat()
        }

    def _save(self):
        self.ref.set(self.pool)

    def get_pool(self):
        return self.pool

    def get_active_motifs(self):
        return self.pool.get("active_motifs", [])

    def tick_all(self):
        for motif in self.pool["active_motifs"]:
            motif["entropy_tick"] += 1
        return self

    def tick_random(self, chance=20):
        for motif in self.pool["active_motifs"]:
            if random.randint(1, 100) <= chance:
                motif["entropy_tick"] += 1
        return self

    def rotate(self, chaos=False):
        active = []
        history = self.pool.get("motif_history", [])

        for motif in self.pool["active_motifs"]:
            if motif_needs_rotation(motif):
                history.append(motif["theme"])
            else:
                active.append(motif)

        while len(active) < 3:
            exclude = [m["theme"] for m in active] + history
            new_motif = roll_new_motif(exclude, chaos_source=chaos)
            active.append(new_motif)
            history.append(new_motif["theme"])

        self.pool["active_motifs"] = active
        self.pool["motif_history"] = history
        self.pool["last_rotated"] = datetime.utcnow().isoformat()
        return self

    def check_aggression_threshold(self):
        weights = [m["weight"] for m in self.pool.get("active_motifs", [])]
        if any(w >= 5 for w in weights):
            return "aggression_5"
        if len([w for w in weights if w >= 4]) >= 2:
            return "dual_pressure"
        return None

    def describe(self):
        return {
            "npc_id": self.npc_id,
            "motifs": self.pool["active_motifs"],
            "history": self.pool.get("motif_history", []),
            "last_rotated": self.pool.get("last_rotated")
        }

    def initialize(self, count=3):
        motifs = [roll_new_motif() for _ in range(count)]
        self.pool = {
            "active_motifs": motifs,
            "motif_history": [m["theme"] for m in motifs],
            "last_rotated": datetime.utcnow().isoformat()
        }
        self._save()
        return self

    def save(self):
        self._save()
        return self
