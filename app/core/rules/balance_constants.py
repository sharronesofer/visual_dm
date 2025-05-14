"""
Core quantitative game constants and formulas.
All numeric values and calculations should be defined here.
"""

# Character Progression
BASE_XP = 1000  # Base XP needed for first level
XP_SCALING_FACTOR = 1.5  # XP multiplier per level

# Default Classes
DEFAULT_CLASS = "fighter"
DEFAULT_SPELLCASTER_CLASS = "wizard"

XP_TABLE = {
    1: 0,
    2: 300,
    3: 900,
    4: 2700,
    5: 6500,
    6: 14000,
    7: 23000,
    8: 34000,
    9: 48000,
    10: 64000,
    11: 85000,
    12: 100000,
    13: 120000,
    14: 140000,
    15: 165000,
    16: 195000,
    17: 225000,
    18: 265000,
    19: 305000,
    20: 355000
}

# Character Creation
STARTING_FEATS = 1
FEATS_PER_LEVEL = 1
ABILITY_POINTS_PER_LEVEL = 2
MAX_ABILITY_SCORE = 20
MIN_ABILITY_SCORE = 3

# Hit Points and Mana
BASE_HIT_DIE = 8
BASE_MANA_DIE = 6
BOOSTED_MANA_DIE = "1d12"  # For characters with high Acuity

# Skill System
BASE_SKILL_POINTS_PER_LEVEL = 4
FIRST_LEVEL_SKILL_MULTIPLIER = 4
MAX_SKILL_RANK = "character_level + 3"

# Combat Constants
BASE_AC = 10
CRITICAL_HIT_MULTIPLIER = 2
CRITICAL_HIT_RANGE = 20
BASE_ATTACK_BONUS = 1
MAX_ATTACK_BONUS = 20

# Damage Calculations
BASE_WEAPON_DAMAGE = "1d8"
UNARMED_DAMAGE = "1d4"
CRITICAL_DAMAGE_MULTIPLIER = 2

# Status Effects
DEFAULT_STATUS_DURATION = 3
MAX_STATUS_STACKS = 5

# NPC Behavior
BASE_MORALE = 50
BASE_LOYALTY = 50
MORALE_THRESHOLD_LOW = 25
MORALE_THRESHOLD_MEDIUM = 50
LOYALTY_MORALE_MODIFIER = 4  # Loyalty reduces flee chance by loyalty//4

# Combat Behavior
FLEE_CHANCE_HP_LOW = 40
FLEE_CHANCE_HP_MEDIUM = 20
FLEE_CHANCE_ODDS_BAD = 20
FLEE_CHANCE_ODDS_POOR = 10
FLEE_CHANCE_MORALE_LOW = 30
FLEE_CHANCE_MORALE_MEDIUM = 15

# Action Economy
MAX_ACTION_SLOTS = {
    "action": 1,
    "bonus": 1,
    "movement": 1,
    "free": 0,
    "trigger": {
        "action": 1,
        "bonus": 1,
        "free": 1
    }
}

# World Mechanics
DEFAULT_REGION_LEVEL_RANGE = [1, 20]
DEFAULT_ENCOUNTER_RATE = 0.2
DEFAULT_RESTORE_RATE = 0.5  # HP/MP restored per rest

# Character limits
MAX_LEVEL = 20
MAX_SKILL_BONUS = 12
MAX_PROFICIENCY_BONUS = 6
MAX_INVENTORY_ITEMS = 100
MAX_SPELLS_KNOWN = 50
MAX_ACTIVE_QUESTS = 10

# Combat values
MAX_ADVANTAGE_BONUS = 5
MAX_DISADVANTAGE_PENALTY = -5
MAX_COMBAT_ROUNDS = 50

# Social values
MAX_RELATIONSHIP_VALUE = 100
MIN_RELATIONSHIP_VALUE = -100
RELATIONSHIP_CHANGE_STEP = 5
MAX_DIALOGUE_OPTIONS = 6
MAX_RUMOR_COUNT = 10

# World values
MAX_PARTY_SIZE = 6
MAX_REGION_LEVEL = 20
MAX_DISCOVERED_LOCATIONS = 1000
MAX_ACTIVE_EVENTS = 10
MAX_FACTION_COUNT = 50

# Quest values
MAX_QUEST_OBJECTIVES = 5
MAX_QUEST_REWARDS = 3
MAX_QUEST_CHAIN_LENGTH = 10
MAX_CONCURRENT_QUESTS = 5

# Item values
MAX_ITEM_STACK = 99
MAX_ITEM_BONUS = 5
MAX_ENCHANTMENT_LEVEL = 10
MAX_DURABILITY = 100

# Magic values
MAX_SPELL_LEVEL = 9
MAX_SPELL_SLOTS = 4
MAX_CONCENTRATION_DURATION = 600  # 10 minutes in seconds
MAX_SPELL_RANGE = 120  # feet

# Economy values
MAX_GOLD = 1000000
MAX_SHOP_INVENTORY = 50
SHOP_RESTOCK_INTERVAL = 24  # hours
MAX_TRADE_VALUE = 10000

# Time values
HOURS_PER_DAY = 24
DAYS_PER_MONTH = 30
MONTHS_PER_YEAR = 12
MAX_TIME_SKIP = 30  # days

# Performance limits
MAX_ENTITIES_PER_REGION = 100
MAX_PATHFINDING_DISTANCE = 50
MAX_AI_SEARCH_DEPTH = 3
MAX_PHYSICS_OBJECTS = 1000

# Skill System Constants
MAX_SKILLS_PER_CHARACTER = 8
SKILL_POINTS_PER_LEVEL = 2

# Class-specific Constants
CLASS_HIT_DICE = {
    "fighter": 10,
    "wizard": 6,
    "cleric": 8,
    "rogue": 8,
    "barbarian": 12,
    "bard": 8,
    "druid": 8,
    "monk": 8,
    "paladin": 10,
    "ranger": 10,
    "sorcerer": 6,
    "warlock": 8
}

CLASS_MANA_DICE = {
    "wizard": 6,
    "cleric": 8,
    "druid": 8,
    "bard": 8,
    "sorcerer": 6,
    "warlock": 8,
    "paladin": 8,
    "ranger": 8
}

# Economy Constants
STARTING_GOLD = 100
GOLD_PER_LEVEL = 50

# Character Stats
DEFAULT_ABILITY_SCORE = 10

# Experience Points
XP_PER_LEVEL = 1000  # Base XP needed for first level
XP_MULTIPLIER = 1.5  # XP multiplier per level

# Hit Points
DEFAULT_HIT_DIE = 8

# Mana Points
DEFAULT_MANA_DIE = 6

# Required Stats
REQUIRED_STATS = [
    "strength",
    "dexterity", 
    "constitution",
    "intelligence",
    "wisdom",
    "charisma"
]

# Level Caps
MIN_LEVEL = 1

# Ability Score Modifiers
def get_ability_modifier(score: int) -> int:
    """Calculate ability score modifier."""
    if score < MIN_ABILITY_SCORE:
        return -5
    return (score - 10) // 2

# New constants from the code block
BASE_HIT_POINTS = 10
BASE_MANA_POINTS = 5
STARTING_SKILL_POINTS = 4
MAX_TERRAIN_TYPES = 10
MAX_QUESTS_PER_ARC = 20
MAX_REWARD_ITEMS = 10
MAX_SAVES = 10
MAX_RELATIONSHIP_CHANGE = 20
MAX_GOLD_REWARD = 10000
MAX_XP_REWARD = 10000

CLASS_SPELLCASTING_ABILITY = {
    "wizard": "intelligence",
    "cleric": "wisdom",
    "druid": "wisdom",
    "bard": "charisma",
    "sorcerer": "charisma",
    "warlock": "charisma",
    "paladin": "charisma",
    "ranger": "wisdom"
}

CLASS_FEATURES = {
    "fighter": {
        "1": ["fighting_style", "second_wind"],
        "2": ["action_surge"],
        "3": ["martial_archetype"],
        "4": ["ability_score_improvement"],
        "5": ["extra_attack"],
        "6": ["ability_score_improvement"],
        "7": ["martial_archetype_feature"],
        "8": ["ability_score_improvement"],
        "9": ["indomitable"],
        "10": ["martial_archetype_feature"],
        "11": ["extra_attack_2"],
        "12": ["ability_score_improvement"],
        "13": ["indomitable_2"],
        "14": ["ability_score_improvement"],
        "15": ["martial_archetype_feature"],
        "16": ["ability_score_improvement"],
        "17": ["action_surge_2", "indomitable_3"],
        "18": ["martial_archetype_feature"],
        "19": ["ability_score_improvement"],
        "20": ["extra_attack_3"]
    }
}

# Base game balance constants

# Character/Enemy Level
MAX_LEVEL = 20  # Maximum level for characters and enemies
MIN_LEVEL = 1   # Minimum level for characters and enemies

# Combat Stats
BASE_AC = 10            # Base armor class before modifiers
BASE_ATTACK_BONUS = 0   # Base attack bonus before modifiers
BASE_HIT_DIE = 8        # Base hit die value (d8)
BASE_PROFICIENCY = 2    # Base proficiency bonus

# Critical Hit Rules
CRITICAL_HIT_MULTIPLIER = 2.0  # Damage multiplier on critical hits
CRITICAL_RANGE = 20           # Natural roll needed for critical hit

# Movement and Distance
BASE_MOVEMENT_SPEED = 30    # Base movement speed in feet per round
DIAGONAL_MOVEMENT_COST = 1.5  # Cost multiplier for diagonal movement
CLIMB_MOVEMENT_COST = 2.0   # Cost multiplier for climbing
SWIM_MOVEMENT_COST = 2.0    # Cost multiplier for swimming
JUMP_DISTANCE_MULTIPLIER = 0.5  # Multiplier for jump distance calculations

# Experience Points
XP_MULTIPLIER = 100     # Base XP multiplier per level
XP_DIFFICULTY = {       # XP multipliers for different difficulties
    'easy': 0.5,
    'medium': 1.0,
    'hard': 1.5,
    'deadly': 2.0
}

# Ability Score Limits
MIN_ABILITY_SCORE = 1
MAX_ABILITY_SCORE = 20
MAX_ENHANCED_ABILITY_SCORE = 30

# Vision and Light
BRIGHT_LIGHT_RADIUS = 60  # Radius in feet for bright light sources
DIM_LIGHT_RADIUS = 30    # Additional radius for dim light beyond bright
DARKVISION_RADIUS = 60   # Radius for darkvision (in dim light)

# Cover Bonuses
HALF_COVER_BONUS = 2     # AC and Dex save bonus for half cover
THREE_QUARTERS_COVER_BONUS = 5  # AC and Dex save bonus for 3/4 cover
FULL_COVER_BONUS = float('inf')  # Represents total cover

# Weather Effects
NORMAL_VISIBILITY = 1000  # Normal visibility range in feet
RAIN_VISIBILITY = 60     # Visibility in rain
HEAVY_RAIN_VISIBILITY = 30  # Visibility in heavy rain
FOG_VISIBILITY = 30      # Visibility in fog
HEAVY_FOG_VISIBILITY = 15   # Visibility in heavy fog
SNOW_VISIBILITY = 45     # Visibility in snow
STORM_VISIBILITY = 20    # Visibility in storm conditions 