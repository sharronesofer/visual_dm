from typing import Any, List
from enum import Enum



class DungeonStructure:
    category: POICategory.DUNGEON
    difficulty: \'DifficultyRating\'
    requiredLevel: float
    rewards: List[RewardType]
class EnemyLair:
    type: BuildingType.ENEMY_LAIR
    enemyTypes: List[str]
    enemyCount: float
    bossPresent: bool
class PuzzleRoom:
    type: BuildingType.PUZZLE_ROOM
    puzzleType: \'PuzzleType\'
    solutionSteps: float
    timeLimit?: float
class TreasureChamber:
    type: BuildingType.TREASURE_CHAMBER
    treasureLevel: float
    guardianType?: str
    trapsCount: float
class TrapRoom:
    type: BuildingType.TRAP_ROOM
    trapTypes: List[TrapType]
    damageTypes: List[DamageType]
    difficultyClass: float
class DifficultyRating(Enum):
    EASY = 'EASY'
    MEDIUM = 'MEDIUM'
    HARD = 'HARD'
    DEADLY = 'DEADLY'
class PuzzleType(Enum):
    RIDDLE = 'RIDDLE'
    MECHANICAL = 'MECHANICAL'
    MAGICAL = 'MAGICAL'
    ENVIRONMENTAL = 'ENVIRONMENTAL'
    COMBINATION = 'COMBINATION'
class TrapType(Enum):
    PIT = 'PIT'
    ARROW = 'ARROW'
    POISON_GAS = 'POISON_GAS'
    MAGICAL = 'MAGICAL'
    CRUSHING = 'CRUSHING'
    FALLING = 'FALLING'
class DamageType(Enum):
    PHYSICAL = 'PHYSICAL'
    FIRE = 'FIRE'
    COLD = 'COLD'
    LIGHTNING = 'LIGHTNING'
    POISON = 'POISON'
    NECROTIC = 'NECROTIC'
class RewardType(Enum):
    GOLD = 'GOLD'
    ITEMS = 'ITEMS'
    EXPERIENCE = 'EXPERIENCE'
    RESOURCES = 'RESOURCES'
    REPUTATION = 'REPUTATION' 