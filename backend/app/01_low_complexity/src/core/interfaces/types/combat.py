from typing import Any



class CombatState:
    accuracy: float
    damage: float
    defense: float
    criticalChance: float
    evasion?: float
    initiative?: float
    resistances?: {
    fire?: float
    ice?: float
    lightning?: float
    wind?: float
} 