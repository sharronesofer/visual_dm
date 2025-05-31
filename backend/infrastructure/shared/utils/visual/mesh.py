from typing import Dict, Optional

class MeshLoader:
    """
    Utility class for loading and managing mesh assets.
    """
    def __init__(self):
        self.meshes: Dict[str, object] = {}  # Replace 'object' with actual mesh type as needed

    def load_mesh(self, mesh_id: str, mesh_data: object):
        """Load a mesh asset into the loader."""
        self.meshes[mesh_id] = mesh_data

    def get_mesh(self, mesh_id: str) -> Optional[object]:
        """Retrieve a mesh asset by its ID."""
        return self.meshes.get(mesh_id)

    def unload_mesh(self, mesh_id: str):
        """Remove a mesh asset from the loader."""
        if mesh_id in self.meshes:
            del self.meshes[mesh_id] 