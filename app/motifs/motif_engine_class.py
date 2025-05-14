
#This class encapsulates all logic for narrative motif tracking, rotation, entropy progression, and chaos sensitivity for NPCs. It is the foundation of the pressure-based escalation system.
#It integrates directly with npc, motif, firebase, and chaos systems.

from datetime import datetime
from firebase_admin import db
import random
from app.motifs.motif_utils import (
    CANONICAL_MOTIFS, roll_new_motif,
    motif_needs_rotation
)


class MotifEngine:
    def __init__(self, entity_id, scope="npc"):
        self.entity_id = entity_id
        self.scope = scope
        self.path = self._resolve_path()
        self.ref = db.reference(self.path)
        self.pool = self.ref.get() or {
            "active_motifs": [],
            "motif_history": [],
            "last_rotated": datetime.utcnow().isoformat()
        }

    def _resolve_path(self):
        if self.scope == "npc":
            return f"/npcs/{self.entity_id}/narrative_motif_pool"
        elif self.scope == "pc":
            return f"/pcs/{self.entity_id}/narrative_motif_pool"
        elif self.scope == "poi":
            return f"/poi_state/{self.entity_id}/motif_pool"
        elif self.scope == "region":
            return f"/regional_state/{self.entity_id}/motif_pool"
        else:
            raise ValueError(f"Unknown scope: {self.scope}")

    def _save(self):
        self.ref.set(self.pool)

    def get_pool(self):
        return self.pool

    def get_active_motifs(self):
        return self.pool.get("active_motifs", [])

    def tick_all(self, on_expire=None):
        expired = []
        for motif in self.pool["active_motifs"]:
            motif["entropy_tick"] += 1
            if motif["entropy_tick"] >= motif["lifespan"]:
                expired.append(motif)

        if expired and on_expire:
            for motif in expired:
                on_expire(self.entity_id, motif)

        self.rotate()
        self._save()
        return self

    def tick_random(self, chance=20):
        for motif in self.pool["active_motifs"]:
            if random.randint(1, 100) <= chance:
                motif["entropy_tick"] += 1
        self._save()
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

    def initialize(self, count=3):
        motifs = [roll_new_motift() for _ in range(count)]
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