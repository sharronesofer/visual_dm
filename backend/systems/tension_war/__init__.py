"""Tension_War system"""

# Auto-generated imports
from . import events
from . import models
from . import repositories
from . import schemas
from . import services
from . import utils

# Conditional import for routers (they have external dependencies)
try:
    from . import routers
except ImportError:
    # Routers may have dependencies that aren't available in all contexts
    pass
