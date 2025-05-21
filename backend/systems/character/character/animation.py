from typing import List

class AnimationManager:
    """
    Handles animation compatibility and binding for character models.
    """
    def __init__(self):
        self.animations: List[str] = []  # List of animation IDs or names

    def add_animation(self, animation_id: str):
        """Add an animation to the manager."""
        if animation_id not in self.animations:
            self.animations.append(animation_id)

    def remove_animation(self, animation_id: str):
        """Remove an animation from the manager."""
        if animation_id in self.animations:
            self.animations.remove(animation_id)

    def has_animation(self, animation_id: str) -> bool:
        """Check if an animation is available."""
        return animation_id in self.animations 