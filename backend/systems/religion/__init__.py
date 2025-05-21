"""
Religion System: Manages religion entities, membership, and narrative hooks.

This module handles religion types, membership, narrative hooks, and integration
with faction and quest systems. It supports cross-faction membership and
narrative-driven mechanics.
"""

from .models import (
    Religion,
    ReligionType,
    ReligionMembership,
    religiontype_to_string,
    string_to_religiontype
)

from .schemas import (
    ReligionSchema,
    ReligionMembershipSchema,
    ReligionCreateSchema,
    ReligionUpdateSchema,
    ReligionMembershipCreateSchema
)

from .services import (
    ReligionService,
    get_religion_service
)

from .repository import ReligionRepository
from .membership_service import ReligionMembershipService
from .narrative_service import ReligionNarrativeService, get_narrative_service
from .faction_service import ReligionFactionService, get_faction_service

from .utils import (
    calculate_devotion_change,
    generate_conversion_narrative,
    generate_religion_event,
    calculate_religion_compatibility,
    calculate_schism_probability
)

__all__ = [
    # Models
    "Religion",
    "ReligionType",
    "ReligionMembership",
    "religiontype_to_string",
    "string_to_religiontype",
    
    # Schemas
    "ReligionSchema",
    "ReligionMembershipSchema",
    "ReligionCreateSchema",
    "ReligionUpdateSchema",
    "ReligionMembershipCreateSchema",
    
    # Services
    "ReligionService",
    "get_religion_service",
    "ReligionRepository",
    "ReligionMembershipService",
    "ReligionNarrativeService",
    "get_narrative_service",
    "ReligionFactionService",
    "get_faction_service",
    
    # Utils
    "calculate_devotion_change",
    "generate_conversion_narrative",
    "generate_religion_event",
    "calculate_religion_compatibility",
    "calculate_schism_probability"
]
