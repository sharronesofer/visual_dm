"""
Visual Model for Character System
--------------------------------
Classes for managing the visual representation of characters, including meshes, 
materials, blend shapes (morph targets), and animations.

This module is part of the canonical backend.systems.character architecture and
provides the visual model functionality expected by the character system tests.
"""

from typing import Dict, Any, Optional, List

class MeshSlot:
    """
    Represents an attachment point for a swappable mesh (e.g., face, hair, armor piece).
    """
    def __init__(self, name: str, mesh_id: Optional[str] = None, compatible_types: Optional[List[str]] = None):
        self.name = name
        self.mesh_id = mesh_id
        self.compatible_types = compatible_types or []

    def is_compatible(self, mesh_type: str) -> bool:
        """Check if a mesh type can be attached to this slot."""
        return mesh_type in self.compatible_types or not self.compatible_types

class BlendShape:
    """
    Represents a blend shape (morph target) with a value.
    """
    def __init__(self, name: str, value: float = 0.0):
        self.name = name
        self.value = max(0.0, min(1.0, value))  # Clamp between 0 and 1

class MaterialAssignment:
    """
    Represents a material assigned to a specific slot/part of the model.
    """
    def __init__(self, slot: str, material_id: str, properties: Optional[Dict[str, Any]] = None):
        self.slot = slot
        self.material_id = material_id
        self.properties = properties or {}

class AnimationState:
    """
    Represents the state of an animation.
    """
    def __init__(self, animation_id: str, speed: float = 1.0, weight: float = 1.0, 
                 loop: bool = True, transition_time: float = 0.25):
        self.animation_id = animation_id
        self.speed = speed
        self.weight = weight
        self.loop = loop
        self.transition_time = transition_time
        self.is_playing = False

class CharacterModel:
    """
    Main class orchestrating mesh swapping, blend shape adjustment, and material application.
    Designed for integration with the Character ORM model in the character system.
    """
    def __init__(self, race: str, base_mesh: str, mesh_slots: Optional[Dict[str, MeshSlot]] = None,
                 blendshapes: Optional[Dict[str, BlendShape]] = None,
                 materials: Optional[Dict[str, MaterialAssignment]] = None,
                 animations: Optional[Dict[str, AnimationState]] = None,
                 scale: Optional[Dict[str, float]] = None):
        self.race = race
        self.base_mesh = base_mesh
        self.mesh_slots = mesh_slots or {}
        self.blendshapes = blendshapes or {}
        self.materials = materials or {}
        self.animations = animations or {}
        self.scale = scale or {"height": 1.0, "build": 0.5}
        self.current_animation = None

    def swap_mesh(self, slot_name: str, mesh_id: str):
        """Swap the mesh in a given slot."""
        if slot_name in self.mesh_slots:
            self.mesh_slots[slot_name].mesh_id = mesh_id
        else:
            self.mesh_slots[slot_name] = MeshSlot(slot_name, mesh_id)

    def set_blendshape(self, name: str, value: float):
        """Set the value of a blend shape (morph target)."""
        if name in self.blendshapes:
            self.blendshapes[name].value = value
        else:
            self.blendshapes[name] = BlendShape(name, value)

    def assign_material(self, slot: str, material_id: str, properties: Optional[Dict[str, Any]] = None):
        """Assign a material to a slot with optional properties."""
        self.materials[slot] = MaterialAssignment(slot, material_id, properties)

    def play_animation(self, animation_id: str, speed: float = 1.0, transition_time: float = 0.25):
        """Start playing an animation, transitioning from current animation if any."""
        if animation_id in self.animations:
            self.animations[animation_id].is_playing = True
            self.animations[animation_id].speed = speed
            self.animations[animation_id].transition_time = transition_time
            self.current_animation = animation_id
        else:
            self.animations[animation_id] = AnimationState(
                animation_id=animation_id,
                speed=speed,
                transition_time=transition_time
            )
            self.animations[animation_id].is_playing = True
            self.current_animation = animation_id

    def stop_animation(self, animation_id: Optional[str] = None):
        """Stop the specified animation or the current animation if none specified."""
        if animation_id is None and self.current_animation:
            animation_id = self.current_animation
            
        if animation_id and animation_id in self.animations:
            self.animations[animation_id].is_playing = False
            if self.current_animation == animation_id:
                self.current_animation = None

    def apply_preset(self, preset_data: Dict[str, Any]):
        """Apply a visual preset to the character model."""
        if "blendshapes" in preset_data:
            for name, value in preset_data["blendshapes"].items():
                self.set_blendshape(name, value)
        
        if "materials" in preset_data:
            for slot, material_data in preset_data["materials"].items():
                if isinstance(material_data, dict):
                    self.assign_material(slot, material_data.get("id", "default"), 
                                       material_data.get("properties", {}))
                else:
                    self.assign_material(slot, material_data)
        
        if "mesh_slots" in preset_data:
            for slot, mesh_id in preset_data["mesh_slots"].items():
                self.swap_mesh(slot, mesh_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the character model to a dictionary."""
        return {
            "race": self.race,
            "base_mesh": self.base_mesh,
            "mesh_slots": {k: v.mesh_id for k, v in self.mesh_slots.items()},
            "blendshapes": {k: v.value for k, v in self.blendshapes.items()},
            "materials": {k: v.material_id for k, v in self.materials.items()},
            "animations": {k: {
                "animation_id": v.animation_id,
                "speed": v.speed,
                "weight": v.weight,
                "loop": v.loop,
                "is_playing": v.is_playing
            } for k, v in self.animations.items()},
            "current_animation": self.current_animation,
            "scale": self.scale
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterModel':
        """Create a CharacterModel instance from a dictionary."""
        mesh_slots = {k: MeshSlot(k, v) for k, v in data.get("mesh_slots", {}).items()}
        blendshapes = {k: BlendShape(k, v) for k, v in data.get("blendshapes", {}).items()}
        materials = {k: MaterialAssignment(k, v) for k, v in data.get("materials", {}).items()}
        
        animations = {}
        for k, v in data.get("animations", {}).items():
            if isinstance(v, dict):
                animations[k] = AnimationState(
                    animation_id=v.get("animation_id", k),
                    speed=v.get("speed", 1.0),
                    weight=v.get("weight", 1.0),
                    loop=v.get("loop", True)
                )
                animations[k].is_playing = v.get("is_playing", False)
            else:
                animations[k] = AnimationState(animation_id=k)
        
        model = cls(
            race=data.get("race", "human"),
            base_mesh=data.get("base_mesh", "base_human"),
            mesh_slots=mesh_slots,
            blendshapes=blendshapes,
            materials=materials,
            animations=animations,
            scale=data.get("scale", {"height": 1.0, "build": 0.5})
        )
        
        model.current_animation = data.get("current_animation")
        return model

# Additional models for compatibility with existing visual system
class VisualModel:
    """Legacy compatibility class for VisualModel references."""

class Mesh:
    """Legacy compatibility class for Mesh references."""

class Material:
    """Legacy compatibility class for Material references."""

class Animation:
    """Legacy compatibility class for Animation references."""

__all__ = [
    'CharacterModel', 'MeshSlot', 'BlendShape', 'MaterialAssignment', 'AnimationState',
    'VisualModel', 'Mesh', 'Material', 'Animation'
] 