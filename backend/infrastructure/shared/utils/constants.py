"""
Shared constants for game mechanics.
"""

# Difficulty multipliers
DIFFICULTY_MULTIPLIERS = {
    'easy': 0.8,
    'normal': 1.0,
    'hard': 1.5,
    'epic': 2.0
}

# Level scaling factors
LEVEL_SCALING = {
    'xp': 1.5,  # Exponential growth for XP
    'damage': 0.05,  # Linear scaling for damage
    'health': 0.1,  # Linear scaling for health
    'gold': 0.5,  # Linear scaling for gold
    'drop_chance': 0.05  # Linear scaling for drop chances
}

# Base values
BASE_XP = 100
BASE_GOLD = 50
BASE_DAMAGE = 10
BASE_HEALTH = 10

# Attribute limits
ATTRIBUTE_LIMITS = {
    'min': 3,
    'max': 18,
    'total': 72  # Point buy limit
}

# Valid races
VALID_RACES = ['human', 'elf', 'dwarf', 'halfling']

# Note: This system uses ability-based progression, no traditional classes
# Valid character archetypes (optional descriptive labels only)
VALID_ARCHETYPES = ['martial', 'scholarly', 'stealthy', 'social']

# Valid difficulties
VALID_DIFFICULTIES = ['easy', 'normal', 'hard', 'epic']

# Valid backgrounds
VALID_BACKGROUNDS = ['noble', 'commoner', 'criminal', 'soldier', 'scholar']

# Valid attributes
VALID_ATTRIBUTES = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'] 