"""
Magic System Business Logic Services

This module provides pure business logic services for the magic system,
separated from technical concerns like file I/O and configuration loading.
"""

import math
import random
from typing import Dict, List, Optional, Any, Tuple, Protocol
from dataclasses import dataclass
from enum import Enum
from uuid import UUID

# from backend.systems.character.models.abilities import CharacterAbilities
# from backend.systems.combat.models.combat_state import CombatState
# from backend.core.exceptions import InvalidSpellError, InsufficientMPError
# from backend.core.data_models import DamageType, ConfigurationType
# from backend.infrastructure.data.json_config_loader import (
#     get_config_loader,
#     validate_config_id
# )


class SaveType(Enum):
    NONE = "none"
    FORTITUDE = "fortitude"
    REFLEX = "reflex"
    WILL = "will"


@dataclass
class SpellEffect:
    """Represents the result of casting a spell"""
    damage: Optional[int] = None
    healing: Optional[int] = None
    damage_type: Optional[str] = None  # Now uses damage type ID
    save_dc: Optional[int] = None
    save_type: Optional[SaveType] = None
    duration_seconds: Optional[int] = None
    concentration_required: bool = False
    bypasses_ac: bool = False
    bypasses_dr: bool = False
    auto_hit: bool = False
    elemental_effects: Optional[Dict[str, Any]] = None


@dataclass
class ConcentrationCheck:
    """Represents a concentration save"""
    dc: int
    ability_modifier: int
    proficiency_bonus: int
    additional_bonuses: int
    has_advantage: bool = False


class MagicConfigRepository(Protocol):
    """Protocol for magic configuration data access"""
    
    def get_spells(self) -> Dict[str, Any]:
        """Get all spell configurations"""
        ...
    
    def get_spell(self, spell_name: str) -> Optional[Dict[str, Any]]:
        """Get specific spell configuration"""
        ...
    
    def get_magic_domains(self) -> Dict[str, Any]:
        """Get all magic domain configurations"""
        ...
    
    def get_domain(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Get specific domain configuration"""
        ...
    
    def get_combat_rules(self) -> Dict[str, Any]:
        """Get spell school combat rules"""
        ...
    
    def get_concentration_rules(self) -> Dict[str, Any]:
        """Get concentration rules"""
        ...


class DamageTypeService(Protocol):
    """Protocol for damage type operations"""
    
    def validate_damage_type(self, damage_type_id: str) -> bool:
        """Validate a damage type ID"""
        ...
    
    def get_environmental_damage_modifier(self, damage_type_id: str, environment: str) -> float:
        """Get environmental damage modifier"""
        ...
    
    def calculate_damage_interaction(self, attacker_type: str, defender_type: str) -> float:
        """Calculate damage interaction multiplier"""
        ...
    
    def get_damage_resistances(self, damage_type_id: str) -> Optional[List[str]]:
        """Get damage resistances for a type"""
        ...
    
    def get_damage_vulnerabilities(self, damage_type_id: str) -> Optional[List[str]]:
        """Get damage vulnerabilities for a type"""
        ...


class MagicBusinessService:
    """Pure business logic service for magic system"""
    
    def __init__(self, 
                 config_repository: MagicConfigRepository,
                 damage_type_service: DamageTypeService):
        self.config_repository = config_repository
        self.damage_type_service = damage_type_service
    
    def calculate_mp_cost(self, spell_name: str, domain: str, extra_mp: int = 0) -> int:
        """Calculate final MP cost including domain modifiers"""
        spell = self.config_repository.get_spell(spell_name)
        if not spell:
            raise ValueError(f"Unknown spell: {spell_name}")
        
        base_cost = spell["mp_cost"]
        
        # Apply domain efficiency
        domain_data = self.config_repository.get_domain(domain)
        efficiency = domain_data.get("mp_efficiency", 1.0) if domain_data else 1.0
        
        # Calculate final cost
        total_cost = math.ceil((base_cost + extra_mp) * efficiency)
        return max(1, total_cost)  # Minimum 1 MP
    
    def can_cast_spell(self, spell_name: str, domain: str, 
                      current_mp: int, extra_mp: int = 0) -> bool:
        """Check if character can cast a spell"""
        spell = self.config_repository.get_spell(spell_name)
        if not spell:
            return False
        
        # Check domain compatibility
        if domain not in spell["valid_domains"]:
            return False
        
        # Check MP requirements
        required_mp = self.calculate_mp_cost(spell_name, domain, extra_mp)
        return current_mp >= required_mp
    
    def calculate_spell_save_dc(self, spell_name: str, domain: str, 
                              abilities: Any, proficiency_bonus: int) -> int:  # Changed type to Any
        """Calculate spell save DC using appropriate ability"""
        domain_data = self.config_repository.get_domain(domain)
        primary_ability = domain_data.get("primary_ability", "intelligence") if domain_data else "intelligence"
        
        # Get ability modifier
        ability_mod = getattr(abilities, f"{primary_ability}_modifier", 0)
        
        # Get domain save bonus
        save_bonus = domain_data.get("save_bonus", 0) if domain_data else 0
        
        # Standard formula: 8 + proficiency + ability mod + domain bonus
        return 8 + proficiency_bonus + ability_mod + save_bonus
    
    def cast_spell(self, spell_name: str, domain: str, abilities: Any,  # Changed type to Any
                  proficiency_bonus: int, extra_mp: int = 0, environment: str = "normal") -> SpellEffect:
        """Cast a spell and return its effects"""
        spell = self.config_repository.get_spell(spell_name)
        if not spell:
            raise ValueError(f"Unknown spell: {spell_name}")
        
        # Calculate save DC if needed
        save_dc = None
        save_type = None
        if spell["save_type"] != "none":
            save_dc = self.calculate_spell_save_dc(spell_name, domain, abilities, proficiency_bonus)
            save_type = SaveType(spell["save_type"])
        
        # Determine combat interactions
        school = spell["school"]
        combat_rules = self.config_repository.get_combat_rules()
        bypasses_ac = school in combat_rules.get("bypasses_armor_class", [])
        bypasses_dr = school in combat_rules.get("bypasses_damage_reduction", [])
        
        # Calculate damage/healing if applicable
        damage = None
        damage_type = None
        healing = None
        elemental_effects = None
        
        if "base_damage" in spell:
            damage = self._calculate_damage(spell, extra_mp)
            damage_type = spell.get("damage_type", "force")
            
            # Validate damage type (simplified for testing)
            if damage_type and not self.damage_type_service.validate_damage_type(damage_type):
                raise ValueError(f"Invalid damage type in spell {spell_name}: {damage_type}")
            
            # Apply environmental modifiers
            if damage_type and environment != "normal":
                env_modifier = self.damage_type_service.get_environmental_damage_modifier(damage_type, environment)
                damage = int(damage * env_modifier)
        
        if "base_healing" in spell:
            healing = self._calculate_healing(spell, extra_mp)
        
        # Duration handling
        duration_seconds = self._parse_duration(spell.get("duration", "instant"))
        concentration_required = spell.get("concentration", False)
        
        return SpellEffect(
            damage=damage,
            healing=healing,
            damage_type=damage_type,
            save_dc=save_dc,
            save_type=save_type,
            duration_seconds=duration_seconds,
            concentration_required=concentration_required,
            bypasses_ac=bypasses_ac,
            bypasses_dr=bypasses_dr,
            auto_hit=spell.get("auto_hit", False),
            elemental_effects=elemental_effects
        )
    
    def apply_damage_with_resistances(self, base_damage: int, damage_type: str, 
                                    target_resistances: List[str], 
                                    target_vulnerabilities: List[str]) -> int:
        """Apply damage resistances and vulnerabilities"""
        final_damage = base_damage
        
        # Check for resistance
        if damage_type in target_resistances:
            final_damage = final_damage // 2
        
        # Check for vulnerability
        if damage_type in target_vulnerabilities:
            final_damage = final_damage * 2
        
        return max(0, final_damage)
    
    def get_damage_type_combinations(self, primary_type: str, secondary_type: str) -> Dict[str, Any]:
        """Calculate combined damage type effects"""
        # Business rule: Primary type dominates, secondary adds 25% effect
        interaction = self.damage_type_service.calculate_damage_interaction(primary_type, secondary_type)
        
        return {
            "primary_type": primary_type,
            "secondary_type": secondary_type,
            "interaction_multiplier": interaction,
            "combined_effectiveness": (interaction * 0.75) + 0.25
        }
    
    def _calculate_damage(self, spell: Dict, extra_mp: int) -> int:
        """Calculate spell damage including extra MP scaling"""
        base_damage = spell["base_damage"]
        scaling = spell.get("mp_scaling", 0)
        
        # Damage scaling: base + (extra_mp * scaling)
        total_damage = base_damage + (extra_mp * scaling)
        
        # Handle dice notation if present
        if "dice" in spell:
            dice_damage = self._roll_dice(spell["dice"])
            total_damage += dice_damage
        
        return max(0, total_damage)
    
    def _calculate_healing(self, spell: Dict, extra_mp: int) -> int:
        """Calculate spell healing including extra MP scaling"""
        base_healing = spell["base_healing"]
        scaling = spell.get("healing_scaling", 0)
        
        # Healing scaling: base + (extra_mp * scaling)
        total_healing = base_healing + (extra_mp * scaling)
        
        # Handle dice notation if present
        if "healing_dice" in spell:
            dice_healing = self._roll_dice(spell["healing_dice"])
            total_healing += dice_healing
        
        return max(0, total_healing)
    
    def _roll_dice(self, dice_string: str) -> int:
        """Roll dice from string notation (e.g., '2d6+3')"""
        # Simple dice parser for business logic
        try:
            # Handle format: XdY+Z or XdY-Z or XdY
            if '+' in dice_string:
                dice_part, bonus = dice_string.split('+')
                bonus = int(bonus.strip())
            elif '-' in dice_string and dice_string.count('-') == 1:
                dice_part, penalty = dice_string.split('-')
                bonus = -int(penalty.strip())
            else:
                dice_part = dice_string
                bonus = 0
            
            if 'd' in dice_part:
                num_dice, sides = dice_part.split('d')
                num_dice = int(num_dice.strip())
                sides = int(sides.strip())
                
                # Roll the dice
                total = sum(random.randint(1, sides) for _ in range(num_dice))
                return total + bonus
            else:
                # Just a flat number
                return int(dice_part) + bonus
                
        except (ValueError, AttributeError):
            # If parsing fails, return 0
            return 0
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to seconds"""
        if duration_str == "instant":
            return None
        
        # Parse common durations
        duration_map = {
            "1 minute": 60,
            "5 minutes": 300,
            "10 minutes": 600,
            "1 hour": 3600,
            "8 hours": 28800,
            "24 hours": 86400,
            "permanent": None
        }
        
        return duration_map.get(duration_str.lower())
    
    def check_concentration(self, damage_taken: int, abilities: Any,  # Changed type to Any
                           proficiency_bonus: int, additional_bonuses: int = 0) -> ConcentrationCheck:
        """Create a concentration check based on damage taken"""
        # Concentration DC = 10 or half damage taken, whichever is higher
        dc = max(10, damage_taken // 2)
        
        # Constitution modifier for concentration saves
        con_modifier = getattr(abilities, "constitution_modifier", 0)
        
        return ConcentrationCheck(
            dc=dc,
            ability_modifier=con_modifier,
            proficiency_bonus=proficiency_bonus,
            additional_bonuses=additional_bonuses
        )
    
    def make_concentration_save(self, check: ConcentrationCheck) -> bool:
        """Roll a concentration save"""
        # Roll d20
        roll = random.randint(1, 20)
        
        # Calculate total
        total = roll + check.ability_modifier + check.proficiency_bonus + check.additional_bonuses
        
        # Handle advantage (simplified - roll twice, take higher)
        if check.has_advantage:
            second_roll = random.randint(1, 20)
            roll = max(roll, second_roll)
            total = roll + check.ability_modifier + check.proficiency_bonus + check.additional_bonuses
        
        return total >= check.dc
    
    def get_spell_range_feet(self, spell_name: str) -> int:
        """Get spell range in feet"""
        spell = self.config_repository.get_spell(spell_name)
        if not spell:
            return 0
        return spell.get("range_feet", 30)  # Default 30 feet
    
    def get_available_spells_for_domain(self, domain: str) -> List[str]:
        """Get list of spells available for a specific domain"""
        spells = self.config_repository.get_spells()
        available = []
        
        for spell_name, spell_data in spells.items():
            if domain in spell_data.get("valid_domains", []):
                available.append(spell_name)
        
        return available


def create_magic_business_service(
    config_repository: MagicConfigRepository,
    damage_type_service: DamageTypeService
) -> MagicBusinessService:
    """Factory function to create magic business service"""
    return MagicBusinessService(config_repository, damage_type_service) 