"""
Magic Combat Integration Business Logic

This module provides pure business logic for integrating magic system with combat,
separated from technical concerns.
"""

from typing import Dict, List, Optional, Any, Tuple, Protocol
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from .magic_business_service import MagicBusinessService, SpellEffect, ConcentrationCheck, SaveType
# from backend.systems.character.models.abilities import CharacterAbilities
# from backend.systems.combat.models.combat_state import CombatState


@dataclass
class ActiveConcentration:
    """Tracks an active concentration effect"""
    spell_name: str
    caster_id: str
    target_id: Optional[str]
    start_time: datetime
    duration_seconds: Optional[int]
    effect_data: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if concentration effect has expired"""
        if self.duration_seconds is None:
            return False
        return datetime.now() > self.start_time + timedelta(seconds=self.duration_seconds)


@dataclass
class SpellCastingResult:
    """Complete result of a spell casting attempt"""
    success: bool
    spell_effect: Optional[SpellEffect] = None
    mp_cost: int = 0
    error_message: Optional[str] = None
    concentration_effect: Optional[ActiveConcentration] = None
    target_saves_required: List[Tuple[str, SaveType, int]] = field(default_factory=list)


class TimeProvider(Protocol):
    """Protocol for time operations"""
    
    def get_current_time(self) -> datetime:
        """Get current time"""
        ...


class MagicCombatBusinessService:
    """Pure business logic for magic combat integration"""
    
    def __init__(self, 
                 magic_service: MagicBusinessService,
                 time_provider: TimeProvider):
        self.magic_service = magic_service
        self.time_provider = time_provider
        self.active_concentrations: Dict[str, ActiveConcentration] = {}
    
    def attempt_spell_cast(
        self,
        caster_id: str,
        spell_name: str,
        domain: str,
        target_id: Optional[str],
        abilities: Any,  # Changed type to Any
        current_mp: int,
        proficiency_bonus: int,
        extra_mp: int = 0,
        combat_state: Optional[Any] = None  # Changed type to Any
    ) -> SpellCastingResult:
        """Attempt to cast a spell with full validation and effects"""
        
        # Check if spell can be cast
        if not self.magic_service.can_cast_spell(spell_name, domain, current_mp, extra_mp):
            return SpellCastingResult(
                success=False,
                error_message=f"Cannot cast {spell_name} - insufficient MP or invalid domain"
            )
        
        # Check concentration conflicts
        if self._has_concentration_conflict(caster_id, spell_name):
            # Break existing concentration
            self._break_concentration(caster_id)
        
        # Calculate MP cost
        mp_cost = self.magic_service.calculate_mp_cost(spell_name, domain, extra_mp)
        
        # Cast the spell
        try:
            spell_effect = self.magic_service.cast_spell(
                spell_name, domain, abilities, proficiency_bonus, extra_mp
            )
            
            # Handle concentration
            concentration_effect = None
            if spell_effect.concentration_required:
                concentration_effect = ActiveConcentration(
                    spell_name=spell_name,
                    caster_id=caster_id,
                    target_id=target_id,
                    start_time=self.time_provider.get_current_time(),
                    duration_seconds=spell_effect.duration_seconds
                )
                self.active_concentrations[caster_id] = concentration_effect
            
            # Prepare save requirements
            saves_required = []
            if spell_effect.save_dc and target_id:
                saves_required.append((target_id, spell_effect.save_type, spell_effect.save_dc))
            
            return SpellCastingResult(
                success=True,
                spell_effect=spell_effect,
                mp_cost=mp_cost,
                concentration_effect=concentration_effect,
                target_saves_required=saves_required
            )
            
        except Exception as e:
            return SpellCastingResult(
                success=False,
                error_message=f"Spell casting failed: {str(e)}"
            )
    
    def _has_concentration_conflict(self, caster_id: str, spell_name: str) -> bool:
        """Check if casting this spell would conflict with existing concentration"""
        if caster_id not in self.active_concentrations:
            return False
        
        # Check if spell requires concentration  
        spell_data = self.magic_service.config_repository.get_spell(spell_name)
        if not spell_data:
            return False
        return spell_data.get("concentration", False)
    
    def handle_damage_concentration_check(
        self,
        caster_id: str,
        damage_taken: int,
        abilities: Any,  # Changed type to Any
        proficiency_bonus: int,
        additional_bonuses: int = 0
    ) -> bool:
        """Handle concentration save when caster takes damage"""
        if caster_id not in self.active_concentrations:
            return True  # No concentration to maintain
        
        # Create concentration check
        check = self.magic_service.check_concentration(
            damage_taken, abilities, proficiency_bonus, additional_bonuses
        )
        
        # Make the save
        success = self.magic_service.make_concentration_save(check)
        
        if not success:
            self._break_concentration(caster_id)
        
        return success
    
    def _break_concentration(self, caster_id: str):
        """Break concentration for a specific caster"""
        if caster_id in self.active_concentrations:
            del self.active_concentrations[caster_id]
    
    def apply_spell_damage(
        self,
        spell_effect: SpellEffect,
        target_id: str,
        target_armor_class: int,
        target_damage_reduction: int,
        save_result: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Apply spell damage considering AC/DR bypass and saves"""
        
        if not spell_effect.damage:
            return {"damage": 0, "bypassed_ac": False, "bypassed_dr": False}
        
        damage = spell_effect.damage
        
        # Handle saves
        if spell_effect.save_type and save_result is not None:
            if save_result and hasattr(spell_effect, 'save_for_half'):
                damage = damage // 2
            elif save_result and hasattr(spell_effect, 'save_negates'):
                damage = 0
        
        # Apply AC bypass
        hits_ac = True
        if not spell_effect.bypasses_ac and not spell_effect.auto_hit:
            # In a real system, you'd roll against AC here
            # For now, assume it hits
            hits_ac = True
        
        if not hits_ac:
            damage = 0
        
        # Apply DR bypass
        final_damage = damage
        if not spell_effect.bypasses_dr and damage > 0:
            final_damage = max(0, damage - target_damage_reduction)
        
        return {
            "damage": final_damage,
            "bypassed_ac": spell_effect.bypasses_ac,
            "bypassed_dr": spell_effect.bypasses_dr,
            "auto_hit": spell_effect.auto_hit
        }
    
    def apply_spell_healing(self, spell_effect: SpellEffect, target_id: str) -> int:
        """Apply spell healing effects"""
        if not spell_effect.healing:
            return 0
        return spell_effect.healing
    
    def get_spell_range_for_targeting(self, spell_name: str) -> int:
        """Get spell range for targeting validation"""
        return self.magic_service.get_spell_range_feet(spell_name)
    
    def validate_spell_target(
        self,
        spell_name: str,
        caster_position: Tuple[int, int],
        target_position: Tuple[int, int]
    ) -> bool:
        """Validate if target is within spell range"""
        max_range = self.get_spell_range_for_targeting(spell_name)
        
        # Calculate distance (simplified - use Manhattan distance)
        distance = abs(caster_position[0] - target_position[0]) + abs(caster_position[1] - target_position[1])
        
        # Convert grid distance to feet (assuming 5 feet per grid square)
        distance_feet = distance * 5
        
        return distance_feet <= max_range
    
    def update_concentration_effects(self):
        """Update and clean up expired concentration effects"""
        current_time = self.time_provider.get_current_time()
        expired_casters = []
        
        for caster_id, effect in self.active_concentrations.items():
            if effect.is_expired():
                expired_casters.append(caster_id)
        
        for caster_id in expired_casters:
            del self.active_concentrations[caster_id]
    
    def get_active_concentration(self, caster_id: str) -> Optional[ActiveConcentration]:
        """Get active concentration for a caster"""
        return self.active_concentrations.get(caster_id)
    
    def get_all_concentration_effects(self) -> Dict[str, ActiveConcentration]:
        """Get all active concentration effects"""
        return self.active_concentrations.copy()
    
    def dispel_magic_interaction(
        self,
        target_id: str,
        dispel_power: int,
        caster_abilities: Any,  # Changed type to Any
        proficiency_bonus: int
    ) -> Dict[str, Any]:
        """Handle dispel magic interactions with concentration effects"""
        
        # Check if target has active concentrations
        target_concentration = self.get_active_concentration(target_id)
        if not target_concentration:
            return {"success": False, "message": "No magic effects to dispel"}
        
        # Business rule: Dispel check = d20 + caster ability + proficiency vs spell DC
        # For simplicity, assume dispel DC = 10 + spell level (estimated from MP cost)
        spell_data = self.magic_service.config_repository.get_spell(target_concentration.spell_name)
        if not spell_data:
            return {"success": False, "message": "Cannot determine spell difficulty"}
        
        # Estimate spell level from MP cost (rough approximation)
        mp_cost = spell_data.get("mp_cost", 1)
        estimated_level = max(1, mp_cost // 2)
        dispel_dc = 10 + estimated_level
        
        # Make dispel check (simplified)
        import random
        roll = random.randint(1, 20)
        
        # Use Intelligence for dispel magic by default
        int_modifier = getattr(caster_abilities, "intelligence_modifier", 0)
        total = roll + int_modifier + proficiency_bonus + dispel_power
        
        success = total >= dispel_dc
        
        if success:
            self._break_concentration(target_id)
            return {
                "success": True,
                "message": f"Successfully dispelled {target_concentration.spell_name}",
                "roll": roll,
                "total": total,
                "dc": dispel_dc
            }
        else:
            return {
                "success": False,
                "message": f"Failed to dispel {target_concentration.spell_name}",
                "roll": roll,
                "total": total,
                "dc": dispel_dc
            }
    
    def get_available_spells_by_mp(self, domain: str, current_mp: int) -> List[Dict[str, Any]]:
        """Get spells available for casting with current MP"""
        available_spells = self.magic_service.get_available_spells_for_domain(domain)
        castable = []
        
        for spell_name in available_spells:
            mp_cost = self.magic_service.calculate_mp_cost(spell_name, domain)
            if mp_cost <= current_mp:
                spell_data = self.magic_service.config_repository.get_spell(spell_name)
                if spell_data:
                    castable.append({
                        "name": spell_name,
                        "mp_cost": mp_cost,
                        "description": spell_data.get("description", ""),
                        "school": spell_data.get("school", ""),
                        "range_feet": spell_data.get("range_feet", 30)
                    })
        
        return sorted(castable, key=lambda x: x["mp_cost"])


def create_magic_combat_service(
    magic_service: MagicBusinessService,
    time_provider: TimeProvider
) -> MagicCombatBusinessService:
    """Factory function to create magic combat service"""
    return MagicCombatBusinessService(magic_service, time_provider) 