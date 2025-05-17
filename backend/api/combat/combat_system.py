from typing import List, Dict, Optional, Tuple, Union, Any
import random
import math
import logging
from datetime import datetime
from enum import Enum

# Logger setup
logger = logging.getLogger(__name__)

class ActionType(str, Enum):
    MOVEMENT = "movement"
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"

class DamageType(str, Enum):
    SLASHING = "slashing"
    PIERCING = "piercing"
    BLUDGEONING = "bludgeoning"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    ACID = "acid"
    POISON = "poison"
    NECROTIC = "necrotic"
    RADIANT = "radiant"
    PSYCHIC = "psychic"
    FORCE = "force"
    THUNDER = "thunder"

class CombatantType(str, Enum):
    PLAYER = "player"
    NPC = "npc"
    MONSTER = "monster"

class StatusEffectType(str, Enum):
    POISONED = "poisoned"
    STUNNED = "stunned"
    PARALYZED = "paralyzed"
    CHARMED = "charmed"
    FRIGHTENED = "frightened"
    BLINDED = "blinded"
    DEAFENED = "deafened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapacitated"
    INVISIBLE = "invisible"
    PRONE = "prone"
    RESTRAINED = "restrained"
    UNCONSCIOUS = "unconscious"

class TerrainType(str, Enum):
    NORMAL = "normal"
    DIFFICULT = "difficult"
    HAZARDOUS = "hazardous"
    COVER_HALF = "half_cover"
    COVER_THREE_QUARTERS = "three_quarters_cover"
    COVER_FULL = "full_cover"

class StatusEffect:
    def __init__(
        self, 
        effect_type: StatusEffectType, 
        duration: int, 
        source_id: str, 
        intensity: int = 1,
        effects: Dict[str, Any] = None
    ):
        self.effect_type = effect_type
        self.duration = duration  # In rounds
        self.source_id = source_id
        self.intensity = intensity
        self.effects = effects or {}
        self.applied_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "effect_type": self.effect_type.value,
            "duration": self.duration,
            "source_id": self.source_id,
            "intensity": self.intensity,
            "effects": self.effects,
            "applied_at": self.applied_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatusEffect':
        return cls(
            effect_type=StatusEffectType(data["effect_type"]),
            duration=data["duration"],
            source_id=data["source_id"],
            intensity=data.get("intensity", 1),
            effects=data.get("effects", {})
        )

class Combatant:
    def __init__(
        self,
        id: str,
        name: str,
        type: CombatantType,
        initiative_bonus: int,
        hp: int,
        max_hp: int,
        armor_class: int,
        stats: Dict[str, int],
        position: Tuple[int, int] = (0, 0)
    ):
        self.id = id
        self.name = name
        self.type = type
        self.initiative_bonus = initiative_bonus
        self.hp = hp
        self.max_hp = max_hp
        self.armor_class = armor_class
        self.stats = stats
        self.position = position
        self.initiative_roll = 0
        self.status_effects: List[StatusEffect] = []
        self.action_points = {
            ActionType.MOVEMENT: 1,
            ActionType.ACTION: 1,
            ActionType.BONUS_ACTION: 1,
            ActionType.REACTION: 1
        }
    
    def roll_initiative(self) -> int:
        """Roll initiative for this combatant."""
        self.initiative_roll = random.randint(1, 20) + self.initiative_bonus
        return self.initiative_roll
    
    def get_initiative_order(self) -> Tuple[int, int]:
        """Return a tuple of (initiative roll, dexterity) for sorting."""
        return (self.initiative_roll, self.stats.get("dexterity", 0))
    
    def add_status_effect(self, effect: StatusEffect) -> bool:
        """Add a status effect to this combatant. Returns True if added, False if updated/stacked."""
        # Check if this effect type already exists
        for existing in self.status_effects:
            if existing.effect_type == effect.effect_type:
                # Check stacking rules
                if effect.intensity > existing.intensity:
                    # Replace with higher intensity
                    existing.intensity = effect.intensity
                    existing.duration = max(existing.duration, effect.duration)
                    existing.effects = effect.effects
                else:
                    # Extend duration only
                    existing.duration = max(existing.duration, effect.duration)
                return False
        
        # If not found, add new
        self.status_effects.append(effect)
        return True
    
    def remove_status_effect(self, effect_type: StatusEffectType) -> bool:
        """Remove a status effect. Returns True if removed, False if not found."""
        original_length = len(self.status_effects)
        self.status_effects = [e for e in self.status_effects if e.effect_type != effect_type]
        return len(self.status_effects) < original_length
    
    def process_turn_start(self):
        """Process the start of this combatant's turn."""
        # Decrement status effect durations and remove expired ones
        new_status_effects = []
        for effect in self.status_effects:
            effect.duration -= 1
            if effect.duration > 0:
                new_status_effects.append(effect)
        
        removed_effects = len(self.status_effects) - len(new_status_effects)
        self.status_effects = new_status_effects
        
        # Reset action points
        self.action_points = {
            ActionType.MOVEMENT: 1,
            ActionType.ACTION: 1,
            ActionType.BONUS_ACTION: 1,
            ActionType.REACTION: 1
        }
        
        return removed_effects
    
    def can_take_action(self, action_type: ActionType) -> bool:
        """Check if the combatant can take the specified action type."""
        # Check if they have action points for this type
        if self.action_points.get(action_type, 0) <= 0:
            return False
        
        # Check status effects that prevent actions
        for effect in self.status_effects:
            if effect.effect_type in [
                StatusEffectType.STUNNED,
                StatusEffectType.PARALYZED,
                StatusEffectType.UNCONSCIOUS
            ]:
                return False
            
            # Specific movement restrictions
            if action_type == ActionType.MOVEMENT and effect.effect_type in [
                StatusEffectType.GRAPPLED,
                StatusEffectType.RESTRAINED,
                StatusEffectType.PARALYZED
            ]:
                return False
        
        return True
    
    def use_action(self, action_type: ActionType) -> bool:
        """Use an action of the specified type. Returns True if successful."""
        if not self.can_take_action(action_type):
            return False
        
        self.action_points[action_type] -= 1
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "initiative_bonus": self.initiative_bonus,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "armor_class": self.armor_class,
            "stats": self.stats,
            "position": self.position,
            "initiative_roll": self.initiative_roll,
            "status_effects": [effect.to_dict() for effect in self.status_effects],
            "action_points": {k.value: v for k, v in self.action_points.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Combatant':
        combatant = cls(
            id=data["id"],
            name=data["name"],
            type=CombatantType(data["type"]),
            initiative_bonus=data["initiative_bonus"],
            hp=data["hp"],
            max_hp=data["max_hp"],
            armor_class=data["armor_class"],
            stats=data["stats"],
            position=tuple(data["position"])
        )
        combatant.initiative_roll = data["initiative_roll"]
        combatant.status_effects = [StatusEffect.from_dict(effect) for effect in data["status_effects"]]
        combatant.action_points = {ActionType(k): v for k, v in data["action_points"].items()}
        return combatant

class CombatLog:
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
    
    def add_entry(self, entry_type: str, data: Dict[str, Any]):
        """Add an entry to the combat log."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": entry_type,
            **data
        }
        self.entries.append(entry)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "entries": self.entries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CombatLog':
        log = cls()
        log.entries = data["entries"]
        return log

class CombatManager:
    def __init__(self):
        self.combatants: List[Combatant] = []
        self.initiative_order: List[str] = []
        self.current_turn_index: int = 0
        self.round_number: int = 0
        self.combat_active: bool = False
        self.battlefield: Dict[Tuple[int, int], TerrainType] = {}
        self.combat_log = CombatLog()
    
    def add_combatant(self, combatant: Combatant) -> None:
        """Add a combatant to the battle."""
        self.combatants.append(combatant)
        self.combat_log.add_entry("combatant_added", {
            "combatant_id": combatant.id,
            "combatant_name": combatant.name,
            "combatant_type": combatant.type.value
        })
    
    def remove_combatant(self, combatant_id: str) -> bool:
        """Remove a combatant from the battle. Returns True if removed."""
        original_length = len(self.combatants)
        self.combatants = [c for c in self.combatants if c.id != combatant_id]
        
        if len(self.combatants) < original_length:
            # Update initiative order
            if combatant_id in self.initiative_order:
                self.initiative_order.remove(combatant_id)
            
            # Update current turn index if needed
            if self.combat_active and self.current_turn_index >= len(self.initiative_order):
                self.current_turn_index = 0
            
            self.combat_log.add_entry("combatant_removed", {
                "combatant_id": combatant_id
            })
            return True
        
        return False
    
    def get_combatant(self, combatant_id: str) -> Optional[Combatant]:
        """Get a combatant by ID."""
        for combatant in self.combatants:
            if combatant.id == combatant_id:
                return combatant
        return None
    
    def start_combat(self) -> None:
        """Initialize combat by rolling initiative and setting up the turn order."""
        if len(self.combatants) == 0:
            raise ValueError("Cannot start combat with no combatants")
        
        # Roll initiative for all combatants
        for combatant in self.combatants:
            combatant.roll_initiative()
        
        # Sort combatants by initiative roll (descending) and dexterity (descending)
        sorted_combatants = sorted(
            self.combatants,
            key=lambda c: (c.initiative_roll, c.stats.get("dexterity", 0)),
            reverse=True
        )
        
        # Set initiative order
        self.initiative_order = [c.id for c in sorted_combatants]
        self.current_turn_index = 0
        self.round_number = 1
        self.combat_active = True
        
        # Log combat start
        self.combat_log.add_entry("combat_started", {
            "initiative_order": self.initiative_order,
            "combatants": {c.id: {"name": c.name, "initiative": c.initiative_roll} for c in self.combatants}
        })
    
    def end_combat(self) -> None:
        """End the current combat encounter."""
        self.combat_active = False
        self.combat_log.add_entry("combat_ended", {
            "round_number": self.round_number,
            "total_rounds": self.round_number
        })
    
    def get_current_combatant(self) -> Optional[Combatant]:
        """Get the combatant whose turn it currently is."""
        if not self.combat_active or len(self.initiative_order) == 0:
            return None
        
        current_id = self.initiative_order[self.current_turn_index]
        return self.get_combatant(current_id)
    
    def next_turn(self) -> Optional[Combatant]:
        """Move to the next turn in the initiative order."""
        if not self.combat_active:
            return None
        
        # Process end of current turn
        current_combatant = self.get_current_combatant()
        if current_combatant:
            self.combat_log.add_entry("turn_ended", {
                "combatant_id": current_combatant.id,
                "combatant_name": current_combatant.name,
                "round": self.round_number
            })
        
        # Increment turn index
        self.current_turn_index += 1
        
        # Check if we've completed a round
        if self.current_turn_index >= len(self.initiative_order):
            self.current_turn_index = 0
            self.round_number += 1
            self.combat_log.add_entry("round_started", {
                "round_number": self.round_number
            })
        
        # Get the new current combatant
        current_combatant = self.get_current_combatant()
        if current_combatant:
            # Process turn start
            removed_effects = current_combatant.process_turn_start()
            
            # Log turn start
            self.combat_log.add_entry("turn_started", {
                "combatant_id": current_combatant.id,
                "combatant_name": current_combatant.name,
                "round": self.round_number,
                "status_effects_removed": removed_effects
            })
        
        return current_combatant
    
    def set_terrain(self, position: Tuple[int, int], terrain_type: TerrainType) -> None:
        """Set the terrain type at a specific position."""
        self.battlefield[position] = terrain_type
    
    def get_terrain(self, position: Tuple[int, int]) -> TerrainType:
        """Get the terrain type at a specific position."""
        return self.battlefield.get(position, TerrainType.NORMAL)
    
    def calculate_damage(
        self,
        attacker: Combatant,
        target: Combatant,
        damage_roll: int,
        damage_type: DamageType,
        critical: bool = False
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Calculate the final damage after applying resistances, vulnerabilities, etc.
        Returns the final damage amount and a dictionary with calculation details.
        """
        # Start with base damage
        final_damage = damage_roll
        
        # Apply critical hit damage
        if critical:
            final_damage *= 2
        
        # TODO: Apply resistances, vulnerabilities, and immunities
        # This would be based on the target's characteristics
        
        # Apply status effects that modify damage
        for effect in attacker.status_effects:
            # Example: If attacker is under an effect that increases damage
            if "damage_bonus" in effect.effects:
                final_damage += effect.effects["damage_bonus"]
        
        for effect in target.status_effects:
            # Example: If target is under an effect that reduces damage
            if "damage_reduction" in effect.effects:
                final_damage -= effect.effects["damage_reduction"]
        
        # Ensure damage doesn't go below 0
        final_damage = max(0, final_damage)
        
        details = {
            "base_damage": damage_roll,
            "critical": critical,
            "damage_type": damage_type.value,
            "final_damage": final_damage
        }
        
        return final_damage, details
    
    def apply_damage(self, target: Combatant, damage: int, details: Dict[str, Any]) -> Dict[str, Any]:
        """Apply damage to a target and return the result."""
        original_hp = target.hp
        target.hp = max(0, target.hp - damage)
        
        result = {
            "target_id": target.id,
            "target_name": target.name,
            "damage_taken": damage,
            "original_hp": original_hp,
            "new_hp": target.hp,
            "details": details
        }
        
        # Log the damage
        self.combat_log.add_entry("damage_applied", result)
        
        return result
    
    def attack_roll(
        self,
        attacker: Combatant,
        target: Combatant,
        attack_bonus: int,
        advantage: bool = False,
        disadvantage: bool = False
    ) -> Tuple[int, bool, bool]:
        """
        Make an attack roll.
        Returns the roll total, whether it hit, and whether it was a critical hit.
        """
        # Determine if advantage/disadvantage cancel out
        has_advantage = advantage and not disadvantage
        has_disadvantage = disadvantage and not advantage
        
        # Roll with advantage/disadvantage if applicable
        if has_advantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            natural_roll = max(roll1, roll2)
            roll_detail = f"Advantage: {roll1} and {roll2}, taking {natural_roll}"
        elif has_disadvantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            natural_roll = min(roll1, roll2)
            roll_detail = f"Disadvantage: {roll1} and {roll2}, taking {natural_roll}"
        else:
            natural_roll = random.randint(1, 20)
            roll_detail = f"Normal roll: {natural_roll}"
        
        # Critical hit on natural 20
        is_critical = natural_roll == 20
        
        # Add attack bonus
        total_roll = natural_roll + attack_bonus
        
        # Check if it hits
        hits = is_critical or total_roll >= target.armor_class
        
        # Log the attack
        self.combat_log.add_entry("attack_roll", {
            "attacker_id": attacker.id,
            "attacker_name": attacker.name,
            "target_id": target.id,
            "target_name": target.name,
            "natural_roll": natural_roll,
            "attack_bonus": attack_bonus,
            "total_roll": total_roll,
            "target_ac": target.armor_class,
            "hits": hits,
            "is_critical": is_critical,
            "roll_detail": roll_detail
        })
        
        return total_roll, hits, is_critical
    
    def perform_attack(
        self,
        attacker_id: str,
        target_id: str,
        attack_bonus: int,
        damage_dice: str,
        damage_type: DamageType,
        advantage: bool = False,
        disadvantage: bool = False
    ) -> Dict[str, Any]:
        """Perform a complete attack action, including attack roll and damage."""
        attacker = self.get_combatant(attacker_id)
        target = self.get_combatant(target_id)
        
        if not attacker or not target:
            raise ValueError("Attacker or target not found")
        
        # Check if the attacker can take an action
        if not attacker.can_take_action(ActionType.ACTION):
            raise ValueError(f"{attacker.name} cannot take an action at this time")
        
        # Make an attack roll
        _, hits, is_critical = self.attack_roll(attacker, target, attack_bonus, advantage, disadvantage)
        
        result = {
            "attacker_id": attacker_id,
            "attacker_name": attacker.name,
            "target_id": target_id,
            "target_name": target.name,
            "hits": hits,
            "is_critical": is_critical
        }
        
        # If the attack hits, calculate and apply damage
        if hits:
            # Parse and roll damage dice
            damage_roll = self._roll_damage(damage_dice)
            
            # Calculate final damage after modifiers
            final_damage, damage_details = self.calculate_damage(
                attacker, target, damage_roll, damage_type, is_critical
            )
            
            # Apply the damage
            damage_result = self.apply_damage(target, final_damage, damage_details)
            result["damage"] = damage_result
        
        # Use up the attacker's action
        attacker.use_action(ActionType.ACTION)
        
        return result
    
    def _roll_damage(self, damage_dice: str) -> int:
        """
        Roll damage based on dice notation (e.g., "2d6+3").
        Returns the total damage.
        """
        # Simple dice parser
        try:
            # Handle fixed damage
            if damage_dice.isdigit():
                return int(damage_dice)
            
            # Parse dice notation with potential modifier
            if "+" in damage_dice:
                dice_part, mod_part = damage_dice.split("+")
                modifier = int(mod_part)
            else:
                dice_part = damage_dice
                modifier = 0
            
            # Parse the dice part (e.g., "2d6")
            if "d" in dice_part:
                num_dice, sides = dice_part.split("d")
                num_dice = int(num_dice)
                sides = int(sides)
                
                # Roll the dice
                rolls = [random.randint(1, sides) for _ in range(num_dice)]
                return sum(rolls) + modifier
            
            return int(dice_part) + modifier
        except Exception:  # autofix: specify exception
            # Fallback to minimum damage on parse error
            logger.error(f"Failed to parse damage dice: {damage_dice}")
            return 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the combat manager state to a dictionary."""
        return {
            "combatants": [c.to_dict() for c in self.combatants],
            "initiative_order": self.initiative_order,
            "current_turn_index": self.current_turn_index,
            "round_number": self.round_number,
            "combat_active": self.combat_active,
            "battlefield": {f"{x},{y}": terrain.value for (x, y), terrain in self.battlefield.items()},
            "combat_log": self.combat_log.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CombatManager':
        """Create a combat manager from a dictionary."""
        manager = cls()
        manager.combatants = [Combatant.from_dict(c) for c in data["combatants"]]
        manager.initiative_order = data["initiative_order"]
        manager.current_turn_index = data["current_turn_index"]
        manager.round_number = data["round_number"]
        manager.combat_active = data["combat_active"]
        
        # Parse battlefield
        manager.battlefield = {}
        for pos_str, terrain_value in data["battlefield"].items():
            x, y = map(int, pos_str.split(","))
            manager.battlefield[(x, y)] = TerrainType(terrain_value)
        
        # Parse combat log
        manager.combat_log = CombatLog.from_dict(data["combat_log"])
        
        return manager 