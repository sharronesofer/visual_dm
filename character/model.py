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

class CharacterModel:
    """
    Main class orchestrating mesh swapping, blend shape adjustment, and material application.
    """
    def __init__(self, race: str, base_mesh: str, mesh_slots: Optional[Dict[str, MeshSlot]] = None,
                 blendshapes: Optional[Dict[str, BlendShape]] = None,
                 materials: Optional[Dict[str, MaterialAssignment]] = None,
                 scale: Optional[Dict[str, float]] = None):
        self.race = race
        self.base_mesh = base_mesh
        self.mesh_slots = mesh_slots or {}
        self.blendshapes = blendshapes or {}
        self.materials = materials or {}
        self.scale = scale or {"height": 1.0, "build": 0.5}

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

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the character model to a dictionary."""
        return {
            "race": self.race,
            "base_mesh": self.base_mesh,
            "mesh_slots": {k: v.mesh_id for k, v in self.mesh_slots.items()},
            "blendshapes": {k: v.value for k, v in self.blendshapes.items()},
            "materials": {k: v.material_id for k, v in self.materials.items()},
            "scale": self.scale
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterModel':
        mesh_slots = {k: MeshSlot(k, v) for k, v in data.get("mesh_slots", {}).items()}
        blendshapes = {k: BlendShape(k, v) for k, v in data.get("blendshapes", {}).items()}
        materials = {k: MaterialAssignment(k, v) for k, v in data.get("materials", {}).items()}
        return cls(
            race=data.get("race", "human"),
            base_mesh=data.get("base_mesh", "base_human"),
            mesh_slots=mesh_slots,
            blendshapes=blendshapes,
            materials=materials,
            scale=data.get("scale", {"height": 1.0, "build": 0.5})
        ) 