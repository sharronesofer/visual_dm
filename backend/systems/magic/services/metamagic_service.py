"""
Metamagic Service - Advanced Spell Enhancement

Provides metamagic effects that allow characters to enhance spells by spending
additional MP for increased power, range, duration, or other effects.

Canonical metamagic effects from the Development Bible:
- Empowered: +50% damage/healing for +25% MP cost
- Extended: Double duration for +50% MP cost  
- Enlarged: Double range for +25% MP cost
- Quickened: Reduce casting time for +100% MP cost
- Silent: Remove verbal components for +50% MP cost
- Subtle: Hide magical aura for +75% MP cost
- Twinned: Target second creature for +100% MP cost
"""

from typing import Dict, Any, Optional, List, Protocol
from dataclasses import dataclass
from enum import Enum

class MetamagicType(Enum):
    """Available metamagic effects"""
    EMPOWERED = "empowered"        # +50% damage/healing for +25% MP
    EXTENDED = "extended"          # Double duration for +50% MP
    ENLARGED = "enlarged"          # Double range for +25% MP  
    QUICKENED = "quickened"        # Reduce casting time for +100% MP
    SILENT = "silent"              # Remove verbal components for +50% MP
    SUBTLE = "subtle"              # Hide magical aura for +75% MP
    TWINNED = "twinned"            # Target second creature for +100% MP
    MAXIMIZED = "maximized"        # Maximum effect for +200% MP
    PERSISTENT = "persistent"      # Concentration-free for +300% MP

@dataclass
class MetamagicEffect:
    """Represents a metamagic modification to a spell"""
    type: MetamagicType
    mp_cost_multiplier: float  # Multiplier for additional MP cost
    description: str
    prerequisites: List[str] = None
    
    def calculate_extra_mp(self, base_mp_cost: int) -> int:
        """Calculate additional MP required for this metamagic"""
        extra_mp = int(base_mp_cost * self.mp_cost_multiplier)
        return max(1, extra_mp)  # Minimum 1 extra MP

class SpellEffect(Protocol):
    """Protocol for spell effect data"""
    damage: Optional[int]
    healing: Optional[int]
    range_feet: int
    duration_seconds: Optional[int]
    concentration: bool
    components: List[str]

@dataclass
class MetamagicResult:
    """Result of applying metamagic to a spell"""
    success: bool
    total_mp_cost: int
    extra_mp_used: int
    modified_effect: Dict[str, Any]
    metamagic_applied: List[MetamagicType]
    error_message: Optional[str] = None

class MetamagicService:
    """Service for applying metamagic effects to spells"""
    
    def __init__(self):
        self.available_metamagic = {
            MetamagicType.EMPOWERED: MetamagicEffect(
                type=MetamagicType.EMPOWERED,
                mp_cost_multiplier=0.25,
                description="Increase damage or healing by 50%"
            ),
            MetamagicType.EXTENDED: MetamagicEffect(
                type=MetamagicType.EXTENDED,
                mp_cost_multiplier=0.50,
                description="Double the spell's duration"
            ),
            MetamagicType.ENLARGED: MetamagicEffect(
                type=MetamagicType.ENLARGED,
                mp_cost_multiplier=0.25,
                description="Double the spell's range"
            ),
            MetamagicType.QUICKENED: MetamagicEffect(
                type=MetamagicType.QUICKENED,
                mp_cost_multiplier=1.00,
                description="Reduce casting time (1 action becomes bonus action)"
            ),
            MetamagicType.SILENT: MetamagicEffect(
                type=MetamagicType.SILENT,
                mp_cost_multiplier=0.50,
                description="Remove verbal component requirement"
            ),
            MetamagicType.SUBTLE: MetamagicEffect(
                type=MetamagicType.SUBTLE,
                mp_cost_multiplier=0.75,
                description="Hide spell's magical aura and casting"
            ),
            MetamagicType.TWINNED: MetamagicEffect(
                type=MetamagicType.TWINNED,
                mp_cost_multiplier=1.00,
                description="Target a second creature with the same spell",
                prerequisites=["single_target"]
            ),
            MetamagicType.MAXIMIZED: MetamagicEffect(
                type=MetamagicType.MAXIMIZED,
                mp_cost_multiplier=2.00,
                description="Spell produces maximum possible effect"
            ),
            MetamagicType.PERSISTENT: MetamagicEffect(
                type=MetamagicType.PERSISTENT,
                mp_cost_multiplier=3.00,
                description="Remove concentration requirement from spell",
                prerequisites=["concentration"]
            )
        }
    
    def get_available_metamagic(self, spell_properties: Dict[str, Any]) -> List[MetamagicEffect]:
        """Get metamagic effects available for a specific spell"""
        available = []
        
        for metamagic in self.available_metamagic.values():
            if self._can_apply_metamagic(metamagic, spell_properties):
                available.append(metamagic)
        
        return available
    
    def _can_apply_metamagic(self, metamagic: MetamagicEffect, spell_properties: Dict[str, Any]) -> bool:
        """Check if metamagic can be applied to spell"""
        if not metamagic.prerequisites:
            return True
        
        for prerequisite in metamagic.prerequisites:
            if prerequisite == "single_target" and spell_properties.get("target") != "single_target":
                return False
            elif prerequisite == "concentration" and not spell_properties.get("concentration", False):
                return False
            elif prerequisite == "damage" and not spell_properties.get("base_damage"):
                return False
            elif prerequisite == "healing" and not spell_properties.get("base_healing"):
                return False
        
        return True
    
    def calculate_metamagic_cost(self, base_mp_cost: int, metamagic_types: List[MetamagicType]) -> int:
        """Calculate total MP cost with metamagic applied"""
        total_multiplier = 0.0
        
        for metamagic_type in metamagic_types:
            if metamagic_type in self.available_metamagic:
                total_multiplier += self.available_metamagic[metamagic_type].mp_cost_multiplier
        
        extra_mp = int(base_mp_cost * total_multiplier)
        return base_mp_cost + max(1, extra_mp)
    
    def apply_metamagic(
        self,
        spell_properties: Dict[str, Any],
        base_mp_cost: int,
        metamagic_types: List[MetamagicType],
        available_mp: int
    ) -> MetamagicResult:
        """Apply metamagic effects to a spell"""
        
        # Validate metamagic compatibility
        for metamagic_type in metamagic_types:
            if metamagic_type not in self.available_metamagic:
                return MetamagicResult(
                    success=False,
                    total_mp_cost=base_mp_cost,
                    extra_mp_used=0,
                    modified_effect={},
                    metamagic_applied=[],
                    error_message=f"Unknown metamagic type: {metamagic_type}"
                )
            
            metamagic = self.available_metamagic[metamagic_type]
            if not self._can_apply_metamagic(metamagic, spell_properties):
                return MetamagicResult(
                    success=False,
                    total_mp_cost=base_mp_cost,
                    extra_mp_used=0,
                    modified_effect={},
                    metamagic_applied=[],
                    error_message=f"Cannot apply {metamagic_type.value} to this spell"
                )
        
        # Calculate total cost
        total_mp_cost = self.calculate_metamagic_cost(base_mp_cost, metamagic_types)
        extra_mp_used = total_mp_cost - base_mp_cost
        
        # Check MP availability
        if total_mp_cost > available_mp:
            return MetamagicResult(
                success=False,
                total_mp_cost=total_mp_cost,
                extra_mp_used=extra_mp_used,
                modified_effect={},
                metamagic_applied=[],
                error_message=f"Insufficient MP. Required: {total_mp_cost}, Available: {available_mp}"
            )
        
        # Apply metamagic effects
        modified_effect = spell_properties.copy()
        
        for metamagic_type in metamagic_types:
            modified_effect = self._apply_single_metamagic(modified_effect, metamagic_type)
        
        return MetamagicResult(
            success=True,
            total_mp_cost=total_mp_cost,
            extra_mp_used=extra_mp_used,
            modified_effect=modified_effect,
            metamagic_applied=metamagic_types
        )
    
    def _apply_single_metamagic(self, spell_properties: Dict[str, Any], metamagic_type: MetamagicType) -> Dict[str, Any]:
        """Apply a single metamagic effect to spell properties"""
        modified = spell_properties.copy()
        
        if metamagic_type == MetamagicType.EMPOWERED:
            # Increase damage/healing by 50%
            if modified.get("base_damage"):
                modified["base_damage"] = int(modified["base_damage"] * 1.5)
            if modified.get("base_healing"):
                modified["base_healing"] = int(modified["base_healing"] * 1.5)
        
        elif metamagic_type == MetamagicType.EXTENDED:
            # Double duration
            if modified.get("duration_seconds"):
                modified["duration_seconds"] = modified["duration_seconds"] * 2
        
        elif metamagic_type == MetamagicType.ENLARGED:
            # Double range
            modified["range_feet"] = modified.get("range_feet", 30) * 2
        
        elif metamagic_type == MetamagicType.QUICKENED:
            # Reduce casting time
            casting_time = modified.get("casting_time", "1 action")
            if "1 action" in casting_time:
                modified["casting_time"] = "1 bonus action"
            elif "1 minute" in casting_time:
                modified["casting_time"] = "1 action"
        
        elif metamagic_type == MetamagicType.SILENT:
            # Remove verbal components
            components = modified.get("components", [])
            if "verbal" in components:
                components = [c for c in components if c != "verbal"]
                modified["components"] = components
        
        elif metamagic_type == MetamagicType.SUBTLE:
            # Hide magical aura (add stealth bonus)
            modified["subtle_casting"] = True
            modified["detection_difficulty"] = modified.get("detection_difficulty", 15) + 5
        
        elif metamagic_type == MetamagicType.TWINNED:
            # Enable second target
            modified["additional_targets"] = 1
            modified["twinned_spell"] = True
        
        elif metamagic_type == MetamagicType.MAXIMIZED:
            # Maximum effect values
            if modified.get("base_damage"):
                # Add maximum scaling bonus
                scaling = modified.get("mp_scaling", 1)
                modified["base_damage"] = modified["base_damage"] + (scaling * 3)
            if modified.get("base_healing"):
                scaling = modified.get("healing_scaling", 1)
                modified["base_healing"] = modified["base_healing"] + (scaling * 3)
        
        elif metamagic_type == MetamagicType.PERSISTENT:
            # Remove concentration requirement
            modified["concentration"] = False
            modified["persistent_effect"] = True
        
        # Add metamagic indicator
        metamagic_list = modified.get("metamagic_applied", [])
        metamagic_list.append(metamagic_type.value)
        modified["metamagic_applied"] = metamagic_list
        
        return modified

def create_metamagic_service() -> MetamagicService:
    """Factory function to create metamagic service"""
    return MetamagicService() 