#This class governs the NPC loyalty and goodwill dynamics, simulating emotional drift, bonding, abandonment, and resistance to relationship change over time or in response to events.
#It supports the npc, relationship, party, and motif systems.

from datetime import datetime
import random
from firebase_admin import db

class LoyaltyManager:
    """
    Manages NPC loyalty and relationship dynamics with both a direct score and goodwill buffer system.
    - score: -10 to 10 loyalty (negative = disloyal, positive = loyal)
    - goodwill: 0 to 36 buffer that influences loyalty shifts
    - auto_abandon: Flag that indicates NPC likely to abandon party
    - tags: Special relationship flags that modify behavior
    """
    def __init__(self, npc_id, loyalty_data=None):
        self.npc_id = npc_id
        self.loyalty = loyalty_data or {
            "score": 0,
            "goodwill": 18,
            "tags": [],
            "last_tick": datetime.utcnow().isoformat(),
            "auto_abandon": False
        }

    def tick(self):
        """Advances loyalty/goodwill over time."""
        score = self.loyalty["score"]
        goodwill = self.loyalty["goodwill"]

        # Regenerate goodwill based on loyalty
        if score == 10:
            self.loyalty["goodwill"] = min(goodwill + 1, 36)
        elif score >= 5 and goodwill < 36:
            self.loyalty["goodwill"] += 1
        elif score <= -5 and goodwill > 0:
            self.loyalty["goodwill"] -= 1

        # Loyalty shift based on goodwill range
        if score < 10 and goodwill >= 30:
            self.loyalty["score"] += 1
        elif score > -10 and goodwill <= 6:
            self.loyalty["score"] -= 1

        # Clamp
        self.loyalty["score"] = max(-10, min(10, self.loyalty["score"]))
        self.loyalty["goodwill"] = max(0, min(36, self.loyalty["goodwill"]))

        # Lock state if bonded or abandoning
        if self.loyalty["score"] <= -5 and self.loyalty["goodwill"] == 0:
            self.loyalty["auto_abandon"] = True
        if self.loyalty["score"] == 10:
            self.loyalty["auto_abandon"] = False  # cannot be lost

        self.loyalty["last_tick"] = datetime.utcnow().isoformat()
        return self.loyalty

    def apply_event(self, impact: dict):
        """Apply goodwill or loyalty shift directly."""
        self.loyalty["goodwill"] += impact.get("goodwill", 0)
        self.loyalty["score"] += impact.get("loyalty", 0)
        return self.tick()  # Re-evaluate thresholds immediately

    def apply_qualifying_event(self, chance=0.5):
        """Roll a qualifying event check."""
        block_chance = self.loyalty["goodwill"] * 0.03  # 3% per goodwill
        final_chance = max(0.0, chance - block_chance)
        if random.random() < final_chance:
            self.loyalty["goodwill"] -= 1
        return self.tick()
    
    def apply_alignment_event(self, alignment_score, character_id=None):
        """
        Apply an alignment-based event to loyalty from a PC interaction.
        Positive alignment increases loyalty, negative decreases it.
        Character-specific modifiers apply if character_id is provided.
        """
        gain_mod = 1.0
        loss_mod = 1.0
        
        # Apply tag-based modifiers
        tags = self.loyalty.get("tags", [])
        if "loyalist" in tags:
            gain_mod, loss_mod = 1.5, 0.5
        elif "coward" in tags:
            gain_mod, loss_mod = 0.5, 1.5
        elif "bestie" in tags:
            self.loyalty["score"] = 10  # Always loyal
            gain_mod, loss_mod = 2.0, 0.1
        elif "nemesis" in tags:
            self.loyalty["score"] = -10  # Always disloyal
            gain_mod, loss_mod = 0.1, 2.0
            
        # Apply the score changes
        if alignment_score > 0:
            self.loyalty["score"] += int(alignment_score * gain_mod)
            self.loyalty["goodwill"] += 1
        elif alignment_score < 0:
            self.loyalty["score"] += int(alignment_score * loss_mod)
            self.loyalty["goodwill"] -= abs(alignment_score)
            
        # Ripple faction opinion if character ID provided
        if character_id:
            self._ripple_faction_opinion(character_id, alignment_score)
            
        return self.tick()
    
    def _ripple_faction_opinion(self, character_id, alignment_score):
        """Updates faction opinions based on character interaction."""
        try:
            pc_factions = db.reference(f"/pcs/{character_id}/faction_affiliations").get() or []
            for faction in pc_factions:
                faction_ref = db.reference(f"/npcs/{self.npc_id}/faction_opinions/{faction}")
                prev_opinion = faction_ref.get() or 0
                faction_ref.set(prev_opinion + (1 if alignment_score > 0 else -1))
        except Exception:
            # Fail silently if Firebase access fails
            pass
    
    def should_abandon(self) -> bool:
        """Check if NPC should abandon the party based on loyalty score and goodwill."""
        return self.loyalty["goodwill"] <= 0 and self.loyalty["score"] <= -5
    
    def save_to_firebase(self, character_id=None):
        """Save loyalty data to Firebase."""
        path = f"/npcs/{self.npc_id}"
        if character_id:
            path += f"/relationships/{character_id}"
        db.reference(path).update({"loyalty": self.loyalty})
        return self.loyalty
    
    @classmethod
    def load_from_firebase(cls, npc_id, character_id=None):
        """Load loyalty data from Firebase."""
        path = f"/npcs/{npc_id}"
        if character_id:
            path += f"/relationships/{character_id}"
        data = db.reference(path).get() or {}
        loyalty_data = data.get("loyalty")
        return cls(npc_id, loyalty_data)

    def to_dict(self):
        return self.loyalty
