"""NPC System - Business Logic Components

This module contains the business logic components for the NPC system:
- Core business services and operations
- Business-specific utilities and helpers
- Domain logic and rules

Infrastructure components (models, routers, repositories, schemas, events) 
have been moved to backend.infrastructure.npc
"""

# Import business logic components
from . import services
from . import utils

# Import NPCService for compatibility
from .services.npc_service import NPCService

# Create alias for backward compatibility with quest system
NPCManager = NPCService

# Import infrastructure components from new location for backward compatibility
from backend.infrastructure.systems.npc.models.models import NpcEntity

# Create alias for backward compatibility
NPC = NpcEntity

# Re-export infrastructure components for backward compatibility
# This allows existing code to continue working while we update imports
from backend.infrastructure.systems.npc import (
    # Models
    NpcEntity, NpcMemory, NpcFactionAffiliation, NpcRumor,
    NpcLocationHistory, NpcMotif, CreateNpcRequest, 
    UpdateNpcRequest, NpcResponse, NpcListResponse,
    
    # Repositories  
    NPCRepository, NPCMemoryRepository, NPCLocationRepository,
    
    # Events
    get_npc_event_publisher
)

__all__ = [
    # Business Logic
    'services', 'utils', 'NPCService', 'NPCManager',
    
    # Backward Compatibility Aliases
    'NPC', 'NpcEntity',
    
    # Re-exported Infrastructure (for backward compatibility)
    'NpcMemory', 'NpcFactionAffiliation', 'NpcRumor',
    'NpcLocationHistory', 'NpcMotif', 'CreateNpcRequest', 
    'UpdateNpcRequest', 'NpcResponse', 'NpcListResponse',
    'NPCRepository', 'NPCMemoryRepository', 'NPCLocationRepository',
    'get_npc_event_publisher'
]
