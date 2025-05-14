from typing import Dict, List, Optional, Tuple
from .social_utils import SocialInteraction
from .social_skills import SocialSkills
from .social_consequences import SocialConsequences

class SocialWorld:
    def __init__(self):
        self.active_interactions: Dict[str, SocialInteraction] = {}
        self.relationship_changes: Dict[str, Dict[str, int]] = {}
        self.reputation_changes: Dict[str, Dict[str, int]] = {}

    def start_interaction(self, npc_id: str, character_id: str, relationship_status: str = "neutral") -> str:
        """Start a new social interaction and return its ID."""
        interaction_id = f"{npc_id}_{character_id}"
        if interaction_id not in self.active_interactions:
            self.active_interactions[interaction_id] = SocialInteraction(npc_id, relationship_status)
        return interaction_id

    def end_interaction(self, interaction_id: str):
        """End a social interaction and process its effects."""
        if interaction_id in self.active_interactions:
            del self.active_interactions[interaction_id]

    def process_interaction_result(self,
                                 interaction_id: str,
                                 character: Dict,
                                 skill: str,
                                 application: str,
                                 result: Dict) -> Dict:
        """Process the results of a social interaction and update the world state."""
        if interaction_id not in self.active_interactions:
            return {"error": "Interaction not found"}

        interaction = self.active_interactions[interaction_id]
        npc_id = interaction.npc_id
        character_id = character["id"]

        # Get the consequence
        consequence = SocialConsequences.get_consequence(
            result["degree"],
            skill,
            application
        )

        # Update relationship based on result
        relationship_change = self._calculate_relationship_change(
            skill,
            application,
            result["degree"]
        )

        # Update reputation based on result
        reputation_change = self._calculate_reputation_change(
            skill,
            application,
            result["degree"]
        )

        # Apply changes
        self._update_relationship(npc_id, character_id, relationship_change)
        self._update_reputation(character_id, reputation_change)

        return {
            "consequence": consequence,
            "relationship_change": relationship_change,
            "reputation_change": reputation_change,
            "new_relationship": self._get_relationship(npc_id, character_id),
            "new_reputation": self._get_reputation(character_id)
        }

    def _calculate_relationship_change(self,
                                     skill: str,
                                     application: str,
                                     degree: str) -> int:
        """Calculate how much the relationship changes based on the interaction."""
        base_changes = {
            "critical_success": 2,
            "success": 1,
            "failure": -1,
            "critical_failure": -2
        }

        skill_modifiers = {
            "Persuasion": 1,
            "Deception": -1,
            "Intimidation": -2,
            "Insight": 0
        }

        base_change = base_changes.get(degree, 0)
        skill_modifier = skill_modifiers.get(skill, 0)

        return base_change + skill_modifier

    def _calculate_reputation_change(self,
                                   skill: str,
                                   application: str,
                                   degree: str) -> Dict[str, int]:
        """Calculate how much the character's reputation changes."""
        changes = {
            "critical_success": {
                "Persuasion": {"diplomatic": 2, "intimidating": 0},
                "Deception": {"diplomatic": -1, "intimidating": 0},
                "Intimidation": {"diplomatic": -2, "intimidating": 2},
                "Insight": {"diplomatic": 1, "intimidating": 0}
            },
            "success": {
                "Persuasion": {"diplomatic": 1, "intimidating": 0},
                "Deception": {"diplomatic": -1, "intimidating": 0},
                "Intimidation": {"diplomatic": -1, "intimidating": 1},
                "Insight": {"diplomatic": 0, "intimidating": 0}
            },
            "failure": {
                "Persuasion": {"diplomatic": -1, "intimidating": 0},
                "Deception": {"diplomatic": -1, "intimidating": 0},
                "Intimidation": {"diplomatic": -1, "intimidating": -1},
                "Insight": {"diplomatic": 0, "intimidating": 0}
            },
            "critical_failure": {
                "Persuasion": {"diplomatic": -2, "intimidating": 0},
                "Deception": {"diplomatic": -2, "intimidating": 0},
                "Intimidation": {"diplomatic": -2, "intimidating": -2},
                "Insight": {"diplomatic": -1, "intimidating": 0}
            }
        }

        return changes.get(degree, {}).get(skill, {"diplomatic": 0, "intimidating": 0})

    def _update_relationship(self, npc_id: str, character_id: str, change: int):
        """Update the relationship between an NPC and character."""
        key = f"{npc_id}_{character_id}"
        if key not in self.relationship_changes:
            self.relationship_changes[key] = 0
        self.relationship_changes[key] += change

    def _update_reputation(self, character_id: str, changes: Dict[str, int]):
        """Update a character's reputation."""
        if character_id not in self.reputation_changes:
            self.reputation_changes[character_id] = {"diplomatic": 0, "intimidating": 0}
        
        for rep_type, change in changes.items():
            self.reputation_changes[character_id][rep_type] += change

    def _get_relationship(self, npc_id: str, character_id: str) -> int:
        """Get the current relationship value between an NPC and character."""
        key = f"{npc_id}_{character_id}"
        return self.relationship_changes.get(key, 0)

    def _get_reputation(self, character_id: str) -> Dict[str, int]:
        """Get a character's current reputation values."""
        return self.reputation_changes.get(character_id, {"diplomatic": 0, "intimidating": 0}) 