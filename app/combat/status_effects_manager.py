from typing import List, Dict, Any, Optional
from datetime import datetime
from app.combat.status_effects import StatusEffectsSystem, load_effects_from_config
import os

# Singleton/shared instance of the system and loader
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'effects', 'effects_config.json')
EFFECTS = load_effects_from_config(CONFIG_PATH)
STATUS_EFFECTS_SYSTEM = StatusEffectsSystem()
for effect in EFFECTS.values():
    STATUS_EFFECTS_SYSTEM.register_effect(effect)

class StatusEffectManager:
    """
    Manages application, removal, and processing of status effects for combat participants using the new data-driven system.
    Handles stacking, duration, and effect resolution at start/end of turn.
    """
    def __init__(self, db_session, system=None):
        self.db = db_session
        self.system = system if system is not None else STATUS_EFFECTS_SYSTEM

    def _sync_participant_effects(self, participant):
        target_id = str(participant.id)
        active = self.system.get_active_effects(target_id)
        participant.status_effects = [
            {
                'id': inst.effect.id,
                'name': inst.effect.name,
                'duration': inst.remaining_duration,
                'magnitude': inst.effect.modifiers[0].value if inst.effect.modifiers else None,
                'stacks': inst.current_stacks
            }
            for inst in active
        ]

    def apply_effect(self, participant, effect_id: str, stacking: str = "refresh") -> Optional[str]:
        target_id = str(participant.id)
        now = datetime.utcnow()
        active_effects = self.system.get_active_effects(target_id)
        effect = self.system.get_effect(effect_id)
        if not effect:
            return None
        existing = next((e for e in active_effects if e.effect.id == effect_id), None)
        result = None
        if existing:
            if stacking == "refresh":
                existing.remaining_duration = effect.duration_value
                existing.start_time = now
                result = existing.id
            elif stacking == "replace":
                self.system.remove_effect(target_id, existing.id)
                result = self.system.apply_effect(target_id, effect_id, now)
            elif stacking == "stack":
                if effect.stackable:
                    if existing.add_stack():
                        result = existing.id
                    else:
                        result = None
                else:
                    result = None
            elif stacking == "ignore":
                result = existing.id
        else:
            result = self.system.apply_effect(target_id, effect_id, now)
        self._sync_participant_effects(participant)
        return result

    def remove_effect(self, participant, effect_id: str) -> bool:
        target_id = str(participant.id)
        active_effects = self.system.get_active_effects(target_id)
        result = False
        for inst in active_effects:
            if inst.effect.id == effect_id:
                result = self.system.remove_effect(target_id, inst.id)
        self._sync_participant_effects(participant)
        return result

    def process_start_of_turn(self, participant) -> None:
        target_id = str(participant.id)
        for inst in self.system.get_active_effects(target_id):
            if inst.effect.custom_logic.get('timing', 'start') in ('start', 'both'):
                self._resolve_effect(participant, inst)
        self.db.commit()

    def process_end_of_turn(self, participant) -> None:
        target_id = str(participant.id)
        for inst in self.system.get_active_effects(target_id):
            if inst.effect.custom_logic.get('timing', 'start') in ('end', 'both'):
                self._resolve_effect(participant, inst)
        self.db.commit()

    def decrement_durations(self, participant) -> None:
        target_id = str(participant.id)
        active = self.system.get_active_effects(target_id)
        to_remove = []
        for inst in active:
            if not inst.update_duration(1):
                to_remove.append(inst.id)
        for inst_id in to_remove:
            self.system.remove_effect(target_id, inst_id)
        self._sync_participant_effects(participant)
        self.db.commit()

    def _resolve_effect(self, participant, inst) -> None:
        effect = inst.effect
        magnitude = 1
        for mod in effect.modifiers:
            if mod.attribute == 'damage':
                participant.take_damage(mod.value * inst.current_stacks)
            elif mod.attribute == 'heal':
                participant.heal(mod.value * inst.current_stacks)
            elif mod.attribute == 'action_points':
                participant.action_points = 0
        # Extend for more attributes and custom logic as needed 