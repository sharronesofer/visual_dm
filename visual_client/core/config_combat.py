# visual_client/core/config_combat.py

# Derived Stat Formulas (as notes for developers)
# HP = Level × (1d12 + CON)
# MP = Level × 1d8 + (INT × Level)
# DR = sum of armor DR + feat bonuses
# AC = 10 + DEX + feat bonuses

# Action economy rules
MAX_ACTIONS = 1
MAX_BONUS_ACTIONS = 1
MAX_MOVEMENT = 1
MAX_FREE_ACTIONS = 2
TRIGGERS_PER_TYPE = 1

# Critical rules
CRIT_THRESHOLD = 20
CRIT_MULTIPLIER = 2

# Advantage/disadvantage system
ADVANTAGE_STACKING = True  # Can be toggled to flatten multiple stacks

# Default skill/DC formulas
ATTRIBUTE_DC_BASE = 10
SKILL_DC_BASE = 10

# Default grid dimensions for tactical combat
COMBAT_GRID_WIDTH = 10
COMBAT_GRID_HEIGHT = 10
