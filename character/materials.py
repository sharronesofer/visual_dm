from typing import Dict, Any

class MaterialManager:
    """
    Manages material assignments and dynamic property changes for character customization.
    """
    def __init__(self):
        self.materials: Dict[str, Dict[str, Any]] = {}  # slot -> material properties

    def assign_material(self, slot: str, material_id: str, properties: Dict[str, Any]):
        """Assign a material with properties to a slot."""
        self.materials[slot] = {"material_id": material_id, **properties}

    def get_material(self, slot: str) -> Dict[str, Any]:
        """Get the material properties for a slot."""
        return self.materials.get(slot, {})

    def set_property(self, slot: str, prop: str, value: Any):
        """Set a property for a material slot."""
        if slot in self.materials:
            self.materials[slot][prop] = value 