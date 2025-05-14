from typing import Dict, List, Optional
from .social_utils import SocialInteraction

class SocialSkills:
    SKILL_APPLICATIONS = {
        "Persuasion": {
            "description": "Convince others to see things your way",
            "applications": [
                "Negotiate better prices",
                "Convince someone to help you",
                "Change someone's opinion",
                "Get someone to reveal information",
                "Convince someone to take a risk"
            ],
            "dc_modifiers": {
                "Negotiate better prices": {"request_difficulty": "moderate"},
                "Convince someone to help you": {"request_difficulty": "hard"},
                "Change someone's opinion": {"request_difficulty": "very_hard"},
                "Get someone to reveal information": {"request_difficulty": "hard"},
                "Convince someone to take a risk": {"request_difficulty": "very_hard"}
            }
        },
        "Deception": {
            "description": "Lie, mislead, or conceal the truth",
            "applications": [
                "Bluff your way past guards",
                "Conceal your true intentions",
                "Create a false identity",
                "Spread misinformation",
                "Fake an emotion or reaction"
            ],
            "dc_modifiers": {
                "Bluff your way past guards": {"request_difficulty": "hard"},
                "Conceal your true intentions": {"request_difficulty": "moderate"},
                "Create a false identity": {"request_difficulty": "very_hard"},
                "Spread misinformation": {"request_difficulty": "moderate"},
                "Fake an emotion or reaction": {"request_difficulty": "easy"}
            }
        },
        "Intimidation": {
            "description": "Influence others through threats or displays of power",
            "applications": [
                "Extort information",
                "Force compliance",
                "Break someone's will",
                "Establish dominance",
                "Scare off potential threats"
            ],
            "dc_modifiers": {
                "Extort information": {"request_difficulty": "hard"},
                "Force compliance": {"request_difficulty": "very_hard"},
                "Break someone's will": {"request_difficulty": "very_hard"},
                "Establish dominance": {"request_difficulty": "moderate"},
                "Scare off potential threats": {"request_difficulty": "moderate"}
            }
        },
        "Insight": {
            "description": "Read people's emotions and intentions",
            "applications": [
                "Detect lies",
                "Sense hidden motives",
                "Read emotional state",
                "Predict reactions",
                "Understand social dynamics"
            ],
            "dc_modifiers": {
                "Detect lies": {"request_difficulty": "moderate"},
                "Sense hidden motives": {"request_difficulty": "hard"},
                "Read emotional state": {"request_difficulty": "easy"},
                "Predict reactions": {"request_difficulty": "moderate"},
                "Understand social dynamics": {"request_difficulty": "moderate"}
            }
        }
    }

    @classmethod
    def get_skill_info(cls, skill: str) -> Optional[Dict]:
        """Get information about a specific social skill."""
        return cls.SKILL_APPLICATIONS.get(skill)

    @classmethod
    def get_all_skills(cls) -> List[str]:
        """Get a list of all social skills."""
        return list(cls.SKILL_APPLICATIONS.keys())

    @classmethod
    def get_skill_applications(cls, skill: str) -> Optional[List[str]]:
        """Get all possible applications for a specific skill."""
        skill_info = cls.get_skill_info(skill)
        return skill_info["applications"] if skill_info else None

    @classmethod
    def get_application_dc_modifiers(cls, skill: str, application: str) -> Optional[Dict]:
        """Get DC modifiers for a specific skill application."""
        skill_info = cls.get_skill_info(skill)
        if not skill_info:
            return None
        return skill_info["dc_modifiers"].get(application) 