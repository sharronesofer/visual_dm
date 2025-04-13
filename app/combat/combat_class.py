import random
from app.combat.status_effects_utils import apply_status

class Combatant:
    def __init__(self, character_id, full_stats):
        ...
        self.action_slots = {
            "action": False,
            "bonus": False,
            "movement": False,
            "free": 0,
            "trigger": {"action": False, "bonus": False, "free": False}
        }

    def reset_action_slots(self):
        self.action_slots = {
            "action": False,
            "bonus": False,
            "movement": False,
            "free": 0,
            "trigger": {"action": False, "bonus": False, "free": False}
        }

    def consume_slot(self, slot_type):
        if slot_type == "action":
            if self.action_slots["action"]: return False
            self.action_slots["action"] = True
        elif slot_type == "bonus":
            if self.action_slots["bonus"]: return False
            self.action_slots["bonus"] = True
        elif slot_type == "movement":
            if self.action_slots["movement"]: return False
            self.action_slots["movement"] = True
        elif slot_type == "free":
            if self.action_slots["free"] >= 2: return False
            self.action_slots["free"] += 1
        elif slot_type.startswith("trigger"):
            _, subtype = slot_type.split("_")
            if self.action_slots["trigger"].get(subtype): return False
            self.action_slots["trigger"][subtype] = True
        else:
            return False
        return True

def resolve(self):
    # Check and consume action economy slot (default: "action")
    action_type = self.action.get("action_type", "action")
    if not self.attacker.consume_slot(action_type):
        return {
            "result": "slot_used",
            "slot": action_type,
            "character_id": self.attacker.character_id
        }

    # Check MP cost
    mp_cost = self.action.get("mp_cost", 0)
    if mp_cost > 0:
        if not self.attacker.use_mp(mp_cost):
            return {
                "result": "insufficient_mp",
                "action": self.action.get("name"),
                "character_id": self.attacker.character_id
            }

    # Damage resolution
    base_damage = self.action.get("base_damage", 10)
    damage_dealt = self.target.apply_damage(base_damage)

    # Status effect
    status = self.action.get("status_condition")
    if status:
        duration = self.action.get("effect_duration", 3)
        apply_status(self.target, status, duration, source=self.attacker.character_id)

    # Result payload
    return {
        "attacker": self.attacker.character_id,
        "target": self.target.character_id,
        "action": self.action.get("name", "basic_attack"),
        "action_type": action_type,
        "damage": damage_dealt,
        "mp_used": mp_cost,
        "status_applied": status,
        "target_remaining_hp": self.target.stats.get("HP", "?")
    }
from app.combat.status_effects_utils import apply_status

class CombatAction:
    def __init__(self, attacker, target, action_data, battlefield=None):
        self.attacker = attacker
        self.target = target
        self.action = action_data
        self.battlefield = battlefield

    def resolve(self):
        action_type = self.action.get("action_type", "action")
        if not self.attacker.consume_slot(action_type):
            return {
                "result": "slot_used",
                "slot": action_type,
                "character_id": self.attacker.character_id
            }

        mp_cost = self.action.get("mp_cost", 0)
        if mp_cost > 0 and not self.attacker.use_mp(mp_cost):
            return {
                "result": "insufficient_mp",
                "action": self.action.get("name"),
                "character_id": self.attacker.character_id
            }

        base_damage = self.action.get("base_damage", 10)
        damage_dealt = self.target.apply_damage(base_damage)

        status = self.action.get("status_condition")
        if status:
            duration = self.action.get("effect_duration", 3)
            apply_status(self.target, status, duration, source=self.attacker.character_id)

        return {
            "attacker": self.attacker.character_id,
            "target": self.target.character_id,
            "action": self.action.get("name", "basic_attack"),
            "action_type": action_type,
            "damage": damage_dealt,
            "mp_used": mp_cost,
            "status_applied": status,
            "target_remaining_hp": self.target.stats.get("HP", "?")
        }