# visual_client/core/config_creation.py

# Character Creation Constraints
MAX_FEATS = 7                 # Starting feats
LEVEL = 1                     # Starting level
MAX_BG_LENGTH = 10000         # Max length of background input
MAX_VISIBLE = 18              # Max items shown in scroll menus
STARTING_POINTS_POOL = 16     # Points available for stat assignment (if point-buy)

# Stat assignment range (before modifiers)
MIN_STAT_BASE = -2
MAX_STAT_BASE = 5

# Feat selection phases
FEAT_SELECTION_MODE = "categories"  # can also be "feats"
