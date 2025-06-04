"""Models for religion system"""

# Auto-generated imports
from .models import *

# Simple religion type constants (no complex enum needed)
# These can be imported from the config if needed, but string values work fine
RELIGION_TYPES = [
    "monotheistic",
    "polytheistic", 
    "animistic",
    "dualistic",
    "ancestor_worship",
    "cult",
    "sect",
    "folk",
    "state",
    "ancient",
    "emergent"
]

# Aliases for backward compatibility and expected imports
Religion = ReligionModel
ReligionMembership = ReligionMembershipEntity  # Use the proper SQLAlchemy entity

# Export the corrected types
__all__ = [
    'ReligionModel',
    'ReligionEntity', 
    'CreateReligionRequest',
    'UpdateReligionRequest',
    'ReligionResponse',
    'ReligionListResponse',
    'Religion',
    'ReligionMembership',
    'ReligionMembershipEntity',
    'RegionalInfluenceEntity',
    'RELIGION_TYPES'
]
