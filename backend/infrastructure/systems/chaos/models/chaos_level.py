"""
Chaos Level Enumeration

Defines the chaos intensity levels used throughout the chaos system.
This is a data structure that belongs in the infrastructure layer.
"""

from enum import Enum

class ChaosLevel(Enum):
    """Chaos intensity levels with backward compatibility"""
    DORMANT = 0      # No chaos events
    STABLE = 1       # Very low chaos (alias for LOW for compatibility)
    LOW = 1          # Minor disturbances  
    MODERATE = 2     # Noticeable events
    HIGH = 3         # Significant disruption
    CRITICAL = 4     # Critical chaos (alias for EXTREME for compatibility)
    EXTREME = 4      # World-shaking events
    CATASTROPHIC = 5 # Reality-altering chaos 