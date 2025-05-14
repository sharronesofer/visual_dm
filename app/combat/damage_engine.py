from typing import Dict, Optional, List, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from app.core.models.combat import CombatStats
from app.core.models.character import Character
from app.core.models.npc import NPC

class DamageType(Enum):
    PHYSICAL = "physical"
    MAGICAL = "magical"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    POISON = "poison"
    PSYCHIC = "psychic"
    FORCE = "force"
    RADIANT = "radiant"
    NECROTIC = "necrotic"

class AttackType(Enum):
    MELEE = "melee"
    RANGED = "ranged"
    SPELL = "spell"
    OPPORTUNITY = "opportunity"

@dataclass
class DamageResult:
    raw_damage: int
    final_damage: int
    damage_type: DamageType
    critical: bool
    absorbed_damage: int
    damage_reduction: int
    effects_applied: List[str]
    hit_location: Optional[str] = None

class DamageCalculationEngine:
    """
    Comprehensive engine for calculating and applying combat damage.
    Handles all aspects of damage calculation including:
    - Base damage calculation
    - Critical hits
    - Damage type modifiers
    - Status effects
    - Resistances and vulnerabilities
    - Armor and damage reduction
    - Battlefield conditions
    """
    
    def __init__(self):
        self._damage_cache = {}
        self._last_calculation_time = datetime.now()
        
    def calculate_damage(
        self,
        attacker: Union[Character, NPC],
        defender: Union[Character, NPC],
        attack_type: AttackType,
        weapon: Optional[Dict] = None,
        spell: Optional[Dict] = None,
        battlefield_conditions: Optional[Dict] = None,
        status_effects: Optional[List[Dict]] = None,
        is_critical: bool = False,
        advantage: bool = False,
        disadvantage: bool = False
    ) -> DamageResult:
        """
        Calculate damage for an attack with all relevant modifiers.
        
        Args:
            attacker: The attacking character/NPC
            defender: The defending character/NPC
            attack_type: Type of attack (melee, ranged, spell)
            weapon: Optional weapon data for weapon attacks
            spell: Optional spell data for spell attacks
            battlefield_conditions: Optional battlefield condition modifiers
            status_effects: Optional list of active status effects
            is_critical: Whether this is a critical hit
            advantage: Whether attacker has advantage
            disadvantage: Whether attacker has disadvantage
            
        Returns:
            DamageResult containing detailed damage calculation results
        """
        # Calculate base damage
        base_damage = self._calculate_base_damage(
            attacker, attack_type, weapon, spell
        )
        
        # Apply critical hit multiplier if applicable
        if is_critical:
            base_damage *= 2
            
        # Calculate ability score modifiers
        ability_modifier = self._calculate_ability_modifier(
            attacker, attack_type
        )
        
        # Apply weapon/spell specific modifiers
        item_modifier = self._calculate_item_modifier(weapon, spell)
        
        # Calculate raw damage before reductions
        raw_damage = base_damage + ability_modifier + item_modifier
        
        # Determine damage type
        damage_type = self._determine_damage_type(
            attack_type, weapon, spell
        )
        
        # Apply battlefield condition modifiers
        if battlefield_conditions:
            raw_damage = self._apply_battlefield_modifiers(
                raw_damage,
                battlefield_conditions,
                damage_type
            )
            
        # Apply status effect modifiers
        if status_effects:
            raw_damage = self._apply_status_modifiers(
                raw_damage,
                status_effects,
                damage_type
            )
            
        # Calculate defender's damage reduction
        damage_reduction = self._calculate_damage_reduction(
            defender,
            damage_type,
            attack_type
        )
        
        # Calculate damage absorption from temporary HP or shields
        absorbed_damage = self._calculate_absorption(
            defender,
            raw_damage,
            damage_type
        )
        
        # Calculate final damage after all reductions
        final_damage = max(0, raw_damage - damage_reduction - absorbed_damage)
        
        # Track any effects that should be applied
        effects_applied = self._determine_additional_effects(
            attacker,
            defender,
            attack_type,
            weapon,
            spell,
            is_critical
        )
        
        # Determine hit location for detailed combat
        hit_location = self._determine_hit_location(
            attack_type,
            advantage,
            disadvantage
        )
        
        # Cache the calculation for performance
        self._cache_calculation(
            attacker,
            defender,
            attack_type,
            final_damage,
            damage_type
        )
        
        return DamageResult(
            raw_damage=raw_damage,
            final_damage=final_damage,
            damage_type=damage_type,
            critical=is_critical,
            absorbed_damage=absorbed_damage,
            damage_reduction=damage_reduction,
            effects_applied=effects_applied,
            hit_location=hit_location
        )
    
    def _calculate_base_damage(
        self,
        attacker: Union[Character, NPC],
        attack_type: AttackType,
        weapon: Optional[Dict],
        spell: Optional[Dict]
    ) -> int:
        """Calculate the base damage before any modifiers."""
        if attack_type == AttackType.SPELL and spell:
            return spell.get('base_damage', 0)
        elif weapon:
            return weapon.get('damage', 0)
        else:
            # Unarmed strike or basic attack
            return max(1, (attacker.strength - 10) // 2)
    
    def _calculate_ability_modifier(
        self,
        attacker: Union[Character, NPC],
        attack_type: AttackType
    ) -> int:
        """Calculate the ability score modifier for the attack."""
        if attack_type == AttackType.MELEE:
            return (attacker.strength - 10) // 2
        elif attack_type == AttackType.RANGED:
            return (attacker.dexterity - 10) // 2
        elif attack_type == AttackType.SPELL:
            return (attacker.intelligence - 10) // 2
        else:  # Opportunity attacks use strength by default
            return (attacker.strength - 10) // 2
    
    def _calculate_item_modifier(
        self,
        weapon: Optional[Dict],
        spell: Optional[Dict]
    ) -> int:
        """Calculate modifiers from weapons or spells."""
        modifier = 0
        if weapon:
            modifier += weapon.get('bonus', 0)
            modifier += weapon.get('enhancement', 0)
        if spell:
            modifier += spell.get('power_modifier', 0)
        return modifier
    
    def _determine_damage_type(
        self,
        attack_type: AttackType,
        weapon: Optional[Dict],
        spell: Optional[Dict]
    ) -> DamageType:
        """Determine the type of damage being dealt."""
        if spell:
            return DamageType(spell.get('damage_type', 'magical'))
        elif weapon:
            return DamageType(weapon.get('damage_type', 'physical'))
        return DamageType.PHYSICAL
    
    def _apply_battlefield_modifiers(
        self,
        damage: int,
        conditions: Dict,
        damage_type: DamageType
    ) -> int:
        """Apply modifiers from battlefield conditions."""
        multiplier = 1.0
        
        # Apply terrain advantages
        if conditions.get('high_ground'):
            multiplier *= 1.1
        if conditions.get('difficult_terrain'):
            multiplier *= 0.9
            
        # Apply environmental effects
        if damage_type == DamageType.FIRE and conditions.get('rain'):
            multiplier *= 0.8
        elif damage_type == DamageType.LIGHTNING and conditions.get('water'):
            multiplier *= 1.2
            
        return int(damage * multiplier)
    
    def _apply_status_modifiers(
        self,
        damage: int,
        status_effects: List[Dict],
        damage_type: DamageType
    ) -> int:
        """Apply modifiers from status effects."""
        multiplier = 1.0
        
        for effect in status_effects:
            if effect.get('type') == 'strengthened':
                multiplier *= 1.2
            elif effect.get('type') == 'weakened':
                multiplier *= 0.8
                
        return int(damage * multiplier)
    
    def _calculate_damage_reduction(
        self,
        defender: Union[Character, NPC],
        damage_type: DamageType,
        attack_type: AttackType
    ) -> int:
        """Calculate damage reduction from armor and resistances."""
        reduction = 0
        
        # Base armor reduction
        if hasattr(defender, 'armor_class'):
            reduction += defender.armor_class // 2
            
        # Damage type resistances
        if hasattr(defender, 'resistances'):
            if damage_type.value in defender.resistances:
                reduction += 5
                
        # Attack type specific reductions
        if attack_type == AttackType.RANGED and hasattr(defender, 'deflection'):
            reduction += defender.deflection
            
        return reduction
    
    def _calculate_absorption(
        self,
        defender: Union[Character, NPC],
        damage: int,
        damage_type: DamageType
    ) -> int:
        """Calculate damage absorption from temporary HP or shields."""
        absorption = 0
        
        # Temporary HP absorption
        if hasattr(defender, 'temp_health'):
            absorption += min(defender.temp_health, damage)
            
        # Magical shields
        if hasattr(defender, 'magical_shields'):
            for shield in defender.magical_shields:
                if damage_type.value in shield.get('protected_types', []):
                    absorption += min(
                        shield.get('remaining_absorption', 0),
                        damage - absorption
                    )
                    
        return absorption
    
    def _determine_additional_effects(
        self,
        attacker: Union[Character, NPC],
        defender: Union[Character, NPC],
        attack_type: AttackType,
        weapon: Optional[Dict],
        spell: Optional[Dict],
        is_critical: bool
    ) -> List[str]:
        """Determine any additional effects that should be applied."""
        effects = []
        
        # Weapon effects
        if weapon:
            if weapon.get('bleeding') and is_critical:
                effects.append('bleeding')
            if weapon.get('stunning') and is_critical:
                effects.append('stunned')
                
        # Spell effects
        if spell:
            effects.extend(spell.get('additional_effects', []))
            
        # Critical hit effects
        if is_critical:
            effects.append('critical_hit')
            
        return effects
    
    def _determine_hit_location(
        self,
        attack_type: AttackType,
        advantage: bool,
        disadvantage: bool
    ) -> Optional[str]:
        """Determine which body part was hit for detailed combat."""
        if attack_type == AttackType.SPELL:
            return None  # Spells don't typically target specific locations
            
        locations = [
            'head',
            'torso',
            'left_arm',
            'right_arm',
            'left_leg',
            'right_leg'
        ]
        
        import random
        if advantage:
            # Roll twice and take the "better" location
            roll1 = random.randint(0, len(locations) - 1)
            roll2 = random.randint(0, len(locations) - 1)
            return locations[min(roll1, roll2)]  # Lower index = more vital area
        elif disadvantage:
            # Roll twice and take the "worse" location
            roll1 = random.randint(0, len(locations) - 1)
            roll2 = random.randint(0, len(locations) - 1)
            return locations[max(roll1, roll2)]  # Higher index = less vital area
        else:
            return locations[random.randint(0, len(locations) - 1)]
    
    def _cache_calculation(
        self,
        attacker: Union[Character, NPC],
        defender: Union[Character, NPC],
        attack_type: AttackType,
        damage: int,
        damage_type: DamageType
    ):
        """Cache the damage calculation for performance."""
        cache_key = (
            attacker.id,
            defender.id,
            attack_type.value,
            damage_type.value
        )
        
        self._damage_cache[cache_key] = {
            'damage': damage,
            'timestamp': datetime.now()
        }
        
        # Clear old cache entries (older than 5 minutes)
        current_time = datetime.now()
        old_keys = [
            k for k, v in self._damage_cache.items()
            if (current_time - v['timestamp']).total_seconds() > 300
        ]
        for k in old_keys:
            del self._damage_cache[k] 