"""NPC Infrastructure Components

This module contains all infrastructure-related components for the NPC system:
- Database models and entities
- Data repositories and access layer
- Request/response schemas
- Event publishing infrastructure

Note: Routers are not imported here to avoid circular dependencies.
They should be imported directly when needed.
"""

# Import infrastructure components (excluding routers to avoid circular imports)
from . import models
from . import repositories
from . import schemas
from . import events

# Export key infrastructure classes for easy access
from .models.models import (
    NpcEntity, NpcMemory, NpcFactionAffiliation, NpcRumor, 
    NpcLocationHistory, NpcMotif, CreateNpcRequest, 
    UpdateNpcRequest, NpcResponse, NpcListResponse
)

from .repositories.npc_repository import NPCRepository
from .repositories.npc_memory_repository import NPCMemoryRepository
from .repositories.npc_location_repository import NPCLocationRepository

from .events.event_publisher import get_npc_event_publisher

__all__ = [
    # Modules
    'models', 'repositories', 'schemas', 'events',
    
    # Models
    'NpcEntity', 'NpcMemory', 'NpcFactionAffiliation', 'NpcRumor',
    'NpcLocationHistory', 'NpcMotif', 'CreateNpcRequest', 
    'UpdateNpcRequest', 'NpcResponse', 'NpcListResponse',
    
    # Repositories
    'NPCRepository', 'NPCMemoryRepository', 'NPCLocationRepository',
    
    # Events
    'get_npc_event_publisher'
] 