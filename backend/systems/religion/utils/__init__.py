"""Utils for religion system"""

# Import improved implementations from utils.py
from .utils import (
    generate_conversion_narrative,
    generate_religion_event,
    calculate_devotion_change,
    check_religion_compatibility,
    generate_devotion_narrative,
    get_religion_type_info,
    calculate_regional_influence
)

__all__ = [
    "generate_conversion_narrative",
    "generate_religion_event", 
    "calculate_devotion_change",
    "check_religion_compatibility",
    "generate_devotion_narrative",
    "get_religion_type_info",
    "calculate_regional_influence"
]

