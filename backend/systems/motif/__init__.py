"""
Motif System Module

This module provides a system for managing narrative motifs that influence the game world.
Motifs are recurring patterns or themes that affect various aspects of the world's behavior.
The system also includes chaos functionality for narrative disruption and unpredictability.
"""

# Export main models
from .models import (
    Motif, MotifCreate, MotifUpdate, MotifFilter,
    MotifScope, MotifLifecycle, MotifCategory, MotifEffect,
    LocationInfo
)

# Export the main manager class (primary interface)
from .manager import MotifManager

# Export the service and repository for direct access if needed
from .service import MotifService
from .repository import MotifRepository, Vector2

# Utility functions
from .utils import (
    generate_motif_name, generate_motif_description,
    estimate_motif_compatibility, generate_realistic_duration,
    motif_to_narrative_context, calculate_motif_spread,
    roll_chaos_event, NARRATIVE_CHAOS_TABLE
)

# Router
from .router import router as motif_router

# Convenience function to get manager instance
def get_motif_manager() -> MotifManager:
    """Get the singleton instance of the MotifManager."""
    return MotifManager.get_instance()

__all__ = [
    # Models
    'Motif', 'MotifCreate', 'MotifUpdate', 'MotifFilter',
    'MotifScope', 'MotifLifecycle', 'MotifCategory', 'MotifEffect',
    'LocationInfo',
    
    # Core components
    'MotifManager', 'MotifService', 'MotifRepository', 'Vector2',
    'get_motif_manager',
    
    # Utilities
    'generate_motif_name', 'generate_motif_description',
    'estimate_motif_compatibility', 'generate_realistic_duration',
    'motif_to_narrative_context', 'calculate_motif_spread',
    'roll_chaos_event', 'NARRATIVE_CHAOS_TABLE',
    
    # Router
    'motif_router'
]
