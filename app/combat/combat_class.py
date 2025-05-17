#This file implements core combat logic for individual actors—players or NPCs. It handles damage application, action slot consumption, and MP usage. It defines battle state manipulation through Combatant and CombatAction.

import random
from app.combat.status_effects_utils import apply_status_effect
from typing import Dict, Any, List, Optional
from app.core.models.character import Character
from app.core.models.npc import NPC
from app.core.database import db

class Combatant:
    """Class representing a combatant in a battle."""
    def __init__(self, entity_id: int, data: Dict[str, Any]):
        self.id = entity_id
        self.type = data.get("type", "character")  # character or npc
        self.attributes = data.get("attributes", {})
        self.feats = data.get("feats", [])
        self.equipment = data.get("equipment", [])
        self.status_effects = data.get("status_effects", [])
        self.action_slots = {
            "action": True,
            "bonus_action": True,
            "reaction": True,
            "movement": data.get("attributes", {}).get("speed", 30)
        }
        self.temp_health = 0
        self.temp_mana = 0
        
    def get_attribute(self, attr: str) -> Any:
        """Get an attribute value."""
        return self.attributes.get(attr)
        
    def set_attribute(self, attr: str, value: Any):
        """Set an attribute value."""
        self.attributes[attr] = value
        
    def has_feat(self, feat_name: str) -> bool:
        """Check if combatant has a feat."""
        return feat_name in self.feats
        
    def has_equipment(self, item_name: str) -> bool:
        """Check if combatant has an equipment item."""
        return item_name in self.equipment
        
    def apply_damage(self, amount: int, damage_type: str = "physical") -> int:
        """Apply damage to the combatant."""
        # Handle temporary health first
        if self.temp_health > 0:
            absorbed = min(self.temp_health, amount)
            self.temp_health -= absorbed
            amount -= absorbed
            
        # Then apply to regular health
        current_health = self.attributes.get("HP", 0)
        new_health = max(0, current_health - amount)
        self.attributes["HP"] = new_health
        
        return amount
        
    def heal(self, amount: int) -> int:
        """Heal the combatant."""
        current_health = self.attributes.get("HP", 0)
        max_health = self.attributes.get("max_HP", 100)
        new_health = min(max_health, current_health + amount)
        self.attributes["HP"] = new_health
        
        return new_health - current_health
        
    def spend_mana(self, amount: int) -> bool:
        """Spend mana if available."""
        current_mana = self.attributes.get("MP", 0) + self.temp_mana
        if current_mana >= amount:
            # Use temporary mana first
            from_temp = min(self.temp_mana, amount)
            self.temp_mana -= from_temp
            remaining = amount - from_temp
            
            if remaining > 0:
                current_base_mana = self.attributes.get("MP", 0)
                self.attributes["MP"] = current_base_mana - remaining
            return True
        return False
        
    def gain_mana(self, amount: int):
        """Gain mana up to max."""
        current_mana = self.attributes.get("MP", 0)
        max_mana = self.attributes.get("max_MP", 100)
        new_mana = min(max_mana, current_mana + amount)
        self.attributes["MP"] = new_mana
        
    def use_action_slot(self, slot_type: str) -> bool:
        """Use an action slot if available."""
        if slot_type in self.action_slots and self.action_slots[slot_type]:
            if slot_type == "movement":
                return True  # Movement is handled separately
            self.action_slots[slot_type] = False
            return True
        return False
        
    def reset_action_slots(self):
        """Reset all action slots."""
        self.action_slots = {
            "action": True,
            "bonus_action": True,
            "reaction": True,
            "movement": self.attributes.get("speed", 30)
        }
        
    def add_status_effect(self, effect: Dict[str, Any]):
        """Add a status effect."""
        self.status_effects.append(effect)
        
    def remove_status_effect(self, effect_name: str):
        """Remove a status effect by name."""
        self.status_effects = [e for e in self.status_effects if e["name"] != effect_name]
        
    def has_status_effect(self, effect_name: str) -> bool:
        """Check if combatant has a status effect."""
        return any(e["name"] == effect_name for e in self.status_effects)
        
    def tick_status_effects(self):
        """Process status effects, reducing duration and removing expired ones."""
        active_effects = []
        for effect in self.status_effects:
            effect["duration"] -= 1
            if effect["duration"] > 0:
                active_effects.append(effect)
        self.status_effects = active_effects

    def set_action(self, action_data, target=None, attacker=None):
        """Set the current action and targets"""
        self.current_action = action_data
        self.target = target
        self.attacker = attacker or self

    def resolve(self):
        """Resolve the current combat action"""
        if not self.current_action:
            return {
                "result": "no_action",
                "character_id": self.id
            }

        # Check and consume action economy slot (default: "action")
        action_type = self.current_action.get("action_type", "action")
        if not self.attacker.use_action_slot(action_type):
            return {
                "result": "slot_used",
                "slot": action_type,
                "character_id": self.id
            }

        # Check MP cost
        mp_cost = self.current_action.get("mp_cost", 0)
        if mp_cost > 0:
            if not self.attacker.spend_mana(mp_cost):
                return {
                    "result": "insufficient_mp",
                    "action": self.current_action.get("name"),
                    "character_id": self.id
                }

        # Damage resolution
        base_damage = self.current_action.get("base_damage", 10)
        damage_dealt = self.target.apply_damage(base_damage)

        # Status effect
        status = self.current_action.get("status_condition")
        if status:
            duration = self.current_action.get("effect_duration", 3)
            apply_status_effect(self.target, status, duration, source=self.attacker.id)

        # Result payload
        result = {
            "attacker": self.attacker.id,
            "target": self.id,
            "action": self.current_action.get("name", "basic_attack"),
            "action_type": action_type,
            "damage": damage_dealt,
            "mp_used": mp_cost,
            "status_applied": status,
            "target_remaining_hp": self.attributes.get("HP", 0)
        }

        # Check for victory condition
        if self.attributes.get("HP", 0) <= 0:
            result["status"] = "victory"
            result["target_status"] = "defeated"
        else:
            result["status"] = "active"

        return result

class CombatManager:
    """Manager class for handling combat encounters."""
    
    def __init__(self, combat_state):
        from app.core.models.combat import CombatEngine
        self.combat_state = combat_state
        self.engine = CombatEngine(combat_state)

    @classmethod
    def create_combat(cls, participants: List[Dict]) -> 'CombatManager':
        """Create a new combat encounter."""
        combat_state = CombatState()
        db.session.add(combat_state)
        db.session.flush()

        for p_data in participants:
            participant = CombatParticipant(
                combat_state_id=combat_state.id,
                character_id=p_data.get('character_id'),
                npc_id=p_data.get('npc_id'),
                current_health=p_data.get('current_health', 0),
                current_mana=p_data.get('current_mana', 0)
            )
            db.session.add(participant)

        db.session.commit()
        return cls(combat_state)

    def add_participant(self, participant_data: Dict):
        """Add a participant to the combat."""
        participant = CombatParticipant(
            combat_state_id=self.combat_state.id,
            character_id=participant_data.get('character_id'),
            npc_id=participant_data.get('npc_id'),
            current_health=participant_data.get('current_health', 0),
            current_mana=participant_data.get('current_mana', 0)
        )
        db.session.add(participant)
        db.session.commit()
        return participant

    def remove_participant(self, participant_id: int) -> None:
        """Remove a participant from the combat."""
        participant = CombatParticipant.query.get(participant_id)
        if participant and participant.combat_state_id == self.combat_state.id:
            db.session.delete(participant)
            db.session.commit()

    def process_action(self, action: Dict) -> Dict:
        """Process a combat action."""
        return self.engine.process_turn(action)

    def end_combat(self) -> None:
        """End the combat encounter."""
        self.combat_state.status = 'completed'
        db.session.commit()

    def get_combat_state(self) -> Dict:
        """Get the current combat state."""
        return self.combat_state.to_dict()

    def get_participants(self) -> List[Dict]:
        """Get all participants in the combat."""
        return [p.to_dict() for p in self.combat_state.participants]

    def get_current_actor(self) -> Optional[Dict]:
        """Get the participant whose turn it is."""
        actor = self.combat_state.get_current_actor()
        return actor.to_dict() if actor else None
