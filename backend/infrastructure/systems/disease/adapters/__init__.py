"""
Disease System Cross-System Adapters

Adapters for integrating the disease system with other game systems
following the canonical pattern for cross-system communication.
"""

from .population_adapter import DiseasePopulationAdapter
from .region_adapter import DiseaseRegionAdapter

__all__ = [
    'DiseasePopulationAdapter',
    'DiseaseRegionAdapter'
] 