"""
CombatAnimationSystem module for the Visual DM combat system.

This module implements a system for managing and coordinating all combat-related
animations including attacks, spells, movement, and reactions. It provides a 
flexible, event-driven animation framework that works entirely at runtime.

Following the design principles from the Development Bible, this implementation:
1. Is entirely runtime-generated with no scene/prefab dependencies
2. Uses a modular, data-driven approach to animations
3. Supports a wide variety of combat actions and effects
4. Can be extended with new animation types
"""

import logging
import random
import time
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
import uuid

# Set up logging
logger = logging.getLogger(__name__)

class AnimationDefinition:
    """
    Defines a specific animation type that can be played during combat.
    
    This class represents the metadata and parameters for a specific 
    type of animation (e.g., "slash", "fireball", "heal").
    """
    
    def __init__(
        self,
        anim_id: str,
        name: str,
        category: str,
        duration: float,
        properties: Dict[str, Any] = None
    ):
        """
        Initialize a new animation definition.
        
        Args:
            anim_id: Unique identifier for this animation type
            name: Human-readable name
            category: Animation category (attack, spell, movement, etc.)
            duration: Base duration in seconds
            properties: Additional properties specific to this animation
        """
        self.anim_id = anim_id
        self.name = name
        self.category = category
        self.duration = duration
        self.properties = properties or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.anim_id,
            "name": self.name,
            "category": self.category,
            "duration": self.duration,
            "properties": self.properties
        }

class AnimationInstance:
    """
    Represents a specific instance of an animation being played.
    
    This class tracks the state of a single animation playing in the
    combat scene, including timing, source, target, and progress.
    """
    
    def __init__(
        self,
        instance_id: str,
        definition: AnimationDefinition,
        source_id: Optional[str],
        target_ids: List[str],
        start_time: float,
        parameters: Dict[str, Any] = None,
        on_complete: Optional[Callable] = None
    ):
        """
        Initialize a new animation instance.
        
        Args:
            instance_id: Unique identifier for this instance
            definition: AnimationDefinition for this animation
            source_id: ID of the source entity (None for scene-wide)
            target_ids: IDs of target entities (can be empty)
            start_time: Time when the animation started
            parameters: Runtime parameters for this instance
            on_complete: Callback function when animation completes
        """
        self.instance_id = instance_id
        self.definition = definition
        self.source_id = source_id
        self.target_ids = target_ids
        self.start_time = start_time
        self.parameters = parameters or {}
        self.on_complete = on_complete
        self.is_complete = False
        self.progress = 0.0  # 0.0 to 1.0
        
        # Calculate actual duration based on parameters
        self.speed_multiplier = parameters.get("speed_multiplier", 1.0)
        self.duration = definition.duration / self.speed_multiplier
    
    def update(self, current_time: float) -> bool:
        """
        Update animation progress based on current time.
        
        Args:
            current_time: Current time for progress calculation
            
        Returns:
            True if animation just completed this update, False otherwise
        """
        if self.is_complete:
            return False
            
        elapsed = current_time - self.start_time
        self.progress = min(1.0, elapsed / self.duration)
        
        # Check if animation just completed
        if self.progress >= 1.0 and not self.is_complete:
            self.is_complete = True
            
            # Call completion callback if provided
            if self.on_complete:
                try:
                    self.on_complete(self)
                except Exception as e:
                    logger.error(f"Error in animation completion callback: {e}")
            
            return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "instance_id": self.instance_id,
            "definition_id": self.definition.anim_id,
            "source_id": self.source_id,
            "target_ids": self.target_ids,
            "progress": self.progress,
            "is_complete": self.is_complete,
            "parameters": self.parameters,
            "remaining_time": max(0, self.duration * (1 - self.progress))
        }

class CombatAnimationSystem:
    """
    Manages and coordinates all combat animations.
    
    This system handles creating, tracking, and updating all animations
    during combat. It provides an API for triggering animations and
    querying animation state.
    """
    
    def __init__(self):
        """Initialize the animation system."""
        self.animation_definitions: Dict[str, AnimationDefinition] = {}
        self.active_animations: Dict[str, AnimationInstance] = {}
        self.animation_queue: List[Dict[str, Any]] = []
        self.paused = False
        self.last_update_time = time.time()
        self.animation_speed_multiplier = 1.0
        
        # Initialize with default animations
        self._init_default_animations()
        
        logger.info("CombatAnimationSystem initialized")
    
    def _init_default_animations(self) -> None:
        """Initialize the default set of animations."""
        # Melee attack animations
        self.register_animation(AnimationDefinition(
            "melee_slash", "Slash Attack", "melee_attack", 0.8,
            {"swing_arc": 120, "weapon_trail": True}
        ))
        
        self.register_animation(AnimationDefinition(
            "melee_stab", "Stab Attack", "melee_attack", 0.6,
            {"forward_thrust": True, "weapon_trail": True}
        ))
        
        self.register_animation(AnimationDefinition(
            "melee_smash", "Smash Attack", "melee_attack", 1.0,
            {"overhead_arc": True, "impact_effect": "heavy"}
        ))
        
        # Ranged attack animations
        self.register_animation(AnimationDefinition(
            "ranged_arrow", "Arrow Shot", "ranged_attack", 0.7,
            {"projectile_type": "arrow", "arc_height": 0.2}
        ))
        
        self.register_animation(AnimationDefinition(
            "ranged_throw", "Throwing Attack", "ranged_attack", 0.6,
            {"projectile_type": "thrown", "arc_height": 0.4}
        ))
        
        # Spell animations
        self.register_animation(AnimationDefinition(
            "spell_fireball", "Fireball", "spell", 1.2,
            {"element": "fire", "projectile_speed": 8.0, "explosion_radius": 3.0}
        ))
        
        self.register_animation(AnimationDefinition(
            "spell_lightning", "Lightning Bolt", "spell", 0.9,
            {"element": "lightning", "is_instant": True, "fork_count": 0}
        ))
        
        self.register_animation(AnimationDefinition(
            "spell_heal", "Healing Light", "spell", 1.0,
            {"element": "holy", "is_beneficial": True, "radius": 2.0}
        ))
        
        # Movement animations
        self.register_animation(AnimationDefinition(
            "move_walk", "Walk", "movement", 1.0,
            {"speed": 1.0, "footstep_sound": "soft"}
        ))
        
        self.register_animation(AnimationDefinition(
            "move_run", "Run", "movement", 0.7,
            {"speed": 2.0, "footstep_sound": "fast"}
        ))
        
        self.register_animation(AnimationDefinition(
            "move_teleport", "Teleport", "movement", 0.5,
            {"fade_out": True, "fade_in": True, "particles": "magic"}
        ))
        
        # Reaction animations
        self.register_animation(AnimationDefinition(
            "react_hit", "Hit Reaction", "reaction", 0.5,
            {"stagger_amount": 0.3, "shake_intensity": 0.2}
        ))
        
        self.register_animation(AnimationDefinition(
            "react_dodge", "Dodge", "reaction", 0.4,
            {"dodge_distance": 1.0, "return_to_position": True}
        ))
        
        # Effect animations
        self.register_animation(AnimationDefinition(
            "effect_apply", "Apply Effect", "effect", 0.7,
            {"rise_height": 1.0, "fade_in": True, "rotation": True}
        ))
        
        self.register_animation(AnimationDefinition(
            "effect_remove", "Remove Effect", "effect", 0.5,
            {"fade_out": True, "sink_distance": 0.5, "scale_down": True}
        ))
    
    def register_animation(self, definition: AnimationDefinition) -> None:
        """
        Register a new animation definition.
        
        Args:
            definition: The animation definition to register
        """
        self.animation_definitions[definition.anim_id] = definition
        logger.debug(f"Registered animation definition: {definition.name} ({definition.anim_id})")
    
    def play_animation(
        self,
        definition_id: str,
        source_id: Optional[str] = None,
        target_ids: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        on_complete: Optional[Callable] = None,
        queue: bool = False
    ) -> Optional[str]:
        """
        Play an animation immediately or queue it.
        
        Args:
            definition_id: ID of the animation definition to play
            source_id: ID of the source entity (None for scene-wide)
            target_ids: IDs of target entities (can be empty list)
            parameters: Runtime parameters for this instance
            on_complete: Callback function when animation completes
            queue: If True, queue the animation if others are playing
            
        Returns:
            ID of the created animation instance, or None if animation not found
        """
        if definition_id not in self.animation_definitions:
            logger.error(f"Unknown animation definition: {definition_id}")
            return None
            
        definition = self.animation_definitions[definition_id]
        parameters = parameters or {}
        target_ids = target_ids or []
        
        # Apply global speed multiplier
        if "speed_multiplier" not in parameters:
            parameters["speed_multiplier"] = self.animation_speed_multiplier
        
        # Check if we need to queue this animation
        if queue and self.active_animations:
            self.animation_queue.append({
                "definition_id": definition_id,
                "source_id": source_id,
                "target_ids": target_ids,
                "parameters": parameters,
                "on_complete": on_complete
            })
            logger.debug(f"Queued animation: {definition.name}")
            return None
        
        # Create and start the animation
        instance_id = f"anim_{uuid.uuid4().hex[:8]}"
        current_time = time.time()
        
        instance = AnimationInstance(
            instance_id=instance_id,
            definition=definition,
            source_id=source_id,
            target_ids=target_ids,
            start_time=current_time,
            parameters=parameters,
            on_complete=on_complete
        )
        
        self.active_animations[instance_id] = instance
        logger.debug(f"Started animation: {definition.name} ({instance_id})")
        
        return instance_id
    
    def stop_animation(self, instance_id: str, complete_callback: bool = False) -> bool:
        """
        Stop an active animation.
        
        Args:
            instance_id: ID of the animation instance to stop
            complete_callback: Whether to run the completion callback
            
        Returns:
            True if animation was found and stopped, False otherwise
        """
        if instance_id not in self.active_animations:
            return False
            
        instance = self.active_animations[instance_id]
        
        # Run completion callback if requested
        if complete_callback and instance.on_complete and not instance.is_complete:
            try:
                instance.on_complete(instance)
            except Exception as e:
                logger.error(f"Error in animation completion callback: {e}")
        
        # Remove the animation
        del self.active_animations[instance_id]
        logger.debug(f"Stopped animation: {instance.definition.name} ({instance_id})")
        
        return True
    
    def stop_all_animations(self, complete_callbacks: bool = False) -> int:
        """
        Stop all active animations.
        
        Args:
            complete_callbacks: Whether to run completion callbacks
            
        Returns:
            Number of animations stopped
        """
        count = 0
        
        # Make a copy of the keys since we'll be modifying the dictionary
        for instance_id in list(self.active_animations.keys()):
            if self.stop_animation(instance_id, complete_callbacks):
                count += 1
        
        # Clear the queue too
        queue_count = len(self.animation_queue)
        self.animation_queue.clear()
        
        logger.debug(f"Stopped {count} active animations and cleared {queue_count} from queue")
        return count
    
    def pause_animations(self, pause: bool = True) -> None:
        """
        Pause or resume all animations.
        
        Args:
            pause: True to pause, False to resume
        """
        # Only do something if state is changing
        if pause != self.paused:
            self.paused = pause
            current_time = time.time()
            
            if pause:
                # Store the time we paused to adjust later
                self.pause_time = current_time
                logger.debug("Animations paused")
            else:
                # When resuming, adjust all animation start times
                time_diff = current_time - self.pause_time
                
                for instance in self.active_animations.values():
                    instance.start_time += time_diff
                
                logger.debug("Animations resumed")
    
    def update(self, delta_time: Optional[float] = None) -> int:
        """
        Update all active animations.
        
        Args:
            delta_time: Time elapsed since last update (in seconds)
                       If None, will use real-time calculation
            
        Returns:
            Number of animations that completed this update
        """
        if self.paused:
            return 0
            
        current_time = time.time()
        
        # If delta_time is provided, use it to simulate time passing
        if delta_time is not None:
            self.last_update_time += delta_time
            current_time = self.last_update_time
        else:
            self.last_update_time = current_time
        
        completed_count = 0
        completed_animations = []
        
        # Update all active animations
        for instance_id, instance in self.active_animations.items():
            if instance.update(current_time):
                completed_count += 1
                completed_animations.append(instance_id)
        
        # Remove completed animations
        for instance_id in completed_animations:
            del self.active_animations[instance_id]
        
        # Start animations from the queue if any are waiting
        if not self.active_animations and self.animation_queue:
            next_anim = self.animation_queue.pop(0)
            self.play_animation(
                next_anim["definition_id"],
                next_anim["source_id"],
                next_anim["target_ids"],
                next_anim["parameters"],
                next_anim["on_complete"]
            )
        
        return completed_count
    
    def get_active_animations(self) -> List[Dict[str, Any]]:
        """
        Get information about all currently active animations.
        
        Returns:
            List of dictionaries with animation instance data
        """
        return [instance.to_dict() for instance in self.active_animations.values()]
    
    def get_animation_definitions(self) -> List[Dict[str, Any]]:
        """
        Get all registered animation definitions.
        
        Returns:
            List of dictionaries with animation definition data
        """
        return [definition.to_dict() for definition in self.animation_definitions.values()]
    
    def get_animation_count(self) -> Dict[str, int]:
        """
        Get counts of active and queued animations.
        
        Returns:
            Dictionary with counts
        """
        return {
            "active": len(self.active_animations),
            "queued": len(self.animation_queue)
        }
    
    def set_global_speed_multiplier(self, multiplier: float) -> None:
        """
        Set the global animation speed multiplier.
        
        Args:
            multiplier: Speed multiplier (1.0 = normal speed)
        """
        self.animation_speed_multiplier = max(0.1, min(3.0, multiplier))
        logger.debug(f"Set global animation speed multiplier to {self.animation_speed_multiplier}")
    
    def play_action_animation(
        self,
        action_type: str,
        source_id: str,
        target_ids: List[str],
        action_parameters: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Play an appropriate animation for a combat action.
        
        Args:
            action_type: Type of action being performed
            source_id: ID of the character performing the action
            target_ids: IDs of target characters
            action_parameters: Additional parameters for the action
            
        Returns:
            ID of the created animation instance, or None if no animation played
        """
        action_parameters = action_parameters or {}
        animation_id = None
        animation_params = {}
        
        # Apply any global parameters
        animation_params["speed_multiplier"] = action_parameters.get("animation_speed", self.animation_speed_multiplier)
        
        # Map action types to appropriate animations
        if action_type == "melee_attack":
            weapon_type = action_parameters.get("weapon_type", "sword")
            
            if weapon_type in ["sword", "dagger"]:
                animation_id = "melee_slash"
            elif weapon_type in ["spear", "rapier"]:
                animation_id = "melee_stab"
            elif weapon_type in ["axe", "hammer", "mace"]:
                animation_id = "melee_smash"
            else:
                # Default to slash for unknown weapon types
                animation_id = "melee_slash"
                
            # Add weapon-specific parameters
            animation_params["weapon_type"] = weapon_type
            animation_params["damage_type"] = action_parameters.get("damage_type", "physical")
                
        elif action_type == "ranged_attack":
            weapon_type = action_parameters.get("weapon_type", "bow")
            
            if weapon_type in ["bow", "crossbow"]:
                animation_id = "ranged_arrow"
            else:
                animation_id = "ranged_throw"
                
            # Add projectile-specific parameters
            animation_params["projectile_type"] = weapon_type
            animation_params["damage_type"] = action_parameters.get("damage_type", "physical")
                
        elif action_type == "spell":
            spell_type = action_parameters.get("spell_type", "damage")
            element = action_parameters.get("element", "fire")
            
            if spell_type == "damage":
                if element == "fire":
                    animation_id = "spell_fireball"
                elif element == "lightning":
                    animation_id = "spell_lightning"
                else:
                    # Default to fireball for unknown elements
                    animation_id = "spell_fireball"
                    animation_params["element"] = element
            elif spell_type == "heal":
                animation_id = "spell_heal"
            else:
                # Default to a generic effect animation for other spell types
                animation_id = "effect_apply"
                animation_params["effect_type"] = spell_type
                
            # Add spell-specific parameters
            animation_params["spell_power"] = action_parameters.get("power", 1.0)
                
        elif action_type == "move":
            move_type = action_parameters.get("move_type", "walk")
            
            if move_type == "run":
                animation_id = "move_run"
            elif move_type == "teleport":
                animation_id = "move_teleport"
            else:
                animation_id = "move_walk"
                
            # Add movement-specific parameters
            animation_params["distance"] = action_parameters.get("distance", 1.0)
            animation_params["direction"] = action_parameters.get("direction", (1, 0, 0))
        
        # If we have a valid animation ID, play it
        if animation_id and animation_id in self.animation_definitions:
            return self.play_animation(
                animation_id,
                source_id,
                target_ids,
                animation_params
            )
        
        return None
    
    def play_reaction_animation(
        self,
        reaction_type: str,
        character_id: str,
        reaction_parameters: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Play a reaction animation for a character.
        
        Args:
            reaction_type: Type of reaction (hit, dodge, etc.)
            character_id: ID of the character reacting
            reaction_parameters: Additional parameters
            
        Returns:
            ID of the created animation instance, or None if no animation played
        """
        reaction_parameters = reaction_parameters or {}
        animation_id = None
        animation_params = {}
        
        # Apply any global parameters
        animation_params["speed_multiplier"] = reaction_parameters.get("animation_speed", self.animation_speed_multiplier)
        
        # Map reaction types to appropriate animations
        if reaction_type == "hit":
            animation_id = "react_hit"
            animation_params["hit_direction"] = reaction_parameters.get("hit_direction", (1, 0, 0))
            animation_params["hit_strength"] = reaction_parameters.get("hit_strength", 1.0)
            
        elif reaction_type == "dodge":
            animation_id = "react_dodge"
            animation_params["dodge_direction"] = reaction_parameters.get("dodge_direction", (-1, 0, 0))
            
        elif reaction_type in ["buff", "debuff"]:
            animation_id = "effect_apply"
            animation_params["effect_type"] = reaction_type
            animation_params["effect_name"] = reaction_parameters.get("effect_name", "Unknown")
        
        # If we have a valid animation ID, play it
        if animation_id and animation_id in self.animation_definitions:
            return self.play_animation(
                animation_id,
                None,
                [character_id],
                animation_params
            )
        
        return None

# Create a singleton instance for global access
combat_animation_system = CombatAnimationSystem() 