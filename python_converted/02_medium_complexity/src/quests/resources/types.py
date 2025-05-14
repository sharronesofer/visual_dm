from typing import Any, Dict, Union



/**
 * Represents a resource requirement for a quest
 */
class QuestResource:
    id: str
    name: str
    amount: float
    type: Union['ITEM', 'CURRENCY', 'MATERIAL']
    description?: str
/**
 * Represents an environmental or state condition for a quest
 */
class QuestCondition:
    type: Union['WEATHER', 'TIME', 'SEASON', 'FACTION_STATE', 'WORLD_STATE']
    value: Union[str, float, bool]
    description?: str
    customData?: Dict[str, Any> 