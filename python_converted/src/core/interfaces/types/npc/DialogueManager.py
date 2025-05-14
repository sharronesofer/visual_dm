from typing import Any, List


class DialogueResponse:
    message: str
    tone: str
    emotionalState: str
    subtext?: str
    followUp?: List[str]
class DialogueManager:
    generateDialogue(
    npc: Any,
    context: Any
  ): Awaitable[DialogueResponse>
    generateResponse(
    npc: Any,
    input: str,
    context: Any
  ): Awaitable[DialogueResponse>
    generateEmotionalResponse(
    npc: Any,
    emotion: str,
    intensity: float,
    context: Any
  ): Awaitable[DialogueResponse>
    generateNegotiationResponse(
    npc: Any,
    offerQuality: float,
    context: Any
  ): Awaitable[DialogueResponse>
    generateDeceptionResponse(
    npc: Any,
    detected: bool,
    context: Any
  ): Awaitable[DialogueResponse>
    generateCooperationResponse(
    npc: Any,
    proposal: Any,
    context: Any
  ): Awaitable[DialogueResponse>
    generateCompetitionResponse(
    npc: Any,
    challenge: Any,
    context: Any
  ): Awaitable[DialogueResponse> 