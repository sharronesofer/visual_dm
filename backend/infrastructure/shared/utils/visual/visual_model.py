"""
Visual Model
-----------
Classes for managing the visual representation of characters, including meshes, 
materials, blend shapes (morph targets), and animations.

This file consolidates visual model functionality from:
- character/character/model.py
- character/character/mesh.py
- character/character/materials.py
- character/character/blendshapes.py
- character/character/animation.py
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

class BlendShape:
    """
    Represents a morph target for facial/body feature adjustment.
    """
    def __init__(self, name: str, value: float = 0.0):
        self.name = name
        self.value = value

class MaterialAssignment:
    """
    Handles dynamic material property assignment and texture mapping.
    """
    def __init__(self, slot: str, material_id: str, properties: Optional[Dict[str, Any]] = None):
        self.slot = slot
        self.material_id = material_id
        self.properties = properties or {}

class AnimationState:
    """
    Manages the current animation state of a character.
    """
    def __init__(self, animation_id: str, speed: float = 1.0, weight: float = 1.0, 
                 loop: bool = True, transition_time: float = 0.25):
        self.animation_id = animation_id
        self.speed = speed
        self.weight = weight
        self.loop = loop
        self.transition_time = transition_time
        self.time = 0.0
        self.is_playing = False

class CharacterModel:
    """
    Main class orchestrating mesh swapping, blend shape adjustment, and material application.
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

    def apply_preset(self, preset_data: Dict[str, Any]):
        """Apply a preset to the character model, updating multiple aspects at once."""
        if "mesh_slots" in preset_data:
            for slot, mesh_id in preset_data["mesh_slots"].items():
                self.swap_mesh(slot, mesh_id)
                
        if "blendshapes" in preset_data:
            for name, value in preset_data["blendshapes"].items():
                self.set_blendshape(name, value)
                
        if "materials" in preset_data:
            for slot, material_data in preset_data["materials"].items():
                if isinstance(material_data, dict) and "id" in material_data:
                    self.assign_material(slot, material_data["id"], material_data.get("properties"))
                else:
                    self.assign_material(slot, material_data)
                    
        if "scale" in preset_data:
            self.scale.update(preset_data["scale"])

    def randomize(self, constraints: Optional[Dict[str, Any]] = None):
        """Randomize character appearance within optional constraints."""
        from random import random, choice, uniform
        
        constraints = constraints or {}
        
        # Randomize blendshapes within constraints
        if "blendshapes" not in constraints:
            for name in self.blendshapes:
                self.blendshapes[name].value = uniform(0.0, 1.0)
        else:
            for name, range_data in constraints.get("blendshapes", {}).items():
                if name in self.blendshapes:
                    min_val = range_data.get("min", 0.0)
                    max_val = range_data.get("max", 1.0)
                    self.blendshapes[name].value = uniform(min_val, max_val)
        
        # TODO: Implement randomization for meshes, materials, and other aspects
        # This would require access to available options which would typically
        # come from a repository of available assets 