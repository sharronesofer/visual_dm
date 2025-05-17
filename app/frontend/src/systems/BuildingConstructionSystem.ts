/**
 * Helper to emit a construction request event using the event bus.
 *
 * Usage:
 *   BuildingConstructionSystem.emitConstructionRequest({ ... });
 */
import { EventBus } from '../core/interfaces/types/events';
import { ConstructionRequest } from './ConstructionRequestSystem';
import { BuildingStructure } from '../core/interfaces/types/building';
import { Position } from '../core/interfaces/types/common';

export class BuildingConstructionSystem {
    // ... existing code ...

    /**
     * Emit a construction request event for the event-driven system
     */
    static emitConstructionRequest(event: {
        request: ConstructionRequest;
        structure: BuildingStructure;
        player: import('../core/interfaces/types/player').PlayerState;
        resourceCheck: (player: import('../core/interfaces/types/player').PlayerState, resources: Record<string, number>) => boolean;
        permissionCheck: (player: import('../core/interfaces/types/player').PlayerState, position: Position) => boolean;
    }) {
        const bus = EventBus.getInstance();
        // TODO: Extend EventMap to include 'construction:request' for full type safety
        (bus as any).emit('construction:request', event);
    }

    // ... existing code ...
} 