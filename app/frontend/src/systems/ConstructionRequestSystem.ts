import { EventBus } from '../core/interfaces/types/events';
import { PlayerState } from '../core/interfaces/types/player';
import { BuildingStructure, MaterialType, BuildingElementType, BuildingElement } from '../core/interfaces/types/building';
import { Position } from '../core/interfaces/types/common';
import { BuildingConstructionSystem } from './BuildingConstructionSystem';
import { v4 as uuidv4 } from 'uuid';

// --- Construction Request Types ---
export interface ConstructionRequest {
    id: string;
    playerId: string;
    buildingType: string;
    elementType: BuildingElementType;
    position: Position;
    material: MaterialType;
    isLoadBearing?: boolean;
    resources: Record<string, number>;
    timestamp: number;
}

export type ConstructionRequestStatus = 'pending' | 'validating' | 'validated' | 'invalid' | 'queued' | 'processing' | 'completed' | 'failed';

export interface ConstructionRequestResult {
    requestId: string;
    status: ConstructionRequestStatus;
    errors?: string[];
    structure?: BuildingStructure;
}

// --- Construction Request Queue ---
export class ConstructionRequestQueue {
    private queue: ConstructionRequest[] = [];

    enqueue(request: ConstructionRequest) {
        this.queue.push(request);
    }

    dequeue(): ConstructionRequest | undefined {
        return this.queue.shift();
    }

    peek(): ConstructionRequest | undefined {
        return this.queue[0];
    }

    get length() {
        return this.queue.length;
    }

    clear() {
        this.queue = [];
    }
}

// --- Construction Validator ---
export class ConstructionValidator {
    constructor(
        private constructionSystem: BuildingConstructionSystem
    ) { }

    validate(
        request: ConstructionRequest,
        structure: BuildingStructure,
        player: PlayerState,
        resourceCheck: (player: PlayerState, resources: Record<string, number>) => boolean,
        permissionCheck: (player: PlayerState, position: Position) => boolean
    ): { valid: boolean; errors: string[] } {
        const errors: string[] = [];
        // 1. Check permissions
        if (!permissionCheck(player, request.position)) {
            errors.push('Player does not have permission to build at this location.');
        }
        // 2. Check resources
        if (!resourceCheck(player, request.resources)) {
            errors.push('Insufficient resources for construction.');
        }
        // 3. Check placement validity
        if (!this.constructionSystem.canBuildAt(structure, request.position, request.elementType)) {
            errors.push('Invalid placement: position is occupied or not allowed.');
        }
        // 4. Additional rules (e.g., load-bearing, adjacency)
        // Extend here as needed
        return { valid: errors.length === 0, errors };
    }
}

// --- Construction Request Handler ---
export class ConstructionRequestHandler {
    private queue = new ConstructionRequestQueue();
    private validator: ConstructionValidator;
    private eventBus = EventBus.getInstance();
    private constructionSystem: BuildingConstructionSystem;

    constructor(constructionSystem: BuildingConstructionSystem) {
        this.constructionSystem = constructionSystem;
        this.validator = new ConstructionValidator(constructionSystem);
        // Register event listener for construction requests
        this.eventBus.on('construction:request', this.handleRequestEvent.bind(this));
    }

    // Simulated event type for construction requests
    public static readonly EVENT_TYPE = 'construction:request';

    // Main entry point for handling construction requests
    async handleRequestEvent(event: { request: ConstructionRequest; structure: BuildingStructure; player: PlayerState; resourceCheck: (player: PlayerState, resources: Record<string, number>) => boolean; permissionCheck: (player: PlayerState, position: Position) => boolean; }) {
        const { request, structure, player, resourceCheck, permissionCheck } = event;
        // Validate request
        const validation = this.validator.validate(request, structure, player, resourceCheck, permissionCheck);
        if (!validation.valid) {
            this.eventBus.emit('construction:result', {
                requestId: request.id,
                status: 'invalid',
                errors: validation.errors
            });
            return;
        }
        // Enqueue validated request
        this.queue.enqueue(request);
        this.eventBus.emit('construction:result', {
            requestId: request.id,
            status: 'queued'
        });
        // Process queue (could be async, throttled, or batched)
        await this.processQueue(structure, player);
    }

    // Process the next request in the queue
    private async processQueue(structure: BuildingStructure, player: PlayerState) {
        while (this.queue.length > 0) {
            const request = this.queue.dequeue();
            if (!request) break;
            try {
                let updatedStructure = structure;
                switch (request.elementType) {
                    case 'wall':
                        updatedStructure = this.constructionSystem.addWall(
                            structure,
                            request.position,
                            request.material,
                            request.isLoadBearing || false,
                            request.playerId,
                            request.buildingType
                        );
                        break;
                    case 'door':
                        updatedStructure = this.constructionSystem.addDoor(
                            structure,
                            request.position,
                            request.material,
                            request.playerId,
                            request.buildingType
                        );
                        break;
                    case 'window':
                        updatedStructure = this.constructionSystem.addWindow(
                            structure,
                            request.position,
                            request.material,
                            request.playerId,
                            request.buildingType
                        );
                        break;
                    default:
                        throw new Error('Unsupported element type');
                }
                this.eventBus.emit('construction:result', {
                    requestId: request.id,
                    status: 'completed',
                    structure: updatedStructure
                });
            } catch (err: any) {
                this.eventBus.emit('construction:result', {
                    requestId: request.id,
                    status: 'failed',
                    errors: [err.message]
                });
            }
        }
    }
}

// Usage Example (to be removed in production):
// const constructionSystem = new BuildingConstructionSystem();
// const handler = new ConstructionRequestHandler(constructionSystem);
// handler.handleRequestEvent({ ... }); 