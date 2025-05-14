"""
Core enums used throughout the application.
"""

from enum import Enum, auto
from typing import Dict, List

class WorldType(str, Enum):
    """Types of game worlds."""
    FANTASY = "fantasy"
    SCIFI = "scifi"
    MODERN = "modern"
    HORROR = "horror"
    CUSTOM = "custom"

class CombatType(str, Enum):
    """Types of combat encounters."""
    MELEE = "melee"
    RANGED = "ranged"
    MIXED = "mixed"
    MAGICAL = "magical"
    STEALTH = "stealth"
    BOSS = "boss"

class TerrainType(str, Enum):
    """Types of terrain in the game world."""
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    SWAMP = "swamp"
    WATER = "water"
    URBAN = "urban"
    DUNGEON = "dungeon"

class WeatherType(Enum):
    CLEAR = auto()
    CLOUDY = auto()
    OVERCAST = auto()
    RAIN = auto()
    HEAVY_RAIN = auto()
    THUNDERSTORM = auto()
    SNOW = auto()
    BLIZZARD = auto()
    FOG = auto()
    HAIL = auto()
    
    @property
    def visibility_modifier(self) -> float:
        """Returns the visibility modifier (0-1) for this weather type."""
        modifiers = {
            WeatherType.CLEAR: 1.0,
            WeatherType.CLOUDY: 0.9,
            WeatherType.OVERCAST: 0.8,
            WeatherType.RAIN: 0.7,
            WeatherType.HEAVY_RAIN: 0.5,
            WeatherType.THUNDERSTORM: 0.3,
            WeatherType.SNOW: 0.6,
            WeatherType.BLIZZARD: 0.2,
            WeatherType.FOG: 0.4,
            WeatherType.HAIL: 0.6
        }
        return modifiers[self]
    
    @property
    def movement_speed_modifier(self) -> float:
        """Returns the movement speed modifier (0-1) for this weather type."""
        modifiers = {
            WeatherType.CLEAR: 1.0,
            WeatherType.CLOUDY: 1.0,
            WeatherType.OVERCAST: 1.0,
            WeatherType.RAIN: 0.8,
            WeatherType.HEAVY_RAIN: 0.6,
            WeatherType.THUNDERSTORM: 0.5,
            WeatherType.SNOW: 0.7,
            WeatherType.BLIZZARD: 0.4,
            WeatherType.FOG: 0.9,
            WeatherType.HAIL: 0.7
        }
        return modifiers[self]
    
    @property
    def combat_modifier(self) -> float:
        """Returns the combat effectiveness modifier (0-1) for this weather type."""
        modifiers = {
            WeatherType.CLEAR: 1.0,
            WeatherType.CLOUDY: 1.0,
            WeatherType.OVERCAST: 0.9,
            WeatherType.RAIN: 0.8,
            WeatherType.HEAVY_RAIN: 0.7,
            WeatherType.THUNDERSTORM: 0.6,
            WeatherType.SNOW: 0.8,
            WeatherType.BLIZZARD: 0.5,
            WeatherType.FOG: 0.7,
            WeatherType.HAIL: 0.7
        }
        return modifiers[self]

class WeatherIntensity(Enum):
    MILD = auto()
    MODERATE = auto()
    STRONG = auto()
    SEVERE = auto()
    
    @property
    def effect_multiplier(self) -> float:
        """Returns the multiplier for weather effects based on intensity."""
        multipliers = {
            WeatherIntensity.MILD: 0.5,
            WeatherIntensity.MODERATE: 1.0,
            WeatherIntensity.STRONG: 1.5,
            WeatherIntensity.SEVERE: 2.0
        }
        return multipliers[self]

class TimeOfDay(Enum):
    DAWN = auto()
    MORNING = auto()
    NOON = auto()
    AFTERNOON = auto()
    DUSK = auto()
    NIGHT = auto()

class Season(Enum):
    SPRING = auto()
    SUMMER = auto()
    FALL = auto()
    WINTER = auto()
    
    @property
    def next_season(self) -> 'Season':
        seasons = list(Season)
        current_index = seasons.index(self)
        next_index = (current_index + 1) % len(seasons)
        return seasons[next_index]
    
    @property
    def temperature_modifier(self) -> float:
        """Returns the base temperature modifier for this season."""
        modifiers = {
            Season.SPRING: 0.0,   # Neutral
            Season.SUMMER: 10.0,  # Warmer
            Season.FALL: 0.0,     # Neutral
            Season.WINTER: -10.0  # Colder
        }
        return modifiers[self]
    
    @property
    def precipitation_chance(self) -> float:
        """Returns the base precipitation chance (0-1) for this season."""
        chances = {
            Season.SPRING: 0.4,  # April showers
            Season.SUMMER: 0.2,  # Occasional storms
            Season.FALL: 0.3,    # Moderate rain
            Season.WINTER: 0.35  # Snow and sleet
        }
        return chances[self]

class QuestType(str, Enum):
    """Types of quests."""
    MAIN = "main"
    SIDE = "side"
    DAILY = "daily"
    REPEATABLE = "repeatable"
    HIDDEN = "hidden"
    EVENT = "event"

class QuestStatus(str, Enum):
    """Status of quests."""
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    HIDDEN = "hidden"

class NPCType(str, Enum):
    """Types of NPCs."""
    MERCHANT = "merchant"
    QUEST_GIVER = "quest_giver"
    GUARD = "guard"
    CIVILIAN = "civilian"
    ENEMY = "enemy"
    BOSS = "boss"
    COMPANION = "companion"

class ItemType(str, Enum):
    """Types of items."""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    QUEST = "quest"
    CRAFTING = "crafting"
    CURRENCY = "currency"
    KEY = "key"
    MISC = "misc"

class ItemRarity(str, Enum):
    """Rarity levels for items."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    UNIQUE = "unique"

class DamageType(str, Enum):
    """Types of damage."""
    PHYSICAL = "physical"
    MAGICAL = "magical"
    FIRE = "fire"
    ICE = "ice"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    DARK = "dark"

class StatusEffect(str, Enum):
    """Types of status effects."""
    POISON = "poison"
    BURN = "burn"
    FREEZE = "freeze"
    STUN = "stun"
    BLIND = "blind"
    SILENCE = "silence"
    HASTE = "haste"
    SLOW = "slow"
    INVISIBLE = "invisible"
    INVULNERABLE = "invulnerable"

class InfractionType(str, Enum):
    """Types of player infractions."""
    ATTACK_FRIENDLY_NPC = "attack_friendly_npc"
    THEFT = "theft"
    PROPERTY_DAMAGE = "property_damage"
    TRESPASSING = "trespassing"
    CHEATING = "cheating"
    EXPLOIT = "exploit"
    HARASSMENT = "harassment"
    OTHER = "other"

class InfractionSeverity(str, Enum):
    """Severity levels for infractions."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"

class ConsequenceType(str, Enum):
    """Types of consequences applied to players."""
    FINE = "fine"
    WARNING = "warning"
    ITEM_CONFISCATION = "item_confiscation"
    NPC_HOSTILITY = "npc_hostility"
    SUSPENSION = "suspension"
    BAN = "ban"
    BOUNTY = "bounty"
    OTHER = "other"

class NPCActivityType(Enum):
    IDLE = auto()
    WORKING = auto()
    SHOPPING = auto()
    EATING = auto()
    SLEEPING = auto()
    SOCIALIZING = auto()
    TRAVELING = auto()
    RECREATION = auto()
    MAINTENANCE = auto()
    EMERGENCY = auto()
    
    @property
    def energy_cost(self) -> float:
        """Energy cost per hour for this activity."""
        costs = {
            NPCActivityType.IDLE: 1.0,
            NPCActivityType.WORKING: 4.0,
            NPCActivityType.SHOPPING: 2.0,
            NPCActivityType.EATING: -3.0,  # Recovers energy
            NPCActivityType.SLEEPING: -5.0,  # Recovers energy
            NPCActivityType.SOCIALIZING: 2.0,
            NPCActivityType.TRAVELING: 3.0,
            NPCActivityType.RECREATION: 2.5,
            NPCActivityType.MAINTENANCE: 3.5,
            NPCActivityType.EMERGENCY: 5.0
        }
        return costs[self]
    
    @property
    def weather_sensitivity(self) -> float:
        """How much this activity is affected by bad weather (0-1)."""
        sensitivity = {
            NPCActivityType.IDLE: 0.2,
            NPCActivityType.WORKING: 0.4,
            NPCActivityType.SHOPPING: 0.7,
            NPCActivityType.EATING: 0.1,
            NPCActivityType.SLEEPING: 0.0,
            NPCActivityType.SOCIALIZING: 0.6,
            NPCActivityType.TRAVELING: 0.8,
            NPCActivityType.RECREATION: 0.9,
            NPCActivityType.MAINTENANCE: 0.5,
            NPCActivityType.EMERGENCY: 0.3
        }
        return sensitivity[self]

class NPCProfession(Enum):
    MERCHANT = auto()
    CRAFTSMAN = auto()
    GUARD = auto()
    FARMER = auto()
    SCHOLAR = auto()
    HEALER = auto()
    SERVANT = auto()
    NOBLE = auto()
    ENTERTAINER = auto()
    ADVENTURER = auto()
    
    @property
    def schedule_template(self) -> Dict[TimeOfDay, List[NPCActivityType]]:
        """Default schedule template for this profession."""
        templates = {
            NPCProfession.MERCHANT: {
                TimeOfDay.DAWN: [NPCActivityType.MAINTENANCE],
                TimeOfDay.MORNING: [NPCActivityType.WORKING],
                TimeOfDay.NOON: [NPCActivityType.EATING, NPCActivityType.WORKING],
                TimeOfDay.AFTERNOON: [NPCActivityType.WORKING],
                TimeOfDay.DUSK: [NPCActivityType.MAINTENANCE],
                TimeOfDay.NIGHT: [NPCActivityType.SLEEPING]
            },
            NPCProfession.CRAFTSMAN: {
                TimeOfDay.DAWN: [NPCActivityType.MAINTENANCE],
                TimeOfDay.MORNING: [NPCActivityType.WORKING],
                TimeOfDay.NOON: [NPCActivityType.EATING],
                TimeOfDay.AFTERNOON: [NPCActivityType.WORKING],
                TimeOfDay.DUSK: [NPCActivityType.SOCIALIZING],
                TimeOfDay.NIGHT: [NPCActivityType.SLEEPING]
            },
            NPCProfession.GUARD: {
                TimeOfDay.DAWN: [NPCActivityType.WORKING],
                TimeOfDay.MORNING: [NPCActivityType.WORKING],
                TimeOfDay.NOON: [NPCActivityType.EATING],
                TimeOfDay.AFTERNOON: [NPCActivityType.WORKING],
                TimeOfDay.DUSK: [NPCActivityType.WORKING],
                TimeOfDay.NIGHT: [NPCActivityType.SLEEPING]
            },
            NPCProfession.FARMER: {
                TimeOfDay.DAWN: [NPCActivityType.WORKING],
                TimeOfDay.MORNING: [NPCActivityType.WORKING],
                TimeOfDay.NOON: [NPCActivityType.EATING],
                TimeOfDay.AFTERNOON: [NPCActivityType.WORKING],
                TimeOfDay.DUSK: [NPCActivityType.MAINTENANCE],
                TimeOfDay.NIGHT: [NPCActivityType.SLEEPING]
            },
            NPCProfession.SCHOLAR: {
                TimeOfDay.DAWN: [NPCActivityType.WORKING],
                TimeOfDay.MORNING: [NPCActivityType.WORKING],
                TimeOfDay.NOON: [NPCActivityType.EATING],
                TimeOfDay.AFTERNOON: [NPCActivityType.WORKING],
                TimeOfDay.DUSK: [NPCActivityType.RECREATION],
                TimeOfDay.NIGHT: [NPCActivityType.SLEEPING]
            },
            NPCProfession.HEALER: {
                TimeOfDay.DAWN: [NPCActivityType.MAINTENANCE],
                TimeOfDay.MORNING: [NPCActivityType.WORKING],
                TimeOfDay.NOON: [NPCActivityType.EATING],
                TimeOfDay.AFTERNOON: [NPCActivityType.WORKING],
                TimeOfDay.DUSK: [NPCActivityType.WORKING],
                TimeOfDay.NIGHT: [NPCActivityType.SLEEPING]
            },
            NPCProfession.SERVANT: {
                TimeOfDay.DAWN: [NPCActivityType.WORKING],
                TimeOfDay.MORNING: [NPCActivityType.WORKING],
                TimeOfDay.NOON: [NPCActivityType.EATING],
                TimeOfDay.AFTERNOON: [NPCActivityType.WORKING],
                TimeOfDay.DUSK: [NPCActivityType.MAINTENANCE],
                TimeOfDay.NIGHT: [NPCActivityType.SLEEPING]
            },
            NPCProfession.NOBLE: {
                TimeOfDay.DAWN: [NPCActivityType.SLEEPING],
                TimeOfDay.MORNING: [NPCActivityType.RECREATION],
                TimeOfDay.NOON: [NPCActivityType.EATING, NPCActivityType.SOCIALIZING],
                TimeOfDay.AFTERNOON: [NPCActivityType.RECREATION],
                TimeOfDay.DUSK: [NPCActivityType.SOCIALIZING],
                TimeOfDay.NIGHT: [NPCActivityType.SLEEPING]
            },
            NPCProfession.ENTERTAINER: {
                TimeOfDay.DAWN: [NPCActivityType.SLEEPING],
                TimeOfDay.MORNING: [NPCActivityType.MAINTENANCE],
                TimeOfDay.NOON: [NPCActivityType.EATING, NPCActivityType.WORKING],
                TimeOfDay.AFTERNOON: [NPCActivityType.WORKING],
                TimeOfDay.DUSK: [NPCActivityType.WORKING],
                TimeOfDay.NIGHT: [NPCActivityType.WORKING]
            },
            NPCProfession.ADVENTURER: {
                TimeOfDay.DAWN: [NPCActivityType.MAINTENANCE],
                TimeOfDay.MORNING: [NPCActivityType.TRAVELING],
                TimeOfDay.NOON: [NPCActivityType.EATING],
                TimeOfDay.AFTERNOON: [NPCActivityType.TRAVELING],
                TimeOfDay.DUSK: [NPCActivityType.SOCIALIZING],
                TimeOfDay.NIGHT: [NPCActivityType.SLEEPING]
            }
        }
        return templates[self]

class NPCRelationshipType(Enum):
    STRANGER = auto()
    ACQUAINTANCE = auto()
    FRIEND = auto()
    CLOSE_FRIEND = auto()
    FAMILY = auto()
    RIVAL = auto()
    ENEMY = auto()
    
    @property
    def social_modifier(self) -> float:
        """Affects likelihood and quality of social interactions."""
        modifiers = {
            NPCRelationshipType.STRANGER: 0.0,
            NPCRelationshipType.ACQUAINTANCE: 0.2,
            NPCRelationshipType.FRIEND: 0.5,
            NPCRelationshipType.CLOSE_FRIEND: 0.8,
            NPCRelationshipType.FAMILY: 1.0,
            NPCRelationshipType.RIVAL: -0.3,
            NPCRelationshipType.ENEMY: -0.8
        }
        return modifiers[self] 