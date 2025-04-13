from datetime import datetime
import random

class LoyaltyManager:
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

    def to_dict(self):
        return self.loyalty
