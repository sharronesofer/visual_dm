from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.models.combat import CombatParticipant
from app.core.models.status import StatusEffect, EffectType
from sqlalchemy.orm.session import Session

class StatusEffectManager:
    """
    Manages application, removal, and processing of status effects for combat participants.
    Handles stacking, duration, and effect resolution at start/end of turn.
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def apply_effect(self, participant: CombatParticipant, effect_data: Dict[str, Any], stacking: str = "refresh") -> None:
        """
        Apply a status effect to a participant.
        stacking: 'refresh' (refresh duration), 'replace', 'stack', 'ignore'
        """
        name = effect_data['name']
        found = None
        for e in participant.status_effects:
            if e['name'] == name:
                found = e
                break
        if found:
            if stacking == "refresh":
                found['duration'] = effect_data['duration']
                found['magnitude'] = effect_data.get('magnitude', found.get('magnitude', 1))
            elif stacking == "replace":
                participant.status_effects.remove(found)
                participant.status_effects.append(effect_data)
            elif stacking == "stack":
                participant.status_effects.append(effect_data)
            elif stacking == "ignore":
                return
        else:
            participant.status_effects.append(effect_data)
        participant.updated_at = datetime.utcnow()
        self.db.commit()

    def remove_effect(self, participant: CombatParticipant, effect_name: str) -> None:
        """
        Remove a status effect by name from a participant.
        """
        participant.status_effects = [e for e in participant.status_effects if e['name'] != effect_name]
        participant.updated_at = datetime.utcnow()
        self.db.commit()

    def process_start_of_turn(self, participant: CombatParticipant) -> None:
        """
        Resolve effects that trigger at the start of the participant's turn.
        """
        for effect in participant.status_effects:
            if effect.get('timing', 'start') in ('start', 'both'):
                self._resolve_effect(participant, effect)
        self.db.commit()

    def process_end_of_turn(self, participant: CombatParticipant) -> None:
        """
        Resolve effects that trigger at the end of the participant's turn.
        """
        for effect in participant.status_effects:
            if effect.get('timing', 'start') in ('end', 'both'):
                self._resolve_effect(participant, effect)
        self.db.commit()

    def decrement_durations(self, participant: CombatParticipant) -> None:
        """
        Decrement durations and remove expired effects.
        """
        updated = []
        for effect in participant.status_effects:
            if effect.get('duration', 0) < 0:
                updated.append(effect)
                continue
            effect['duration'] -= 1
            if effect['duration'] > 0:
                updated.append(effect)
        participant.status_effects = updated
        participant.updated_at = datetime.utcnow()
        self.db.commit()

    def _resolve_effect(self, participant: CombatParticipant, effect: Dict[str, Any]) -> None:
        """
        Apply the effect's impact to the participant. Extend as needed for new effects.
        """
        name = effect['name']
        magnitude = effect.get('magnitude', 1)
        if name == 'poisoned':
            participant.take_damage(magnitude)
        elif name == 'blessed':
            participant.heal(magnitude)
        elif name == 'stunned':
            participant.action_points = 0
        # Add more effect types as needed
        # Custom logic for buffs, debuffs, etc. 