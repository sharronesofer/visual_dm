from typing import Any, List, Union


MonsterAttackDirection = Union[, 'north', 'northeast', 'southeast', 'south', 'southwest', 'northwest']
MonsterAttackOutcome = Union[, 'defended', 'close_defeat', 'decisive_defeat']
class MonsterAttack:
    id: str
    poiId: str
    direction: MonsterAttackDirection
    strength: float
    monsterTypes: List[str]
    timestamp: Date
    resolved: bool
    outcome?: MonsterAttackOutcome 