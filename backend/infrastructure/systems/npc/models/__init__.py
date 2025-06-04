"""NPC Models

Database models and Pydantic schemas for the NPC system.
"""

from .models import (
    # SQLAlchemy Models
    NpcEntity, NpcMemory, NpcFactionAffiliation, NpcRumor,
    NpcLocationHistory, NpcMotif,
    
    # Pydantic Models
    NpcBaseModel, NpcModel,
    
    # Request/Response Models
    CreateNpcRequest, UpdateNpcRequest, NpcResponse, NpcListResponse,
    MemoryResponse, FactionAffiliationResponse, RumorResponse, MotifResponse
)

from .barter_types import ItemTier, BarterValidationResult

__all__ = [
    # SQLAlchemy Models
    'NpcEntity', 'NpcMemory', 'NpcFactionAffiliation', 'NpcRumor',
    'NpcLocationHistory', 'NpcMotif',
    
    # Pydantic Models
    'NpcBaseModel', 'NpcModel',
    
    # Request/Response Models
    'CreateNpcRequest', 'UpdateNpcRequest', 'NpcResponse', 'NpcListResponse',
    'MemoryResponse', 'FactionAffiliationResponse', 'RumorResponse', 'MotifResponse',
    
    # Barter Types
    'ItemTier', 'BarterValidationResult'
]
