from typing import Dict, List, Optional, Tuple, Union
from enum import Enum
from dataclasses import dataclass
import random
import math
from app.core.rules.balance_constants import (
    CRITICAL_HIT_MULTIPLIER,
    CRITICAL_RANGE,
    BASE_AC
)
from app.combat.status_effects import StatusEffectsSystem, EffectType
from app.combat.battlefield_conditions import BattlefieldConditionsManager, Position

class DamageType(Enum):
    """Types of damage that can be dealt."""
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
    FORCE = "force"
    PSYCHIC = "psychic"
    
class AttackType(Enum):
    """Types of attacks that can be made."""
    MELEE = "melee"
    RANGED = "ranged"
    SPELL = "spell"
    
class DefensiveAction(Enum):
    """Types of defensive actions that can be taken."""
    NONE = "none"
    DODGE = "dodge"
    BLOCK = "block"
    PARRY = "parry"
    DEFLECT = "deflect"

@dataclass
class AttackRoll:
    """Represents the result of an attack roll."""
    natural_roll: int
    total_roll: int
    modifiers: Dict[str, int]
    is_critical: bool
    is_fumble: bool

@dataclass
class DamageRoll:
    """Represents the result of a damage roll."""
    base_damage: int
    bonus_damage: Dict[DamageType, int]
    multiplier: float
    total_damage: int

@dataclass
class AttackResult:
    """Represents the complete result of an attack."""
    attack_roll: AttackRoll
    damage_roll: Optional[DamageRoll]
    hit: bool
    target_ac: int
    defensive_action: DefensiveAction
    effects_triggered: List[Dict]

class DamageCalculator:
    """
    Handles all combat calculations including attack resolution,
    damage application, critical hits, and defensive reactions.
    """
    def __init__(
        self,
        status_system: StatusEffectsSystem,
        battlefield: BattlefieldConditionsManager
    ):
        self.status_system = status_system
        self.battlefield = battlefield
        
    def calculate_attack_roll(
        self,
        attacker_id: str,
        target_id: str,
        attack_type: AttackType,
        attack_bonus: int,
        advantage: bool = False,
        disadvantage: bool = False
    ) -> AttackRoll:
        """Calculate the result of an attack roll."""
        # Determine if advantage/disadvantage cancel out
        has_advantage = advantage and not disadvantage
        has_disadvantage = disadvantage and not advantage
        
        # Roll dice
        if has_advantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            natural_roll = max(roll1, roll2)
        elif has_disadvantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            natural_roll = min(roll1, roll2)
        else:
            natural_roll = random.randint(1, 20)
            
        # Calculate modifiers
        modifiers = {"base": attack_bonus}
        
        # Apply status effects
        if attack_type == AttackType.RANGED:
            # Check for effects that impact ranged attacks
            for effect in self.status_system.get_active_effects(attacker_id):
                if effect.effect.type == EffectType.DEBUFF:
                    modifiers["status_penalty"] = -2
                    
        # Calculate total
        total_roll = natural_roll + sum(modifiers.values())
        
        # Check for critical hit/fumble
        is_critical = natural_roll >= CRITICAL_RANGE
        is_fumble = natural_roll == 1
        
        return AttackRoll(
            natural_roll=natural_roll,
            total_roll=total_roll,
            modifiers=modifiers,
            is_critical=is_critical,
            is_fumble=is_fumble
        )
        
    def calculate_damage(
        self,
        attacker_id: str,
        target_id: str,
        base_damage: int,
        damage_type: DamageType,
        bonus_damage: Dict[DamageType, int] = None,
        is_critical: bool = False
    ) -> DamageRoll:
        """Calculate damage for a successful attack."""
        if bonus_damage is None:
            bonus_damage = {}
            
        # Start with base multiplier
        multiplier = CRITICAL_HIT_MULTIPLIER if is_critical else 1.0
        
        # Get target's resistances and immunities
        resistances = self.status_system.get_resistances(target_id)
        immunities = self.status_system.get_immunities(target_id)
        
        # Calculate damage for each type
        total_damage = 0
        final_bonus_damage = {}
        
        # Calculate base damage
        if damage_type.value not in immunities:
            damage_mult = multiplier * (1 - resistances.get(damage_type.value, 0))
            base_damage_final = math.floor(base_damage * damage_mult)
            total_damage += base_damage_final
            
        # Calculate bonus damage
        for bonus_type, bonus_amount in bonus_damage.items():
            if bonus_type.value not in immunities:
                damage_mult = multiplier * (1 - resistances.get(bonus_type.value, 0))
                bonus_final = math.floor(bonus_amount * damage_mult)
                final_bonus_damage[bonus_type] = bonus_final
                total_damage += bonus_final
                
        return DamageRoll(
            base_damage=base_damage,
            bonus_damage=final_bonus_damage,
            multiplier=multiplier,
            total_damage=total_damage
        )
        
    def resolve_attack(
        self,
        attacker_id: str,
        target_id: str,
        attacker_pos: Position,
        target_pos: Position,
        attack_type: AttackType,
        attack_bonus: int,
        base_damage: int,
        damage_type: DamageType,
        bonus_damage: Dict[DamageType, int] = None,
        advantage: bool = False,
        disadvantage: bool = False
    ) -> AttackResult:
        """Resolve a complete attack including defensive actions."""
        effects_triggered = []
        
        # Check battlefield conditions
        if not self.battlefield.check_line_of_sight(attacker_pos, target_pos):
            return AttackResult(
                attack_roll=None,
                damage_roll=None,
                hit=False,
                target_ac=0,
                defensive_action=DefensiveAction.NONE,
                effects_triggered=[{"type": "no_line_of_sight"}]
            )
            
        # Get target's base AC
        target_ac = BASE_AC  # This should come from target's stats
        
        # Add cover bonus
        cover_bonus = self.battlefield.get_cover_bonus(attacker_pos, target_pos)
        if cover_bonus:
            target_ac += cover_bonus
            
        # Check for defensive actions
        defensive_action = DefensiveAction.NONE
        # This should be determined by target's available reactions and AI
        
        if defensive_action == DefensiveAction.DODGE:
            disadvantage = True
            effects_triggered.append({"type": "dodge_used"})
            
        # Make attack roll
        attack_roll = self.calculate_attack_roll(
            attacker_id,
            target_id,
            attack_type,
            attack_bonus,
            advantage,
            disadvantage
        )
        
        # Handle fumble
        if attack_roll.is_fumble:
            effects_triggered.append({"type": "fumble"})
            return AttackResult(
                attack_roll=attack_roll,
                damage_roll=None,
                hit=False,
                target_ac=target_ac,
                defensive_action=defensive_action,
                effects_triggered=effects_triggered
            )
            
        # Check if hit
        hit = attack_roll.total_roll >= target_ac
        
        # Calculate damage if hit
        damage_roll = None
        if hit:
            damage_roll = self.calculate_damage(
                attacker_id,
                target_id,
                base_damage,
                damage_type,
                bonus_damage,
                attack_roll.is_critical
            )
            
            if attack_roll.is_critical:
                effects_triggered.append({"type": "critical_hit"})
                
            if damage_roll.total_damage == 0:
                effects_triggered.append({"type": "no_damage"})
                
        return AttackResult(
            attack_roll=attack_roll,
            damage_roll=damage_roll,
            hit=hit,
            target_ac=target_ac,
            defensive_action=defensive_action,
            effects_triggered=effects_triggered
        )
        
    def calculate_healing(
        self,
        target_id: str,
        base_healing: int,
        bonus_healing: int = 0,
        multiplier: float = 1.0
    ) -> int:
        """Calculate healing amount after modifiers."""
        # Get target's healing modifiers from status effects
        healing_mod = 0
        for effect in self.status_system.get_active_effects(target_id):
            if effect.effect.type == EffectType.BUFF:
                for modifier in effect.effect.modifiers:
                    if modifier.attribute == "healing_received":
                        healing_mod += modifier.value
                        
        total_healing = (base_healing + bonus_healing) * (1 + healing_mod)
        return math.floor(total_healing * multiplier)
        
    def calculate_saving_throw(
        self,
        target_id: str,
        save_type: str,
        dc: int,
        save_bonus: int,
        advantage: bool = False,
        disadvantage: bool = False
    ) -> Tuple[bool, int]:
        """
        Calculate the result of a saving throw.
        Returns (success, natural_roll).
        """
        # Determine if advantage/disadvantage cancel out
        has_advantage = advantage and not disadvantage
        has_disadvantage = disadvantage and not advantage
        
        # Roll dice
        if has_advantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            natural_roll = max(roll1, roll2)
        elif has_disadvantage:
            roll1 = random.randint(1, 20)
            roll2 = random.randint(1, 20)
            natural_roll = min(roll1, roll2)
        else:
            natural_roll = random.randint(1, 20)
            
        # Calculate total
        total = natural_roll + save_bonus
        
        # Check for automatic success/failure
        if natural_roll == 20:
            return True, natural_roll
        if natural_roll == 1:
            return False, natural_roll
            
        return total >= dc, natural_roll 