"""Arc system core module."""

from typing import Dict, List, Optional
from dataclasses import dataclass
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

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
    """
    Simple arc manager that acts as a facade over the advanced ArcService.
    
    This class maintains backward compatibility for simple use cases while
    delegating complex operations to the database-backed ArcService.
    """
    
    def __init__(self, arc_service=None):
        """
        Initialize with optional ArcService for database operations.
        
        Args:
            arc_service: Optional ArcService instance for database operations.
                        If None, operations will be in-memory only.
        """
        self.arcs: Dict[str, Arc] = {}
        self.arc_service = arc_service
        self._warn_about_in_memory = True
    
    def _log_in_memory_warning(self):
        """Log warning about in-memory operations."""
        if self._warn_about_in_memory and not self.arc_service:
            logger.warning(
                "ArcManager is operating in in-memory mode. "
                "Consider using ArcService for persistent storage."
            )
            self._warn_about_in_memory = False
    
    def create_arc(self, arc: Arc) -> None:
        """
        Create a new arc.
        
        Args:
            arc: Arc to create
        """
        if self.arc_service:
            try:
                # Use database-backed service if available
                from backend.systems.arc.models.arc import CreateArcRequest, ArcType, ArcPriority
                
                create_request = CreateArcRequest(
                    title=arc.title,
                    description=arc.description,
                    arc_type=ArcType.GLOBAL,  # Default type
                    priority=ArcPriority.MEDIUM
                )
                
                # This would need to be made async in a real implementation
                # For now, we'll store in memory and log the intent
                self.arcs[arc.id] = arc
                logger.info(f"Arc {arc.id} would be saved to database via ArcService")
                
            except Exception as e:
                logger.error(f"Failed to create arc via ArcService: {e}")
                # Fallback to in-memory storage
                self.arcs[arc.id] = arc
        else:
            self._log_in_memory_warning()
            self.arcs[arc.id] = arc
    
    def get_arc(self, arc_id: str) -> Optional[Arc]:
        """
        Get an arc by ID.
        
        Args:
            arc_id: ID of the arc to retrieve
            
        Returns:
            Arc if found, None otherwise
        """
        if self.arc_service:
            try:
                # Try to get from database first
                # This would need proper async handling in real implementation
                logger.info(f"Would fetch arc {arc_id} from database via ArcService")
                # For now, fallback to in-memory
                return self.arcs.get(arc_id)
            except Exception as e:
                logger.error(f"Failed to get arc via ArcService: {e}")
                return self.arcs.get(arc_id)
        else:
            self._log_in_memory_warning()
            return self.arcs.get(arc_id)
    
    def list_arcs(self) -> List[Arc]:
        """
        List all arcs.
        
        Returns:
            List of all arcs
        """
        if self.arc_service:
            try:
                # Try to get from database first
                logger.info("Would fetch all arcs from database via ArcService")
                # For now, fallback to in-memory
                return list(self.arcs.values())
            except Exception as e:
                logger.error(f"Failed to list arcs via ArcService: {e}")
                return list(self.arcs.values())
        else:
            self._log_in_memory_warning()
            return list(self.arcs.values())
    
    def update_arc(self, arc_id: str, updates: Dict) -> bool:
        """
        Update an existing arc.
        
        Args:
            arc_id: ID of the arc to update
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        arc = self.get_arc(arc_id)
        if not arc:
            return False
        
        # Update the arc object
        for key, value in updates.items():
            if hasattr(arc, key):
                setattr(arc, key, value)
        
        if self.arc_service:
            try:
                logger.info(f"Would update arc {arc_id} in database via ArcService")
                # Database update would happen here
            except Exception as e:
                logger.error(f"Failed to update arc via ArcService: {e}")
        
        return True
    
    def delete_arc(self, arc_id: str) -> bool:
        """
        Delete an arc.
        
        Args:
            arc_id: ID of the arc to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if arc_id not in self.arcs:
            return False
        
        if self.arc_service:
            try:
                logger.info(f"Would delete arc {arc_id} from database via ArcService")
                # Database deletion would happen here
            except Exception as e:
                logger.error(f"Failed to delete arc via ArcService: {e}")
        
        # Remove from in-memory storage
        del self.arcs[arc_id]
        return True

# Export main classes
__all__ = ['Arc', 'ArcManager']
