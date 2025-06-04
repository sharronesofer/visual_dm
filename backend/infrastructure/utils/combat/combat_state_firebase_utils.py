"""
This module manages Firebase-based combat state, including starting battles, applying actions,
syncing post-combat data, and resolving status effects. It bridges tactical logic and persistent state.
"""

from datetime import datetime
import random
import logging
from typing import Dict, Any, List, Optional

# Use fallback imports for missing dependencies
try:
#     from firebase_admin import db  # TODO: Replace with proper database integration
    from backend.systems.combat.utils import roll_initiative
    from backend.systems.combat.status_effects import apply_status_effect
    from backend.infrastructure.database_services.combat_status_effects_service import resolve_status_effects
except ImportError:
    # Fallback mock objects for resilience
    db = None
    def roll_initiative(*args, **kwargs):
        return random.randint(1, 20)
    def apply_status_effect(*args, **kwargs):
        pass
    def resolve_status_effects(*args, **kwargs):
        pass

class CombatActionHandler:
    def __init__(self, battle_id: str, actor_id: str, target_id: str):
        self.battle_id = battle_id
        self.actor_id = actor_id
        self.target_id = target_id
        
        if db:
            self.ref = db.reference(f"/combat_state/{battle_id}")
            self.combat_data = self.ref.get()
        else:
            # Fallback for testing
            self.ref = None
            self.combat_data = {"participants": {}, "turn_order": [], "current_turn": 0}
            
        self._validate_combat_exists()
        self.actor = self._get_participant(actor_id)
        self.target = self._get_participant(target_id)

    def _validate_combat_exists(self):
        if not self.combat_data:
            raise ValueError("Battle not found.")

    def _get_participant(self, pid: str):
        return self.combat_data["participants"].get(pid)

    def is_actor_turn(self) -> bool:
        current_turn = self.combat_data.get("current_turn", 0)
        turn_order = self.combat_data.get("turn_order", [])
        if not turn_order:
            return False
        return turn_order[current_turn] == self.actor_id

    def apply_action(self, action_type: str, roll: int, value: int, 
                    notes: str = "", status_effect: str = None, spell_name: str = None):
        if not self.is_actor_turn():
            return {"error": "It's not this character's turn."}, 400

        if not self.actor or not self.target:
            return {"error": "Invalid actor or target ID."}, 400

        narration = self._narrate_action(action_type, value, roll, status_effect, spell_name, notes)

        # Apply updated state
        self.combat_data["participants"][self.target_id] = self.target
        self.combat_data.setdefault("log", []).append(narration)

        # Tick down all status effects for all participants using the centralized function
        for p_id in self.combat_data["participants"]:
            resolve_status_effects(p_id)

        self._advance_turn()
        
        if self.ref:
            self.ref.set(self.combat_data)

        return {
            "result": "success",
            "updated_target": self.target,
            "next_turn": self._get_next_turn_id(),
            "log": self.combat_data["log"][-5:]
        }, 200

    def _narrate_action(self, action_type: str, value: int, roll: int, 
                       status_effect: str, spell_name: str, notes: str) -> str:
        narration = f"{self.actor['name']} uses {action_type}"
        if spell_name:
            narration = f"{self.actor['name']} casts {spell_name}"

        if action_type == "attack" and roll >= self.target.get("AC", 10):
            damage = max(0, value)
            self.target["HP"] = max(0, self.target["HP"] - damage)
            narration += f" and hits {self.target['name']} for {damage} damage!"
        elif action_type == "heal":
            self.target["HP"] += value
            narration += f" and heals {self.target['name']} for {value} HP!"
        else:
            narration += " but it fails."

        if status_effect:
            # Use the centralized apply_status_effect function
            apply_status_effect(self.target, status_effect, duration=2, source=self.actor_id, value=True)
            narration += f" {self.target['name']} is now {status_effect}!"

        if notes:
            narration += f" ({notes})"

        return narration

    def _advance_turn(self):
        turn_order = self.combat_data.get("turn_order", [])
        current_turn = self.combat_data.get("current_turn", 0)
        self.combat_data["current_turn"] = (current_turn + 1) % len(turn_order)

    def _get_next_turn_id(self) -> str:
        turn_order = self.combat_data["turn_order"]
        current_turn = self.combat_data["current_turn"]
        if turn_order:
            return turn_order[current_turn]
        return ""

def start_firebase_combat(encounter_name: str, player_party: list, enemy_party: list, battle_map: dict = None):
    """Start a new Firebase-based combat encounter."""
    battle_id = str(random.randint(100000, 999999))
    participants = {}

    for char in player_party + enemy_party:
        participants[char["id"]] = {
            "name": char["name"],
            "team": "party" if char in player_party else "hostile",
            "HP": char.get("HP", 20),
            "AC": char.get("AC", 12),
            "DEX": char.get("DEX", 10),
            "initiative": roll_initiative(char.get("DEX", 10)),
            "status_effects": []
        }

    sorted_order = sorted(participants, key=lambda pid: participants[pid]["initiative"], reverse=True)

    combat_state = {
        "battle_id": battle_id,
        "name": encounter_name,
        "participants": participants,
        "turn_order": sorted_order,
        "current_turn": 0,
        "battle_map": battle_map or {"type": "open", "lighting": "normal"},
        "started_at": datetime.utcnow().isoformat(),
        "log": []
    }

    if db:
        db.reference(f"/combat_state/{battle_id}").set(combat_state)

    return battle_id, combat_state

def sync_post_combat_state_to_firebase(party: list, enemies: list):
    """
    Push post-combat health, temp HP, and persistent status effects to Firebase.
    """
    if not db:
        return
        
    all_combatants = party + enemies

    for c in all_combatants:
        ref_path = f"/npcs/{c.character_id}" if c.character_id.startswith("npc") else f"/players/{c.character_id}"
        ref = db.reference(ref_path)
        ref.update({
            "current_hp": c.current_hp,
            "temp_hp": c.temp_hp,
            "status_effects": c.attributes.get("status_effects", [])
        })

def update_combatant_state(combat_id: str, character_id: str, combatant_obj):
    """Update a combatant's state in Firebase during combat."""
    if not db:
        return
        
    ref = db.reference(f"/combat_state/{combat_id}/combatants/{character_id}")
    ref.update({
        "HP": combatant_obj.current_hp,
        "MP": combatant_obj.current_mp,
        "temp_HP": combatant_obj.temp_hp,
        "temp_MP": combatant_obj.temp_mp,
    })
