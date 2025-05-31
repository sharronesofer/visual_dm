import random
from typing import Dict, Any, List, Optional

class RandomCharacterGenerator:
    """
    Generates random character customization data with weighted probabilities and feature locking.
    """
    def __init__(self, feature_weights: Dict[str, Dict[Any, float]]):
        self.feature_weights = feature_weights  # e.g., {"hair_color": {"blonde": 0.2, "black": 0.5, ...}}

    def weighted_choice(self, choices: Dict[Any, float]) -> Any:
        total = sum(choices.values())
        r = random.uniform(0, total)
        upto = 0
        for k, w in choices.items():
            if upto + w >= r:
                return k
            upto += w
        assert False, "Shouldn't get here"

    def generate(self, locked: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a random character customization dict, respecting locked features.
        """
        locked = locked or {}
        result = dict(locked)
        for feature, weights in self.feature_weights.items():
            if feature not in result:
                result[feature] = self.weighted_choice(weights)
        return result 