"""
Religion Infrastructure Module

This module contains all technical infrastructure components for the religion system,
including API routers, data repositories, schemas, event handling, WebSocket management,
and configuration loading.

Business logic remains in backend.systems.religion.
"""

# Re-export key infrastructure components (excluding routers to avoid circular imports)
from .repositories import *
from .schemas import *
from .events import *
from .websocket import *
from .config_loader import *

__all__ = [
    # Repositories
    "ReligionRepository",
    "get_religion_repository",
    
    # Schemas
    "ReligionSchema",
    "ReligionCreateSchema", 
    "ReligionUpdateSchema",
    "ReligionMembershipSchema",
    "ReligionMembershipCreateSchema",
    
    # Events
    "ReligionEventPublisher",
    "get_religion_event_publisher",
    "religion_events",
    
    # WebSocket
    "ReligionWebSocketManager",
    "religion_websocket_manager",
    
    # Configuration Loading
    "load_religion_config",
    "reload_all_religion_configs",
    "validate_religion_config",
    "format_narrative_template",
    "select_random_template",
] 