from typing import Any
import difflib

class TruthTracker:
    @staticmethod
    def calculate_truth_value(original: str, rumor: str) -> float:
        """Calculate a percentage-based truth value between the original event and the rumor."""
        seq = difflib.SequenceMatcher(None, original, rumor)
        return round(seq.ratio() * 100, 2)

    @staticmethod
    def update_truth_value(prev_truth: float, new_truth: float, decay: float = 0.95) -> float:
        """Update the truth value, applying a decay factor for each retelling."""
        return round(new_truth * decay, 2) 