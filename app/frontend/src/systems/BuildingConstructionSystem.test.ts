import { ConstructionRequestHandler, ConstructionRequest } from './ConstructionRequestSystem';
import { EventBus } from '../core/interfaces/types/events';
import { BuildingConstructionSystem } from './BuildingConstructionSystem';
import { BuildingPhysics, BUILDING_PHYSICS_DEFAULTS, BuildingStructure } from '../core/interfaces/types/building';
import { BuildingStructuralSystem } from './BuildingStructuralSystem';

describe('Event-driven ConstructionRequestSystem', () => {
    let construction: BuildingConstructionSystem;
    let structure: BuildingStructure;
    let defaultPhysics: BuildingPhysics;
    let structuralSystem: BuildingStructuralSystem;
    let handler: ConstructionRequestHandler;
    let bus: EventBus;
    let player: any;
    let resultEvent: any;

    beforeEach(() => {
        defaultPhysics = { ...BUILDING_PHYSICS_DEFAULTS };
        structuralSystem = new BuildingStructuralSystem(defaultPhysics);
        construction = new BuildingConstructionSystem();
        structure = {
            id: 'test-structure',
            elements: new Map(),
            integrity: 1
        };
        handler = new ConstructionRequestHandler(construction);
        bus = EventBus.getInstance();
        player = { id: 'player1', name: 'Test', position: { x: 0, y: 0 }, health: 100, maxHealth: 100, inventory: [], movement: { isMoving: false, direction: null, speed: 0, path: [], destination: null } };
        resultEvent = null;
        (bus as any).off('construction:result', () => { }); // Remove previous listeners
        (bus as any).on('construction:result', (event: any) => {
            resultEvent = event;
        });
    });

    it('processes a valid construction request and emits a completed event', async () => {
        const request: ConstructionRequest = {
            id: 'req-1',
            playerId: player.id,
            buildingType: 'house',
            elementType: 'wall',
            position: { x: 1, y: 1 },
            material: 'stone',
            resources: { stone: 2 },
            timestamp: Date.now()
        };
        const resourceCheck = () => true;
        const permissionCheck = () => true;
        BuildingConstructionSystem.emitConstructionRequest({
            request,
            structure,
            player,
            resourceCheck,
            permissionCheck
        });
        // Wait for async event processing
        await new Promise(res => setTimeout(res, 10));
        expect(resultEvent).toBeTruthy();
        expect(resultEvent.requestId).toBe('req-1');
        expect(resultEvent.status).toBe('completed');
        expect(resultEvent.structure).toBeDefined();
    });
}); 