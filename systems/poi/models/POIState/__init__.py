"""Module initialization."""

# Import POIState enum using direct file loading to avoid circular imports
import sys
import importlib.util

# Load POIState directly from the models.py file 
spec = importlib.util.spec_from_file_location(
    "poi_models_module", 
    "/Users/Sharrone/Visual_DM/backend/systems/poi/models.py"
)
poi_models_module = importlib.util.module_from_spec(spec)
sys.modules["poi_models_direct"] = poi_models_module
spec.loader.exec_module(poi_models_module)
POIState = poi_models_module.POIState

__all__ = ["POIState"] 