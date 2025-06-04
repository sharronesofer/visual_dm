"""Population API Infrastructure"""

from .router import router as population_router
from .demographic_router import router as demographic_router

__all__ = ["population_router", "demographic_router"]

