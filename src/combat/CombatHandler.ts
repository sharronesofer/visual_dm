import { TacticalHexGrid } from '../hexmap/TacticalHexGrid';
import { CombatParticipant } from './CombatParticipant';
import { EnvironmentalInteractionSystem } from './EnvironmentalInteractionSystem';

export class CombatHandler {
  private grid: TacticalHexGrid;
  private participants: Map<string, CombatParticipant>;
  private environmentSystem: EnvironmentalInteractionSystem;

  constructor(grid: TacticalHexGrid) {
    this.grid = grid;
    this.participants = new Map();
    this.environmentSystem = new EnvironmentalInteractionSystem(grid);
  }

  // Add a participant to combat
  addParticipant(participant: CombatParticipant): void {
    this.participants.set(participant.id, participant);
  }

  // Process a combat turn
  processTurn(): void {
    // Process environmental effects first
    this.environmentSystem.processTurn();

    // Apply environmental effects to all participants
    for (const participant of this.participants.values()) {
      const effects = this.environmentSystem.getEnvironmentalEffectsAtPosition(participant.position);
      for (const effect of effects) {
        participant.applyEffect(effect.type, effect.magnitude);
      }
    }
  }

  // Handle participant interaction with environment
  handleEnvironmentInteraction(participantId: string, objectId: string): boolean {
    const participant = this.participants.get(participantId);
    if (!participant) return false;

    return this.environmentSystem.interactWithObject(objectId, participant);
  }

  // Get interactive objects available to a participant
  getAvailableInteractions(participantId: string): Array<{ id: string; type: string }> {
    const participant = this.participants.get(participantId);
    if (!participant) return [];

    const interactionRange = 1; // Base interaction range
    return this.environmentSystem.getInteractiveObjectsInRange(participant.position, interactionRange)
      .map(obj => ({ id: obj.id, type: obj.type }));
  }
} 