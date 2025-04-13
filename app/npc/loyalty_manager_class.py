from datetime import datetime

class LoyaltyManager:
    def __init__(self, npc_id, loyalty_data=None):
        self.npc_id = npc_id
        self.loyalty = loyalty_data or {
            "score": 0,
            "goodwill": 5,
            "tags": [],  # e.g., ["coward", "nemesis"]
            "last_tick": datetime.utcnow().isoformat()
        }

    def tick(self):
        """Advances loyalty/goodwill logic on a regular basis."""
        # Example: regenerate 1 goodwill if loyalty is high
        if self.loyalty["goodwill"] < 5 and self.loyalty["score"] > 3:
            self.loyalty["goodwill"] += 1

        self.loyalty["last_tick"] = datetime.utcnow().isoformat()
        return self.loyalty

    def apply_event(self, impact, reason=None):
        """
        Applies an event that adjusts goodwill and/or loyalty.
        `impact` = {"goodwill": -1, "loyalty": +2}
        """
        self.loyalty["goodwill"] += impact.get("goodwill", 0)
        self.loyalty["score"] += impact.get("loyalty", 0)

        # Optional: log reasons in the future
        if self.loyalty["goodwill"] < 0:
            self.loyalty["goodwill"] = 0
        if self.loyalty["score"] > 10:
            self.loyalty["score"] = 10
        if self.loyalty["score"] < -10:
            self.loyalty["score"] = -10

        return self.loyalty

    def add_tag(self, tag):
        if tag not in self.loyalty["tags"]:
            self.loyalty["tags"].append(tag)

    def remove_tag(self, tag):
        if tag in self.loyalty["tags"]:
            self.loyalty["tags"].remove(tag)

    def to_dict(self):
        return self.loyalty
