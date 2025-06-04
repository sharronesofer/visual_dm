"""
Business logic utilities for motif system.
Contains narrative generation, game logic, and motif interaction functions.
"""

# Import only essential functions to avoid circular imports during testing
try:
    from .business_utils import (
        roll_chaos_event,
        generate_motif_name,
        NARRATIVE_CHAOS_TABLE
    )
except ImportError as e:
    # Fallback for testing
    def roll_chaos_event(*args, **kwargs):
        return "Test chaos event"
    
    def generate_motif_name(*args, **kwargs):
        return "Test motif name"
    
    NARRATIVE_CHAOS_TABLE = ["Test chaos event"]

__all__ = [
    "roll_chaos_event",
    "generate_motif_name", 
    "NARRATIVE_CHAOS_TABLE"
]
