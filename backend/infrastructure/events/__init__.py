"""Events system - Infrastructure component for cross-cutting event concerns"""

# Auto-generated imports
from . import events
from . import models
from . import repositories
from . import routers
from . import schemas
from . import services
from . import utils

# Canonical exports for proper import resolution
from .services.event_dispatcher import EventDispatcher
from .events.canonical_events import EventBase
from .events.event_types import *

# Export key components for canonical imports
__all__ = [
    "EventDispatcher", 
    "EventBase",
    "events",
    "models", 
    "repositories",
    "routers",
    "schemas", 
    "services",
    "utils"
]

# Backward compatibility for systems expecting the old import path
event_dispatcher = EventDispatcher
