"""
EffectVisualizer module for the Visual DM combat system.

This module implements a system for visualizing combat effects above combatants.
It creates and manages effect icons at runtime with no scene/prefab dependencies,
using a pool of GameObjects for optimal performance.

Following the design principles from the Development Bible, this implementation:
1. Displays effect icons above combatants at runtime
2. Uses SpriteRenderer for visual representation
3. Pools GameObjects for better performance
4. Has no scene/prefab dependencies
5. Is entirely runtime-generated
"""

import logging
from typing import Dict, List, Any, Tuple, Optional, Set
import uuid

from .object_pool import ObjectPool
from .effect_pipeline import CombatEffect, EffectType

# Set up logging
logger = logging.getLogger(__name__)

class EffectIcon:
    """Represents a visual icon for a combat effect."""
    
    def __init__(self, effect_id: str, effect_type: EffectType, 
                position: Tuple[float, float, float] = (0, 0, 0),
                scale: float = 1.0, color: Tuple[float, float, float, float] = (1, 1, 1, 1)):
        """
        Initialize a new effect icon.
        
        Args:
            effect_id: ID of the associated effect
            effect_type: Type of the effect (determines appearance)
            position: (x, y, z) position of the icon
            scale: Size scaling factor
            color: (r, g, b, a) color values (0-1)
        """
        self.id = str(uuid.uuid4())
        self.effect_id = effect_id
        self.effect_type = effect_type
        self.position = position
        self.scale = scale
        self.color = color
        self.visible = True
        self.parent_id = None  # ID of the combatant this icon is attached to
        
    def set_position(self, position: Tuple[float, float, float]) -> None:
        """Set the position of this icon."""
        self.position = position
        
    def set_color(self, color: Tuple[float, float, float, float]) -> None:
        """Set the color of this icon."""
        self.color = color
        
    def set_scale(self, scale: float) -> None:
        """Set the scale of this icon."""
        self.scale = scale
        
    def set_visible(self, visible: bool) -> None:
        """Set visibility of this icon."""
        self.visible = visible
        
    def set_parent(self, parent_id: str) -> None:
        """Set the parent combatant ID for this icon."""
        self.parent_id = parent_id
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "effect_id": self.effect_id,
            "effect_type": self.effect_type.name,
            "position": self.position,
            "scale": self.scale,
            "color": self.color,
            "visible": self.visible,
            "parent_id": self.parent_id
        }


class EffectVisualizer:
    """
    Manages the visual representation of combat effects.
    
    Creates and manages icons for effects above combatants, handling positioning,
    animation, and cleanup.
    """
    
    def __init__(self):
        """Initialize the effect visualizer."""
        self.icons: Dict[str, EffectIcon] = {}  # ID -> EffectIcon
        self.effects_to_icons: Dict[str, str] = {}  # Effect ID -> Icon ID
        self.combatant_icons: Dict[str, List[str]] = {}  # Combatant ID -> [Icon IDs]
        
        # Create a pool for effect icons
        self.icon_pool = ObjectPool(
            EffectIcon,
            initial_size=20,
            factory=lambda: EffectIcon("", EffectType.BUFF),
            reset_func=self._reset_icon
        )
        
        # Color mapping for effect types
        self.effect_type_colors: Dict[EffectType, Tuple[float, float, float, float]] = {
            EffectType.BUFF: (0.0, 1.0, 0.0, 1.0),  # Green
            EffectType.DEBUFF: (1.0, 0.0, 0.0, 1.0),  # Red
            EffectType.CONDITION: (1.0, 1.0, 0.0, 1.0),  # Yellow
            EffectType.DAMAGE_OVER_TIME: (1.0, 0.5, 0.0, 1.0),  # Orange
            EffectType.HEAL_OVER_TIME: (0.0, 1.0, 0.5, 1.0),  # Teal
            EffectType.RESISTANCE: (0.5, 0.5, 1.0, 1.0),  # Light Blue
            EffectType.VULNERABILITY: (1.0, 0.0, 1.0, 1.0),  # Magenta
            EffectType.IMMUNITY: (0.0, 0.0, 1.0, 1.0),  # Blue
            EffectType.TRIGGER: (0.5, 0.0, 0.5, 1.0),  # Purple
            EffectType.PASSIVE: (0.5, 0.5, 0.5, 1.0)  # Gray
        }
        
        logger.info("EffectVisualizer initialized")
    
    def _reset_icon(self, icon: EffectIcon) -> None:
        """
        Reset an icon to default state for reuse.
        
        Args:
            icon: The icon to reset
        """
        icon.effect_id = ""
        icon.effect_type = EffectType.BUFF
        icon.position = (0, 0, 0)
        icon.scale = 1.0
        icon.color = (1, 1, 1, 1)
        icon.visible = True
        icon.parent_id = None
    
    def create_icon_for_effect(self, effect: CombatEffect, combatant_id: str, 
                              position: Tuple[float, float, float] = (0, 0, 0),
                              scale: float = 1.0) -> Optional[str]:
        """
        Create a visual icon for an effect on a combatant.
        
        Args:
            effect: The effect to visualize
            combatant_id: ID of the combatant with the effect
            position: Initial position for the icon
            scale: Size scaling factor
            
        Returns:
            ID of the created icon, or None if creation failed
        """
        # Check if this effect already has an icon
        if effect.id in self.effects_to_icons:
            return self.effects_to_icons[effect.id]
            
        # Get an icon from the pool
        icon = self.icon_pool.acquire()
        icon.effect_id = effect.id
        icon.effect_type = effect.effect_type
        icon.position = position
        icon.scale = scale
        icon.set_parent(combatant_id)
        
        # Set color based on effect type
        if effect.effect_type in self.effect_type_colors:
            icon.color = self.effect_type_colors[effect.effect_type]
        
        # Store the icon
        self.icons[icon.id] = icon
        self.effects_to_icons[effect.id] = icon.id
        
        # Add to combatant's icons
        if combatant_id not in self.combatant_icons:
            self.combatant_icons[combatant_id] = []
        self.combatant_icons[combatant_id].append(icon.id)
        
        logger.debug(f"Created icon {icon.id} for effect {effect.id} on combatant {combatant_id}")
        return icon.id
    
    def remove_icon_for_effect(self, effect_id: str) -> bool:
        """
        Remove the icon for an effect.
        
        Args:
            effect_id: ID of the effect whose icon should be removed
            
        Returns:
            True if an icon was removed, False otherwise
        """
        if effect_id not in self.effects_to_icons:
            return False
            
        icon_id = self.effects_to_icons[effect_id]
        icon = self.icons.get(icon_id)
        
        if not icon:
            logger.warning(f"Icon {icon_id} not found for effect {effect_id}")
            return False
            
        # Remove from combatant's icons
        if icon.parent_id and icon.parent_id in self.combatant_icons:
            if icon_id in self.combatant_icons[icon.parent_id]:
                self.combatant_icons[icon.parent_id].remove(icon_id)
        
        # Remove from mappings
        del self.effects_to_icons[effect_id]
        del self.icons[icon_id]
        
        # Return to pool
        self.icon_pool.release(icon)
        
        logger.debug(f"Removed icon {icon_id} for effect {effect_id}")
        return True
    
    def update_icon_positions(self, combatant_id: str, base_position: Tuple[float, float, float]) -> None:
        """
        Update positions of all icons for a combatant.
        
        Args:
            combatant_id: ID of the combatant
            base_position: Base position (x, y, z) of the combatant
        """
        if combatant_id not in self.combatant_icons:
            return
            
        # Get all icons for this combatant
        icon_ids = self.combatant_icons[combatant_id]
        
        # Calculate positions in a grid or circle around the combatant
        num_icons = len(icon_ids)
        
        for i, icon_id in enumerate(icon_ids):
            if icon_id not in self.icons:
                continue
                
            icon = self.icons[icon_id]
            
            # Position in a row above the combatant
            # Can be enhanced to use a grid or circle for many effects
            offset_x = (i - num_icons / 2) * 0.5  # 0.5 unit spacing
            offset_y = 1.5  # 1.5 units above
            
            new_pos = (base_position[0] + offset_x, base_position[1] + offset_y, base_position[2])
            icon.set_position(new_pos)
    
    def update_all_icons(self, combat_state: Dict[str, Any]) -> None:
        """
        Update all icons based on current combat state.
        
        Args:
            combat_state: Current state of combat
        """
        # Get all effects from combat state
        all_effects = combat_state.get("effects", {})
        
        # Track active effect IDs to remove stale icons
        active_effect_ids: Set[str] = set()
        
        # Create/update icons for all active effects
        for character_id, character_data in combat_state.get("characters", {}).items():
            character_position = character_data.get("position", (0, 0, 0))
            
            # Get effects for this character
            character_effects = character_data.get("effects", [])
            
            for effect_id in character_effects:
                active_effect_ids.add(effect_id)
                
                # Skip if icon already exists
                if effect_id in self.effects_to_icons:
                    continue
                    
                # Get effect data
                effect_data = all_effects.get(effect_id)
                if not effect_data:
                    continue
                    
                # Create a temporary effect object
                try:
                    effect_type = EffectType[effect_data.get("effect_type", "BUFF")]
                except (KeyError, ValueError):
                    effect_type = EffectType.BUFF
                    
                effect = CombatEffect(
                    id=effect_id,
                    name=effect_data.get("name", ""),
                    effect_type=effect_type
                )
                
                # Create icon
                self.create_icon_for_effect(effect, character_id, character_position)
            
            # Update positions of all icons for this character
            self.update_icon_positions(character_id, character_position)
        
        # Remove icons for effects that are no longer active
        stale_effects = set(self.effects_to_icons.keys()) - active_effect_ids
        for effect_id in stale_effects:
            self.remove_icon_for_effect(effect_id)
    
    def clear_all_icons(self) -> None:
        """Remove all effect icons."""
        # Copy the keys to avoid modifying during iteration
        effect_ids = list(self.effects_to_icons.keys())
        
        for effect_id in effect_ids:
            self.remove_icon_for_effect(effect_id)
            
        logger.info("Cleared all effect icons")

    def get_all_icons(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active icons for serialization.
        
        Returns:
            Dictionary of icon data for serialization
        """
        return {icon_id: icon.to_dict() for icon_id, icon in self.icons.items()}

    def handle_effect_applied(self, effect: CombatEffect, target_id: str, position: Tuple[float, float, float] = (0, 0, 0)) -> None:
        """
        Handle an effect being applied to a target.
        
        Args:
            effect: The effect being applied
            target_id: ID of the target
            position: Position of the target
        """
        self.create_icon_for_effect(effect, target_id, position)
    
    def handle_effect_removed(self, effect_id: str) -> None:
        """
        Handle an effect being removed.
        
        Args:
            effect_id: ID of the effect being removed
        """
        self.remove_icon_for_effect(effect_id)

# Create a singleton instance for global access
effect_visualizer = EffectVisualizer() 