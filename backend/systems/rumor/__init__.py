"""
Rumor system package for tracking creation, spread, and mutation of rumors.

This package provides models, services, and API endpoints for managing
rumors within the system. It handles rumor creation, spread, mutation,
and decay according to the game's mechanics.
"""

# Core models
from backend.systems.rumor.models.rumor import (
    Rumor, 
    RumorVariant, 
    RumorSpread, 
    RumorCategory, 
    RumorSeverity,
    RumorEvent
)

# Export only the more robust implementations
from backend.systems.rumor.services.rumor_service import RumorService
from backend.systems.rumor.repositories.rumor_repository import RumorRepository
from backend.systems.rumor.transformer import RumorTransformer

# API schemas
from backend.systems.rumor.schemas import (
    CreateRumorRequest,
    SpreadRumorRequest,
    EntityRumorsRequest,
    DecayRumorsRequest,
    RumorResponse,
    RumorListResponse,
    EntityRumorsResponse,
    RumorOperationResponse,
    RumorSummaryResponse
)

# API endpoints
from backend.systems.rumor.api import router as rumor_router

# Utility functions
from backend.systems.rumor.decay_and_propagation import (
    calculate_rumor_decay,
    calculate_mutation_probability,
    calculate_spread_radius,
    calculate_believability_threshold
)

# Export canonical models and classes
__all__ = [
    # Models
    'Rumor', 'RumorVariant', 'RumorSpread', 'RumorCategory',
    'RumorSeverity', 'RumorEvent',
    
    # Service layer
    'RumorService',
    
    # Repository layer
    'RumorRepository',
    
    # API schemas
    'CreateRumorRequest', 'SpreadRumorRequest', 'EntityRumorsRequest',
    'DecayRumorsRequest', 'RumorResponse', 'RumorListResponse',
    'EntityRumorsResponse', 'RumorOperationResponse',
    'RumorSummaryResponse',
    
    # API router
    'rumor_router',
    
    # Utility functions
    'calculate_rumor_decay', 'calculate_mutation_probability',
    'calculate_spread_radius', 'calculate_believability_threshold'
] 