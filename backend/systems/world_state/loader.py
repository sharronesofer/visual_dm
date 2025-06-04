"""
World State Loader - Business Logic Interface

Simple interface for loading world state data that delegates to infrastructure.
"""

from typing import Dict, Any, Optional, List
from backend.infrastructure.systems.world_state.loaders.file_loader import WorldStateLoader as InfrastructureLoader


class WorldStateLoader:
    """Business logic interface for world state loading"""
    
    def __init__(self, data_dir: str = "data/systems/world_state"):
        self._infrastructure_loader = InfrastructureLoader(data_dir)
    
    def load_state(self) -> Dict[str, Any]:
        """Load the current world state"""
        return self._infrastructure_loader.load_state()
    
    def save_state(self, state: Dict[str, Any]) -> bool:
        """Save world state"""
        return self._infrastructure_loader.save_state(state) 