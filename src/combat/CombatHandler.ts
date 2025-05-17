import { TacticalHexGrid } from '../hexmap/TacticalHexGrid';
import { CombatParticipant } from './CombatParticipant';
import { EnvironmentalInteractionSystem } from './EnvironmentalInteractionSystem';
import { EventBus as CoreEventBus } from '../core/interfaces/types/events';
import { POIEvents } from '../poi/types/POIEvents';
import { TypedEventEmitter } from '../utils/TypedEventEmitter';

export class CombatHandler {
  private grid: TacticalHexGrid;
  private participants: Map<string, CombatParticipant>;
  private environmentSystem: EnvironmentalInteractionSystem;

  constructor(grid: TacticalHexGrid) {
    this.grid = grid;
    this.participants = new Map();
    this.environmentSystem = new EnvironmentalInteractionSystem(grid);

    // Use a typed EventBus for POI events
    const POIEventBus = CoreEventBus.getInstance() as TypedEventEmitter<POIEvents>;

    // Subscribe to POI evolution events for War system integration
    POIEventBus.on('poi:evolved', ({ poiId, poi, trigger, changes, version }) => {
      // Example: Log the event
      console.log(`[War Integration] POI evolved: ${poiId}, trigger: ${trigger}, changes:`, changes);
      // TODO: Update combat objectives, environmental effects, or battle outcomes based on evolved POI state
      // For example, if a POI becomes more fortified, adjust battle difficulty
    });
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