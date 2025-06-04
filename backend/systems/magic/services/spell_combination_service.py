"""
Spell Combination Service - Advanced Spell Synergy

Allows characters to combine compatible spells for enhanced effects by spending
additional MP. Combinations create synergistic effects greater than the sum of parts.

Canonical spell combinations from the Development Bible:
- Elemental Fusion: Combine elemental spells for hybrid damage
- Temporal Weaving: Combine time-based effects for cascading triggers
- Layered Enchantment: Stack multiple enchantments on same target
- Ritual Convergence: Combine multiple casters for massive effects
"""

from typing import Dict, Any, Optional, List, Protocol, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class CombinationType(Enum):
    """Types of spell combinations"""
    ELEMENTAL_FUSION = "elemental_fusion"          # Combine elemental damage types
    TEMPORAL_WEAVING = "temporal_weaving"          # Sequential time-based effects
    LAYERED_ENCHANTMENT = "layered_enchantment"    # Multiple buffs/debuffs
    POWER_AMPLIFICATION = "power_amplification"    # Raw power increase
    RANGE_SYNTHESIS = "range_synthesis"            # Combine area effects
    DURATION_STACKING = "duration_stacking"        # Extend duration effects
    CONDITIONAL_TRIGGER = "conditional_trigger"    # If-then spell logic

@dataclass
class SpellCombination:
    """Definition of a spell combination"""
    name: str
    type: CombinationType
    required_spells: List[str]           # Spell names that must be included
    compatible_schools: List[str]        # Magic schools that work together
    mp_cost_multiplier: float           # Extra MP cost (1.5 = 50% extra)
    max_spells: int                     # Maximum spells in combination
    synergy_bonus: Dict[str, float]     # Bonus effects (damage, range, etc.)
    description: str
    requirements: List[str] = None       # Special requirements

@dataclass
class CombinationResult:
    """Result of attempting a spell combination"""
    success: bool
    combination_name: str
    total_mp_cost: int
    spells_combined: List[str]
    synergy_effects: Dict[str, Any]
    enhanced_properties: Dict[str, Any]
    error_message: Optional[str] = None

class SpellData(Protocol):
    """Protocol for spell data"""
    name: str
    school: str
    mp_cost: int
    base_damage: Optional[int]
    base_healing: Optional[int]
    range_feet: int
    duration_seconds: Optional[int]
    damage_type: Optional[str]

class SpellCombinationService:
    """Service for combining spells into powerful synergistic effects"""
    
    def __init__(self):
        self.combinations = {
            "elemental_storm": SpellCombination(
                name="Elemental Storm",
                type=CombinationType.ELEMENTAL_FUSION,
                required_spells=[],
                compatible_schools=["evocation"],
                mp_cost_multiplier=1.25,
                max_spells=3,
                synergy_bonus={
                    "damage_multiplier": 1.75,
                    "area_bonus": 10,
                    "additional_damage_types": 2
                },
                description="Fuse multiple elemental spells into a devastating storm",
                requirements=["different_damage_types"]
            ),
            "temporal_cascade": SpellCombination(
                name="Temporal Cascade",
                type=CombinationType.TEMPORAL_WEAVING,
                required_spells=[],
                compatible_schools=["transmutation", "divination"],
                mp_cost_multiplier=2.0,
                max_spells=4,
                synergy_bonus={
                    "duration_multiplier": 3.0,
                    "cascade_triggers": 3,
                    "effect_delay": True
                },
                description="Chain time-based effects for cascading triggers",
                requirements=["duration_spells"]
            ),
            "layered_ward": SpellCombination(
                name="Layered Ward",
                type=CombinationType.LAYERED_ENCHANTMENT,
                required_spells=[],
                compatible_schools=["abjuration", "enchantment"],
                mp_cost_multiplier=1.5,
                max_spells=5,
                synergy_bonus={
                    "protection_stacking": True,
                    "resistance_bonus": 2,
                    "duration_overlap": True
                },
                description="Layer multiple protective enchantments",
                requirements=["buff_or_protection"]
            ),
            "power_convergence": SpellCombination(
                name="Power Convergence",
                type=CombinationType.POWER_AMPLIFICATION,
                required_spells=[],
                compatible_schools=["evocation", "necromancy"],
                mp_cost_multiplier=1.75,
                max_spells=2,
                synergy_bonus={
                    "damage_multiplier": 2.5,
                    "critical_chance": 0.25,
                    "penetration_bonus": 5
                },
                description="Converge raw magical power for devastating effect",
                requirements=["damage_spells"]
            ),
            "area_synthesis": SpellCombination(
                name="Area Synthesis",
                type=CombinationType.RANGE_SYNTHESIS,
                required_spells=[],
                compatible_schools=["evocation", "conjuration"],
                mp_cost_multiplier=1.4,
                max_spells=3,
                synergy_bonus={
                    "area_multiplier": 2.0,
                    "range_multiplier": 1.5,
                    "overlapping_effects": True
                },
                description="Synthesize area effects for massive coverage",
                requirements=["area_spells"]
            )
        }
    
    def get_available_combinations(self, spells: List[SpellData]) -> List[SpellCombination]:
        """Get combinations available for given spells"""
        available = []
        
        for combination in self.combinations.values():
            if self._can_create_combination(combination, spells):
                available.append(combination)
        
        return available
    
    def _can_create_combination(self, combination: SpellCombination, spells: List[SpellData]) -> bool:
        """Check if spells can create the combination"""
        if len(spells) < 2 or len(spells) > combination.max_spells:
            return False
        
        # Check required spells
        if combination.required_spells:
            spell_names = [spell.name for spell in spells]
            for required in combination.required_spells:
                if required not in spell_names:
                    return False
        
        # Check compatible schools
        if combination.compatible_schools:
            spell_schools = [spell.school for spell in spells]
            for school in spell_schools:
                if school not in combination.compatible_schools:
                    return False
        
        # Check special requirements
        if combination.requirements:
            if not self._check_requirements(combination.requirements, spells):
                return False
        
        return True
    
    def _check_requirements(self, requirements: List[str], spells: List[SpellData]) -> bool:
        """Check if spells meet special requirements"""
        for requirement in requirements:
            if requirement == "different_damage_types":
                damage_types = set()
                for spell in spells:
                    if spell.damage_type:
                        damage_types.add(spell.damage_type)
                if len(damage_types) < 2:
                    return False
            
            elif requirement == "duration_spells":
                duration_count = sum(1 for spell in spells if spell.duration_seconds and spell.duration_seconds > 0)
                if duration_count < 2:
                    return False
            
            elif requirement == "damage_spells":
                damage_count = sum(1 for spell in spells if spell.base_damage and spell.base_damage > 0)
                if damage_count < 2:
                    return False
            
            elif requirement == "area_spells":
                # This would require area_of_effect data
                area_count = sum(1 for spell in spells if spell.range_feet > 30)
                if area_count < 2:
                    return False
            
            elif requirement == "buff_or_protection":
                # Check for healing or protective spells
                protection_count = sum(1 for spell in spells 
                                    if spell.base_healing or spell.school == "abjuration")
                if protection_count < 2:
                    return False
        
        return True
    
    def calculate_combination_cost(self, spells: List[SpellData], combination: SpellCombination) -> int:
        """Calculate total MP cost for spell combination"""
        base_cost = sum(spell.mp_cost for spell in spells)
        total_cost = int(base_cost * combination.mp_cost_multiplier)
        return max(base_cost + 1, total_cost)  # Minimum 1 extra MP
    
    def combine_spells(
        self,
        spells: List[SpellData],
        combination_name: str,
        available_mp: int
    ) -> CombinationResult:
        """Combine spells using specified combination"""
        
        if combination_name not in self.combinations:
            return CombinationResult(
                success=False,
                combination_name=combination_name,
                total_mp_cost=0,
                spells_combined=[],
                synergy_effects={},
                enhanced_properties={},
                error_message=f"Unknown combination: {combination_name}"
            )
        
        combination = self.combinations[combination_name]
        
        # Validate combination is possible
        if not self._can_create_combination(combination, spells):
            return CombinationResult(
                success=False,
                combination_name=combination_name,
                total_mp_cost=0,
                spells_combined=[],
                synergy_effects={},
                enhanced_properties={},
                error_message=f"Spells cannot create {combination_name}"
            )
        
        # Calculate cost
        total_cost = self.calculate_combination_cost(spells, combination)
        
        # Check MP availability
        if total_cost > available_mp:
            return CombinationResult(
                success=False,
                combination_name=combination_name,
                total_mp_cost=total_cost,
                spells_combined=[],
                synergy_effects={},
                enhanced_properties={},
                error_message=f"Insufficient MP. Required: {total_cost}, Available: {available_mp}"
            )
        
        # Apply combination effects
        enhanced_properties = self._apply_combination_effects(spells, combination)
        
        return CombinationResult(
            success=True,
            combination_name=combination_name,
            total_mp_cost=total_cost,
            spells_combined=[spell.name for spell in spells],
            synergy_effects=combination.synergy_bonus,
            enhanced_properties=enhanced_properties
        )
    
    def _apply_combination_effects(self, spells: List[SpellData], combination: SpellCombination) -> Dict[str, Any]:
        """Apply combination synergy effects to spells"""
        enhanced = {
            "combination_type": combination.type.value,
            "combination_name": combination.name,
            "base_spells": [spell.name for spell in spells],
            "total_base_damage": sum(spell.base_damage or 0 for spell in spells),
            "total_base_healing": sum(spell.base_healing or 0 for spell in spells),
            "max_range": max(spell.range_feet for spell in spells),
            "combined_schools": list(set(spell.school for spell in spells))
        }
        
        # Apply synergy bonuses
        for bonus_type, bonus_value in combination.synergy_bonus.items():
            if bonus_type == "damage_multiplier":
                enhanced["final_damage"] = int(enhanced["total_base_damage"] * bonus_value)
            
            elif bonus_type == "area_bonus":
                enhanced["area_bonus_feet"] = bonus_value
            
            elif bonus_type == "duration_multiplier":
                max_duration = max((spell.duration_seconds or 0) for spell in spells)
                enhanced["extended_duration"] = int(max_duration * bonus_value)
            
            elif bonus_type == "range_multiplier":
                enhanced["extended_range"] = int(enhanced["max_range"] * bonus_value)
            
            elif bonus_type == "additional_damage_types":
                damage_types = [spell.damage_type for spell in spells if spell.damage_type]
                enhanced["damage_types"] = damage_types
                enhanced["hybrid_damage"] = True
            
            elif bonus_type == "cascade_triggers":
                enhanced["delayed_effects"] = bonus_value
                enhanced["trigger_conditions"] = ["on_damage", "on_healing", "on_duration_end"]
            
            elif bonus_type == "protection_stacking":
                enhanced["stacked_protections"] = True
                enhanced["cumulative_resistance"] = True
            
            elif bonus_type == "critical_chance":
                enhanced["enhanced_critical_chance"] = bonus_value
            
            elif bonus_type == "penetration_bonus":
                enhanced["spell_penetration"] = bonus_value
            
            elif bonus_type == "overlapping_effects":
                enhanced["area_overlap"] = True
                enhanced["cumulative_area_damage"] = True
        
        return enhanced
    
    def get_combination_preview(self, spells: List[SpellData], combination_name: str) -> Dict[str, Any]:
        """Get preview of what combination would produce"""
        if combination_name not in self.combinations:
            return {"error": f"Unknown combination: {combination_name}"}
        
        combination = self.combinations[combination_name]
        
        if not self._can_create_combination(combination, spells):
            return {"error": "Spells incompatible with combination"}
        
        cost = self.calculate_combination_cost(spells, combination)
        preview_effects = self._apply_combination_effects(spells, combination)
        
        return {
            "combination_name": combination.name,
            "description": combination.description,
            "mp_cost": cost,
            "spells_required": [spell.name for spell in spells],
            "synergy_effects": combination.synergy_bonus,
            "final_effects": preview_effects
        }

def create_spell_combination_service() -> SpellCombinationService:
    """Factory function to create spell combination service"""
    return SpellCombinationService() 