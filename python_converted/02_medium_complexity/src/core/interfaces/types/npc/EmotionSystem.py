from typing import Any, Dict, List



class EmotionalState:
    primary: str
    intensity: float
    secondary?: List[str]
    triggers: Dict[str, Any]
class EmotionSystem:
    getCurrentEmotionalState(npcId: str): Awaitable[str>
    updateEmotionalState(
    npcId: str,
    trigger: str,
    intensity: float,
    context?: Any
  ): Awaitable[EmotionalState>
    getEmotionalResponse(
    npcId: str,
    stimulus: str,
    intensity: float
  ): Awaitable[{
    response: str
    intensity: float>
  calculateEmotionalImpact(
    baseEmotion: str,
    personality: Any,
    context: Any
  ): Promise<number>
} 