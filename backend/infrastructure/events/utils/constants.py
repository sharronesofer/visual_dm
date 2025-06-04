"""Game constants and multipliers"""

# Difficulty multipliers
DIFFICULTY_MULTIPLIERS = {
    'easy': 0.8,
    'normal': 1.0,
    'hard': 1.5,
    'epic': 2.0
}

# Rarity multipliers
RARITY_MULTIPLIERS = {
    'common': 1.0,
    'uncommon': 1.5,
    'rare': 2.0,
    'epic': 3.0,
    'legendary': 5.0
}

# Rarity weights for random generation
RARITY_WEIGHTS = {
    'common': 0.6,
    'uncommon': 0.25,
    'rare': 0.1,
    'epic': 0.04,
    'legendary': 0.01
}

# Item type weights
ITEM_WEIGHTS = {
    'weapon': 0.3,
    'armor': 0.3,
    'accessory': 0.2,
    'consumable': 0.2
}

# Valid races
VALID_RACES = ['human', 'elf', 'dwarf', 'halfling']

# Valid archetypes (descriptive only, not mechanical classes)
VALID_ARCHETYPES = ['warrior', 'scholar', 'scout', 'mystic']

# Valid difficulties
VALID_DIFFICULTIES = ['easy', 'normal', 'hard', 'epic']

# Valid rarities
VALID_RARITIES = ['common', 'uncommon', 'rare', 'epic', 'legendary']

# Base values
BASE_XP = 100
BASE_GOLD = 50
BASE_DAMAGE = 10
BASE_HEALTH = 10

# Level scaling factors
LEVEL_SCALING = {
    'xp': 1.5,  # Exponential growth for XP
    'damage': 0.05,  # Linear scaling for damage
    'health': 0.1,  # Linear scaling for health
    'gold': 0.5,  # Linear scaling for gold
    'drop_chance': 0.05  # Linear scaling for drop chances
}

# Attribute limits
ATTRIBUTE_LIMITS = {
    'min': 3,
    'max': 18,
    'total': 72  # Point buy limit
}

# Quest time limits (in hours)
QUEST_TIME_LIMITS = {
    'hunt': 24,
    'gather': 48,
    'escort': 72,
    'investigate': 36
}

# Event durations (in hours)
EVENT_DURATIONS = {
    'natural': 24,
    'social': 48,
    'military': 72,
    'mystical': 36
}

# Size multipliers
SIZE_MULTIPLIERS = {
    'small': 0.5,
    'medium': 1.0,
    'large': 2.0
} 