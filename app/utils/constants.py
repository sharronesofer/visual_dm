# Game Constants
BASE_ENERGY_RECOVERY = 1.0
MAX_ENERGY = 100
MIN_ENERGY_FOR_ACTIVITY = 10
RELATIONSHIP_DECAY_RATE = 0.01
RELATIONSHIP_IMPROVEMENT_RATE = 0.02
MAX_LEVEL = 20
MAX_ATTRIBUTE = 20
MIN_ATTRIBUTE = 3
MAX_SKILL_RANK = 20
MAX_FEATS = 7

# Experience Constants
XP_PER_LEVEL = {
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

# Alignment Constants
ALIGNMENTS = [
    "Lawful Good",
    "Neutral Good",
    "Chaotic Good",
    "Lawful Neutral",
    "True Neutral",
    "Chaotic Neutral",
    "Lawful Evil",
    "Neutral Evil",
    "Chaotic Evil"
]

# Difficulty Constants
DIFFICULTY_MULTIPLIERS = {
    "trivial": 0.5,
    "easy": 0.75,
    "normal": 1.0,
    "hard": 1.5,
    "very_hard": 2.0,
    "extreme": 3.0
}

# Combat Constants
COMBAT_ROUNDS_PER_TURN = 1
MAX_ACTIONS_PER_TURN = 3
REACTION_LIMIT_PER_ROUND = 1

# Time Constants
SECONDS_PER_ROUND = 6
ROUNDS_PER_MINUTE = 10
MINUTES_PER_HOUR = 60
HOURS_PER_DAY = 24
DAYS_PER_WEEK = 7
DAYS_PER_SEASON = 91  # Approximately 3 months

# Time of day periods (hours)
DAWN_START = 5
MORNING_START = 8
NOON_START = 12
AFTERNOON_START = 14
DUSK_START = 18
NIGHT_START = 21

# Season temperature ranges (°C)
SPRING_TEMP_RANGE = (10, 20)
SUMMER_TEMP_RANGE = (20, 30)
FALL_TEMP_RANGE = (10, 20)
WINTER_TEMP_RANGE = (-5, 10)

# Weather transition thresholds
WEATHER_CHANGE_THRESHOLD = 0.7  # Probability threshold for weather changes
MIN_WEATHER_DURATION = 3600  # Minimum duration of weather condition in seconds
MAX_WEATHER_DURATION = 14400  # Maximum duration of weather condition in seconds

# Environmental constants
BASE_TEMPERATURE = 20  # Base temperature in °C
BASE_HUMIDITY = 0.5   # Base humidity (0-1)
BASE_WIND_SPEED = 5   # Base wind speed in km/h
BASE_VISIBILITY = 1000  # Base visibility in meters

# Resource Constants
MAX_INVENTORY_WEIGHT = 50  # in pounds
CARRY_CAPACITY_MULTIPLIER = 15  # Strength score × this = carry capacity
COIN_WEIGHT = 0.02  # Weight of one coin in pounds

# Rest Constants
SHORT_REST_MINUTES = 60
LONG_REST_HOURS = 8
MAX_HIT_DICE = 20

# Weather Constants
WEATHER_TYPES = ["clear", "cloudy", "rain", "storm", "snow", "fog"]
WEATHER_EFFECTS = {
    "clear": 1.0,
    "cloudy": 0.9,
    "rain": 0.75,
    "storm": 0.5,
    "snow": 0.6,
    "fog": 0.7
}

# Quest Constants
QUEST_TYPES = [
    "main",
    "side",
    "daily",
    "weekly",
    "special",
    "hidden"
]

QUEST_STATUSES = [
    "not_started",
    "in_progress",
    "completed",
    "failed",
    "expired",
    "abandoned"
]

QUEST_TIME_LIMITS = {
    "main": None,  # No time limit
    "side": 7 * DAYS_PER_WEEK * HOURS_PER_DAY,  # 7 days in hours
    "daily": HOURS_PER_DAY,  # 24 hours
    "weekly": 7 * HOURS_PER_DAY,  # 7 days in hours
    "special": 3 * DAYS_PER_WEEK * HOURS_PER_DAY,  # 3 days in hours
    "hidden": None  # No time limit
}

QUEST_REWARDS = {
    "main": {
        "xp_multiplier": 2.0,
        "gold_multiplier": 2.0,
        "reputation_multiplier": 2.0
    },
    "side": {
        "xp_multiplier": 1.0,
        "gold_multiplier": 1.0,
        "reputation_multiplier": 1.0
    },
    "daily": {
        "xp_multiplier": 0.5,
        "gold_multiplier": 0.5,
        "reputation_multiplier": 0.5
    },
    "weekly": {
        "xp_multiplier": 1.5,
        "gold_multiplier": 1.5,
        "reputation_multiplier": 1.5
    },
    "special": {
        "xp_multiplier": 3.0,
        "gold_multiplier": 3.0,
        "reputation_multiplier": 3.0
    },
    "hidden": {
        "xp_multiplier": 4.0,
        "gold_multiplier": 4.0,
        "reputation_multiplier": 4.0
    }
}

# Quest Difficulty Scaling
QUEST_LEVEL_RANGE = {
    "trivial": -4,
    "easy": -2,
    "normal": 0,
    "hard": 2,
    "very_hard": 4,
    "extreme": 6
}

# Event Constants
EVENT_TYPES = [
    "combat",
    "social",
    "exploration",
    "puzzle",
    "rest",
    "travel",
    "shopping",
    "crafting",
    "training",
    "festival",
    "quest",
    "random"
]

EVENT_PRIORITIES = {
    "low": 0,
    "normal": 1,
    "high": 2,
    "critical": 3
}

EVENT_DURATIONS = {
    "instant": 0,
    "very_short": MINUTES_PER_HOUR // 4,  # 15 minutes
    "short": MINUTES_PER_HOUR,  # 1 hour
    "medium": 4 * MINUTES_PER_HOUR,  # 4 hours
    "long": 8 * MINUTES_PER_HOUR,  # 8 hours
    "very_long": HOURS_PER_DAY,  # 24 hours
    "extended": 3 * HOURS_PER_DAY,  # 3 days
    "permanent": -1  # No expiration
}

EVENT_STATUSES = [
    "pending",
    "active",
    "completed",
    "failed",
    "expired",
    "cancelled"
]

EVENT_TRIGGERS = {
    "time": "Triggered at specific time",
    "location": "Triggered at specific location",
    "quest": "Triggered by quest progress",
    "level": "Triggered by character level",
    "reputation": "Triggered by reputation change",
    "item": "Triggered by item acquisition",
    "combat": "Triggered during combat",
    "rest": "Triggered during rest",
    "random": "Triggered randomly",
    "weather": "Triggered by weather conditions",
    "player_choice": "Triggered by player decisions",
    "npc_interaction": "Triggered by NPC interaction"
}

EVENT_EFFECTS = {
    "none": 0.0,
    "minor": 0.25,
    "moderate": 0.5,
    "major": 1.0,
    "severe": 2.0,
    "extreme": 4.0
}

# Size Constants
SIZE_CATEGORIES = [
    "tiny",
    "small",
    "medium",
    "large",
    "huge",
    "gargantuan"
]

SIZE_MULTIPLIERS = {
    "tiny": 0.5,
    "small": 0.75,
    "medium": 1.0,
    "large": 2.0,
    "huge": 4.0,
    "gargantuan": 8.0
}

SIZE_SPACE = {
    "tiny": 2.5,  # feet
    "small": 5.0,
    "medium": 5.0,
    "large": 10.0,
    "huge": 15.0,
    "gargantuan": 20.0
}

SIZE_REACH = {
    "tiny": 0,  # feet
    "small": 5,
    "medium": 5,
    "large": 10,
    "huge": 15,
    "gargantuan": 20
}

SIZE_CARRYING_CAPACITY = {
    "tiny": 0.5,
    "small": 0.75,
    "medium": 1.0,
    "large": 2.0,
    "huge": 4.0,
    "gargantuan": 8.0
}

SIZE_HIT_DIE_MODIFIER = {
    "tiny": -2,
    "small": -1,
    "medium": 0,
    "large": 1,
    "huge": 2,
    "gargantuan": 4
} 