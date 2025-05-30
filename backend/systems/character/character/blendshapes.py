from typing import Dict

class BlendShapeManager:
    """
    Manages blend shape (morph target) values for a character.
    """
    def __init__(self):
        self.blendshapes: Dict[str, float] = {}

    def set_blendshape(self, name: str, value: float):
        """Set the value of a blend shape."""
        self.blendshapes[name] = value

    def get_blendshape(self, name: str) -> float:
        """Get the value of a blend shape."""
        return self.blendshapes.get(name, 0.0)

    def reset_blendshapes(self):
        """Reset all blend shapes to default (0.0)."""
        for k in self.blendshapes:
            self.blendshapes[k] = 0.0 