"""
Combat state management.
Provides functionality for tracking and managing combat state.
"""

from typing import Dict, List, Optional
from app.core.models.combat import CombatState, CombatParticipant, CombatEngine
from app.core.models.character import Character
from app.core.models.npc import NPC
from app.core.database import db

class CombatStateManager:
    """Manager class for handling combat state."""
    
    def __init__(self, combat_state: CombatState):
        self.combat_state = combat_state
        self.engine = CombatEngine(combat_state)

    def get_state(self) -> Dict:
        """Get the current combat state."""
        return self.combat_state.to_dict()

    def get_participants(self) -> List[Dict]:
        """Get all participants in the combat."""
        return [p.to_dict() for p in self.combat_state.participants]

    def get_current_actor(self) -> Optional[Dict]:
        """Get the participant whose turn it is."""
        actor = self.combat_state.get_current_actor()
        return actor.to_dict() if actor else None

    def advance_turn(self) -> Dict:
        """Advance to the next turn in combat."""
        self.combat_state.next_turn()
        db.session.commit()
        return self.get_state()

    def update_participant(self, participant_id: int, updates: Dict) -> Dict:
        """Update a participant's state."""
        participant = CombatParticipant.query.get(participant_id)
        if not participant or participant.combat_state_id != self.combat_state.id:
            raise ValueError("Participant not found in combat")

        for key, value in updates.items():
            if hasattr(participant, key):
                setattr(participant, key, value)

        db.session.commit()
        return participant.to_dict()

    def add_status_effect(self, participant_id: int, effect: str, duration: int) -> Dict:
        """Add a status effect to a participant."""
        participant = CombatParticipant.query.get(participant_id)
        if not participant or participant.combat_state_id != self.combat_state.id:
            raise ValueError("Participant not found in combat")

        participant.add_status_effect(effect, duration)
        db.session.commit()
        return participant.to_dict()

    def remove_status_effect(self, participant_id: int, effect: str) -> Dict:
        """Remove a status effect from a participant."""
        participant = CombatParticipant.query.get(participant_id)
        if not participant or participant.combat_state_id != self.combat_state.id:
            raise ValueError("Participant not found in combat")

        participant.remove_status_effect(effect)
        db.session.commit()
        return participant.to_dict()

    def check_combat_end(self) -> bool:
        """Check if combat should end."""
        active_participants = [p for p in self.combat_state.participants if p.current_health > 0]
        if len(active_participants) <= 1:
            self.combat_state.status = 'completed'
            db.session.commit()
            return True
        return False
