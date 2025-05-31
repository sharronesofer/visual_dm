"""Arc system core module."""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Arc:
    """Narrative arc data model."""
    id: str
    title: str
    description: str
    status: str = "pending"
    steps: List[Dict] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'steps': self.steps
        }

class ArcManager:
    """Manages narrative arcs."""
    
    def __init__(self):
        self.arcs: Dict[str, Arc] = {}
    
    def create_arc(self, arc: Arc) -> None:
        """Create a new arc."""
        self.arcs[arc.id] = arc
    
    def get_arc(self, arc_id: str) -> Optional[Arc]:
        """Get an arc by ID."""
        return self.arcs.get(arc_id)
    
    def list_arcs(self) -> List[Arc]:
        """List all arcs."""
        return list(self.arcs.values())

# Export main classes
__all__ = ['Arc', 'ArcManager']
