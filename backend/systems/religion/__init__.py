"""
Religion System - Business Logic

This module contains the core business logic for the religion system.
Technical infrastructure components have been moved to backend.infrastructure.religion.
Now includes configuration-driven functionality for religion types, devotion calculations, and narrative generation.
"""

# Import business logic components
try:
    from .models import *
except ImportError:
    pass

try:
    from .services import *
except ImportError:
    pass

try:
    from .utils import *
except ImportError:
    pass

# Import configuration system
try:
    from .config import (
        RELIGION_TYPES,
        religion_config,
        narrative_templates,
        influence_rules, 
        practices_templates,
        get_religion_types,
        get_religion_type_info,
        get_devotion_modifiers,
        get_compatibility_factors,
        calculate_devotion_change,
        check_religion_compatibility,
        get_narrative_template,
        get_regional_modifier,
        get_practice_template,
        get_festival_template,
        reload_religion_config,
        validate_config
    )
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False

__all__ = [
    # Business Logic Models
    "ReligionEntity",
    "CreateReligionRequest", 
    "UpdateReligionRequest",
    "ReligionResponse",
    "ReligionListResponse",
    "ReligionMembership",
    "RELIGION_TYPES",
    
    # Business Logic Services
    "ReligionService",
    "get_religion_service",
    "ReligionNarrativeService",
    "get_religion_narrative_service",
    
    # Business Logic Utilities
    "generate_conversion_narrative",
    "generate_religion_event",
    "calculate_devotion_change",
    "check_religion_compatibility",
    "generate_devotion_narrative",
    "get_religion_type_info",
    "calculate_regional_influence",
    
    # Business Logic Exceptions
    "ReligionNotFoundError",
    "ReligionValidationError", 
    "ReligionConflictError",
]

# Add configuration exports if available
if HAS_CONFIG:
    __all__.extend([
        # Configuration System
        "religion_config",
        "narrative_templates", 
        "influence_rules",
        "practices_templates",
        "get_religion_types",
        "get_devotion_modifiers", 
        "get_compatibility_factors",
        "get_narrative_template",
        "get_regional_modifier",
        "get_practice_template",
        "get_festival_template",
        "reload_religion_config",
        "validate_config"
    ])
