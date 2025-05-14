from typing import Any, Dict, List



class ReputationChange:
    value: float
    reason: str
    timestamp: float
class ReputationSystem:
    processInteractionReputation(
    npcId: str,
    targetId: str,
    result: InteractionResult
  ): Awaitable[float>
    calculateBaseReputation(result: InteractionResult): float
    applyInteractionModifiers(baseChange: float, result: InteractionResult): float
    recordReputationChange(
    npcId: str,
    targetId: str,
    value: float,
    result: InteractionResult
  ): None
    generateChangeReason(result: InteractionResult): str
    getReputationHistory(npcId: List[str, targetId: str): ReputationChange]
    getAggregateReputation(npcId: str, targetId: str): float
    updateReputation(
    npcId: str,
    change: float,
    context: Any
  ): Awaitable[None>
    getReputation(
    npcId: str,
    groupId?: str
  ): Awaitable[float>
    calculateReputationChange(
    baseChange: float,
    context: Any
  ): float
    decayReputation(
    npcId: str,
    timePassed: float
  ): Awaitable[None>
    getReputationHistory(
    npcId: str,
    timeRange: Dict[str, Any][]>
} 