from datetime import datetime, timedelta
from typing import Dict, Any
import random

class DecayAndPropagation:
    @staticmethod
    def calculate_decay(truth_value: float, retellings: int, time_passed: timedelta, npc_trait: float) -> float:
        """
        Decay truth value based on number of retellings, time passed, and NPC trait (0=truthful, 1=gossipy).
        """
        decay_factor = 1.0 - (0.05 * retellings) - (0.01 * (time_passed.total_seconds() // 3600)) + (0.05 * (1 - npc_trait))
        return max(0.0, min(100.0, truth_value * decay_factor))

    @staticmethod
    def should_propagate(npc_trait: float, relationship: float) -> bool:
        """
        Determine if a rumor should be propagated based on NPC's gossipy trait and relationship to recipient.
        """
        base_chance = 0.3 + 0.5 * npc_trait + 0.2 * relationship
        return random.random() < min(1.0, base_chance) 
