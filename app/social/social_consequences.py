from typing import Dict, List, Optional
from .social_utils import SocialInteraction

class SocialConsequences:
    CONSEQUENCES = {
        "critical_success": {
            "Persuasion": {
                "Negotiate better prices": "Get 50% better deal and gain favor",
                "Convince someone to help you": "Get enthusiastic help and future favors",
                "Change someone's opinion": "Complete change of heart and new ally",
                "Get someone to reveal information": "Get all information and more",
                "Convince someone to take a risk": "They take the risk and succeed"
            },
            "Deception": {
                "Bluff your way past guards": "Guards become helpful",
                "Conceal your true intentions": "Target becomes suspicious of others",
                "Create a false identity": "Identity becomes widely accepted",
                "Spread misinformation": "Misinformation spreads rapidly",
                "Fake an emotion or reaction": "Emotion appears completely genuine"
            },
            "Intimidation": {
                "Extort information": "Get all information and future cooperation",
                "Force compliance": "Complete submission and future fear",
                "Break someone's will": "Permanent psychological effect",
                "Establish dominance": "Complete respect and fear",
                "Scare off potential threats": "Threats flee and spread word"
            },
            "Insight": {
                "Detect lies": "See through all deception",
                "Sense hidden motives": "Understand full context",
                "Read emotional state": "Know exact emotional state",
                "Predict reactions": "Know exact future reactions",
                "Understand social dynamics": "Master social situation"
            }
        },
        "success": {
            "Persuasion": {
                "Negotiate better prices": "Get 25% better deal",
                "Convince someone to help you": "Get help as requested",
                "Change someone's opinion": "Partial change of opinion",
                "Get someone to reveal information": "Get requested information",
                "Convince someone to take a risk": "They take the risk"
            },
            "Deception": {
                "Bluff your way past guards": "Guards let you pass",
                "Conceal your true intentions": "Target remains unaware",
                "Create a false identity": "Identity is accepted",
                "Spread misinformation": "Misinformation is believed",
                "Fake an emotion or reaction": "Emotion appears genuine"
            },
            "Intimidation": {
                "Extort information": "Get requested information",
                "Force compliance": "Get compliance as requested",
                "Break someone's will": "Temporary submission",
                "Establish dominance": "Respect and caution",
                "Scare off potential threats": "Threats back off"
            },
            "Insight": {
                "Detect lies": "Detect major lies",
                "Sense hidden motives": "Understand main motives",
                "Read emotional state": "Know general emotional state",
                "Predict reactions": "Predict likely reactions",
                "Understand social dynamics": "Understand main dynamics"
            }
        },
        "failure": {
            "Persuasion": {
                "Negotiate better prices": "No better deal",
                "Convince someone to help you": "No help given",
                "Change someone's opinion": "No change in opinion",
                "Get someone to reveal information": "No information given",
                "Convince someone to take a risk": "They refuse"
            },
            "Deception": {
                "Bluff your way past guards": "Guards remain suspicious",
                "Conceal your true intentions": "Target becomes suspicious",
                "Create a false identity": "Identity is questioned",
                "Spread misinformation": "Misinformation is doubted",
                "Fake an emotion or reaction": "Emotion seems forced"
            },
            "Intimidation": {
                "Extort information": "No information given",
                "Force compliance": "No compliance given",
                "Break someone's will": "No effect",
                "Establish dominance": "No respect gained",
                "Scare off potential threats": "Threats remain"
            },
            "Insight": {
                "Detect lies": "Miss major lies",
                "Sense hidden motives": "Miss main motives",
                "Read emotional state": "Misread emotional state",
                "Predict reactions": "Misjudge reactions",
                "Understand social dynamics": "Misunderstand dynamics"
            }
        },
        "critical_failure": {
            "Persuasion": {
                "Negotiate better prices": "Get worse deal and lose favor",
                "Convince someone to help you": "They become hostile",
                "Change someone's opinion": "Strengthened opposing view",
                "Get someone to reveal information": "They become suspicious",
                "Convince someone to take a risk": "They warn others about you"
            },
            "Deception": {
                "Bluff your way past guards": "Guards become hostile",
                "Conceal your true intentions": "Target sees through you",
                "Create a false identity": "Identity is exposed",
                "Spread misinformation": "Truth comes out",
                "Fake an emotion or reaction": "Emotion seems completely fake"
            },
            "Intimidation": {
                "Extort information": "They report you",
                "Force compliance": "They resist strongly",
                "Break someone's will": "They become defiant",
                "Establish dominance": "They challenge you",
                "Scare off potential threats": "Threats become aggressive"
            },
            "Insight": {
                "Detect lies": "Believe obvious lies",
                "Sense hidden motives": "Completely misread motives",
                "Read emotional state": "Completely misread emotions",
                "Predict reactions": "Completely misjudge reactions",
                "Understand social dynamics": "Completely misunderstand situation"
            }
        }
    }

    @classmethod
    def get_consequence(cls, degree: str, skill: str, application: str) -> Optional[str]:
        """Get the consequence for a specific interaction result."""
        if degree not in cls.CONSEQUENCES:
            return None
        skill_consequences = cls.CONSEQUENCES[degree].get(skill)
        if not skill_consequences:
            return None
        return skill_consequences.get(application)

    @classmethod
    def get_all_consequences(cls, degree: str, skill: str) -> Optional[Dict[str, str]]:
        """Get all consequences for a specific skill at a given degree of success/failure."""
        if degree not in cls.CONSEQUENCES:
            return None
        return cls.CONSEQUENCES[degree].get(skill) 