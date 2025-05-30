from typing import Any


class CombatHandler {
  private grid: TacticalHexGrid
  private participants: Map<string, CombatParticipant>
  private environmentSystem: EnvironmentalInteractionSystem
  constructor(grid: TacticalHexGrid) {
    this.grid = grid
    this.participants = new Map()
    this.environmentSystem = new EnvironmentalInteractionSystem(grid)
  }
  addParticipant(participant: CombatParticipant): void {
    this.participants.set(participant.id, participant)
  }
  processTurn(): void {
    this.environmentSystem.processTurn()
    for (const participant of this.participants.values()) {
      const effects = this.environmentSystem.getEnvironmentalEffectsAtPosition(participant.position)
      for (const effect of effects) {
        participant.applyEffect(effect.type, effect.magnitude)
      }
    }
  }
  handleEnvironmentInteraction(participantId: str, objectId: str): bool {
    const participant = this.participants.get(participantId)
    if (!participant) return false
    return this.environmentSystem.interactWithObject(objectId, participant)
  }
  getAvailableInteractions(participantId: str): Array<{ id: str; type: str }> {
    const participant = this.participants.get(participantId)
    if (!participant) return []
    const interactionRange = 1 
    return this.environmentSystem.getInteractiveObjectsInRange(participant.position, interactionRange)
      .map(obj => ({ id: obj.id, type: obj.type }))
  }
} 