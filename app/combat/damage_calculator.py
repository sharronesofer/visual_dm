from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
import random
import math
import logging
import time
from app.core.rules.balance_constants import (
    CRITICAL_HIT_MULTIPLIER,
    CRITICAL_RANGE,
    BASE_AC
)
from app.combat.status_effects import StatusEffectsSystem, EffectType
from app.combat.battlefield_conditions import BattlefieldConditionsManager, Position
from app.core.models.combat import DamageComposition
from app.core.enums import DamageType

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
    composition: DamageComposition
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

@dataclass
class DamageEvent:
    attacker_id: str
    target_id: str
    base_damage: Union[int, 'DamageComposition']
    damage_type: Optional['DamageType'] = None
    bonus_damage: Optional[Dict['DamageType', int]] = None
    is_critical: bool = False
    context: Optional[dict] = None
    # Pipeline state
    modified_damage: Optional[Union[int, 'DamageComposition']] = None
    stage: str = "PreCalculation"
    log: List[Dict[str, Any]] = field(default_factory=list)
    delayed: bool = False
    delay_duration: Optional[float] = None  # For DoT
    result: Optional[Any] = None

    def add_log(self, stage, info):
        self.log.append({
            'timestamp': time.time(),
            'stage': stage,
            'info': info
        })

class DamageModificationPipeline:
    """
    Event-driven pipeline for damage calculation with multiple modification points and hooks.
    Stages: PreCalculation, TypeModification, ResistanceApplication, CriticalCalculation, PostCalculation, FinalDamage
    Supports registration of modifiers with priorities, detailed logging, and delayed/DoT effects.
    """
    STAGES = [
        "PreCalculation",
        "TypeModification",
        "ResistanceApplication",
        "CriticalCalculation",
        "PostCalculation",
        "FinalDamage"
    ]

    def __init__(self):
        self.hooks: Dict[str, List[Tuple[int, Callable[[DamageEvent], None]]]] = {stage: [] for stage in self.STAGES}
        self.logger = logging.getLogger("DamageModificationPipeline")

    def register_modifier(self, stage: str, fn: Callable[[DamageEvent], None], priority: int = 10):
        """Register a modifier for a stage. Lower priority runs first."""
        if stage not in self.hooks:
            raise ValueError(f"Invalid stage: {stage}")
        self.hooks[stage].append((priority, fn))
        self.hooks[stage].sort(key=lambda x: x[0])

    def run(self, event: DamageEvent) -> DamageEvent:
        for stage in self.STAGES:
            event.stage = stage
            for _, fn in self.hooks[stage]:
                fn(event)
                event.add_log(stage, f"Modifier {fn.__name__} applied")
            self.logger.debug(f"Stage {stage} complete: {event.modified_damage}")
        return event

    def log_event(self, event: DamageEvent):
        for entry in event.log:
            self.logger.info(f"[{entry['stage']}] {entry['info']}")

class CriticalHitCalculator:
    """
    Handles critical hit chance, multiplier, special effects, and immunity/protection.
    Supports registration of special effects and querying crit info for UI/logging.
    """
    def __init__(self):
        self.effect_registry = []  # List of callables: (attacker_id, target_id, context) -> effect dict

    def get_critical_chance(self, attacker, target, context=None) -> float:
        # Base crit chance from attacker stats, weapon, skills, effects, etc.
        base = getattr(attacker, 'critical_chance', 0.05)
        # Add weapon/skill/context bonuses here as needed
        if context and 'crit_bonus' in context:
            base += context['crit_bonus']
        # Clamp to [0.01, 0.5]
        return min(0.5, max(0.01, base))

    def get_critical_multiplier(self, attacker, target, context=None) -> float:
        # Base multiplier from attacker, weapon, skills, effects, etc.
        base = getattr(attacker, 'critical_damage', 1.5)
        if context and 'crit_multiplier_bonus' in context:
            base += context['crit_multiplier_bonus']
        return max(1.0, base)

    def is_immune_to_critical(self, target, context=None) -> bool:
        # Check for crit immunity from status effects, equipment, etc.
        if hasattr(target, 'status_effects'):
            for effect in getattr(target, 'status_effects', []):
                if effect.get('type') == 'crit_immunity':
                    return True
        if context and context.get('ignore_crit_immunity'):
            return False
        return False

    def register_critical_effect(self, effect_fn):
        """Register a callable to trigger on crits: (attacker_id, target_id, context) -> effect dict"""
        self.effect_registry.append(effect_fn)

    def trigger_critical_effects(self, attacker_id, target_id, context=None):
        results = []
        for fn in self.effect_registry:
            result = fn(attacker_id, target_id, context)
            if result:
                results.append(result)
        return results

    def get_critical_info(self, attacker, target, context=None) -> dict:
        """Return crit chance, multiplier, immunity, and registered effects for UI/logging."""
        return {
            'chance': self.get_critical_chance(attacker, target, context),
            'multiplier': self.get_critical_multiplier(attacker, target, context),
            'immune': self.is_immune_to_critical(target, context),
            'effects': [fn.__name__ for fn in self.effect_registry],
        }

class DamageCalculator:
    """
    Handles all combat calculations including attack resolution,
    damage application, critical hits, and defensive reactions.
    """
    def __init__(
        self,
        status_system: StatusEffectsSystem,
        battlefield: BattlefieldConditionsManager,
        combat_stats_lookup: Optional[callable] = None,
        crit_calculator: Optional[CriticalHitCalculator] = None,
        pipeline: Optional[DamageModificationPipeline] = None,
        effectiveness_matrix: Optional['DamageEffectivenessMatrix'] = None
    ):
        self.status_system = status_system
        self.battlefield = battlefield
        self.combat_stats_lookup = combat_stats_lookup  # Function: target_id -> CombatStats or None
        self.crit_calculator = crit_calculator or CriticalHitCalculator()
        self.pipeline = pipeline or DamageModificationPipeline()
        self.effectiveness_matrix = effectiveness_matrix
        # Register default pipeline modifiers if not already present
        def _default_type_modification(event: DamageEvent):
            if isinstance(event.modified_damage, int):
                from app.core.models.combat import DamageComposition, DamageType
                dt = event.damage_type if event.damage_type else DamageType.PHYSICAL
                comp = DamageComposition()
                comp.add(dt, event.modified_damage)
                if event.bonus_damage:
                    for dt, amt in event.bonus_damage.items():
                        comp.add(dt, amt)
                event.modified_damage = comp
            # Apply effectiveness matrix if present and defender_type is available
            matrix = getattr(self, 'effectiveness_matrix', None)
            defender_type = None
            if event.context:
                target = event.context.get('target')
                if target and hasattr(target, 'damage_type'):
                    defender_type = target.damage_type
            if matrix and defender_type:
                event.modified_damage = matrix.apply_to_composition(event.modified_damage, defender_type)
            # If no defender_type, skip matrix application
        def _default_resistance_application(event: DamageEvent):
            from app.core.models.combat import DamageComposition
            comp = event.modified_damage
            if not isinstance(comp, DamageComposition):
                return
            resistances = {}
            vulnerabilities = {}
            # Use combat_stats_lookup if present, else status_system
            target_id = event.target_id
            context = event.context or {}
            lookup = context.get('combat_stats_lookup')
            if lookup:
                target_stats = lookup(target_id)
                resistances = getattr(target_stats, 'resistances', {}) or {}
                vulnerabilities = getattr(target_stats, 'vulnerabilities', {}) or {}
            else:
                status_system = context.get('status_system')
                if status_system:
                    resistances = status_system.get_resistances(target_id) or {}
            for dt in list(comp.amounts.keys()):
                key = getattr(dt, 'value', None) or getattr(dt, 'name', None) or str(dt)
                res = float(resistances.get(key, 0.0))
                vul = float(vulnerabilities.get(key, 0.0))
                res = max(0.0, min(1.0, res))
                # Do not clamp vulnerability, allow > 1.0
                amt = comp.amounts[dt]
                amt = amt * (1.0 - res + vul)
                amt = max(0.0, amt)
                comp.amounts[dt] = amt
        def _default_critical_calculation(event: DamageEvent):
            crit_calc = event.context.get('crit_calculator') if event.context else None
            attacker = event.context.get('attacker') if event.context else None
            target = event.context.get('target') if event.context else None
            if not crit_calc or not attacker or not target:
                event.context['multiplier'] = 1.0
                return
            if crit_calc.is_immune_to_critical(target, event.context):
                event.context['multiplier'] = 1.0
            elif event.is_critical:
                event.context['multiplier'] = crit_calc.get_critical_multiplier(attacker, target, event.context)
            else:
                event.context['multiplier'] = 1.0
        # Only register if not already present
        if not self.pipeline.hooks['TypeModification']:
            self.pipeline.register_modifier('TypeModification', _default_type_modification, priority=10)
        if not self.pipeline.hooks['ResistanceApplication']:
            self.pipeline.register_modifier('ResistanceApplication', _default_resistance_application, priority=10)
        if not self.pipeline.hooks['CriticalCalculation']:
            self.pipeline.register_modifier('CriticalCalculation', _default_critical_calculation, priority=10)
        
    def calculate_attack_roll(
        self,
        attacker_id: str,
        target_id: str,
        attack_type: AttackType,
        attack_bonus: int,
        advantage: bool = False,
        disadvantage: bool = False,
        context: Optional[dict] = None
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
        attacker = self.combat_stats_lookup(attacker_id) if self.combat_stats_lookup else None
        target = self.combat_stats_lookup(target_id) if self.combat_stats_lookup else None
        crit_chance = self.crit_calculator.get_critical_chance(attacker, target, context)
        is_critical = (natural_roll >= CRITICAL_RANGE) or (random.random() < crit_chance)
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
        damage: Union[DamageComposition, int],
        damage_type: DamageType = None,
        bonus_damage: Dict[DamageType, int] = None,
        is_critical: bool = False,
        context: Optional[dict] = None
    ) -> DamageRoll:
        """
        Calculate damage for a successful attack. Supports multi-type damage.
        Applies resistances and vulnerabilities from CombatStats if available, otherwise uses status effects system.
        """
        # Always build a full context for the pipeline
        attacker = self.combat_stats_lookup(attacker_id) if self.combat_stats_lookup else None
        target = self.combat_stats_lookup(target_id) if self.combat_stats_lookup else None
        ctx = dict(context or {})
        ctx.update({'attacker': attacker, 'target': target, 'status_system': self.status_system, 'crit_calculator': self.crit_calculator, 'combat_stats_lookup': self.combat_stats_lookup})
        event = DamageEvent(
            attacker_id=attacker_id,
            target_id=target_id,
            base_damage=damage,
            damage_type=damage_type,
            bonus_damage=bonus_damage,
            is_critical=is_critical,
            context=ctx
        )
        event.modified_damage = damage
        event = self.pipeline.run(event)

        # After calculating damage, trigger special crit effects if any
        effects = []
        if event.modified_damage and is_critical:
            effects.extend(self.crit_calculator.trigger_critical_effects(attacker_id, target_id, context))
        # For legacy compatibility, extract total_damage
        total_damage = 0
        comp = event.modified_damage
        if hasattr(comp, 'items'):
            total_damage = sum(comp.amounts.values())
        elif isinstance(comp, int):
            total_damage = comp
        multiplier = event.context.get('multiplier', 1.0)
        return DamageRoll(
            composition=event.modified_damage,
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
                effects_triggered=[]
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
            # Compose multi-type damage
            comp = DamageComposition()
            comp.add(damage_type, base_damage)
            if bonus_damage:
                for dt, amt in bonus_damage.items():
                    comp.add(dt, amt)
            damage_roll = self.calculate_damage(
                attacker_id,
                target_id,
                comp,
                is_critical=attack_roll.is_critical
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

    @staticmethod
    def compare_compositions(comp1: DamageComposition, comp2: DamageComposition) -> bool:
        """Return True if two DamageCompositions are equal in type and amount."""
        return comp1.amounts == comp2.amounts

    @staticmethod
    def combine_compositions(*comps: DamageComposition) -> DamageComposition:
        """Combine multiple DamageCompositions into one."""
        result = DamageComposition()
        for comp in comps:
            for dt, amt in comp.items():
                result.add(dt, amt)
        return result

    @staticmethod
    def serialize_damage_roll(damage_roll: DamageRoll) -> Dict[str, Any]:
        """Serialize a DamageRoll for logging or UI."""
        return {
            'composition': damage_roll.composition.serialize(),
            'multiplier': damage_roll.multiplier,
            'total_damage': damage_roll.total_damage
        } 
        return {
            'composition': damage_roll.composition.serialize(),
            'multiplier': damage_roll.multiplier,
            'total_damage': damage_roll.total_damage
        } 