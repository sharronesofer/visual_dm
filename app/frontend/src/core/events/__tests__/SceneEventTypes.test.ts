import {
    SceneEventType,
    SceneCreatedEvent,
    SceneLoadedEvent,
    SceneUnloadedEvent,
    SceneModifiedEvent,
    ObjectAddedEvent,
    ObjectRemovedEvent,
    ObjectTransformedEvent,
    RegionEvent,
    WorldgenEvent
} from '../SceneEventTypes';

describe('Scene Event Type Interfaces', () => {
    it('should create a SceneCreatedEvent with correct properties', () => {
        const event: SceneCreatedEvent = {
            type: SceneEventType.SCENE_PRE_LOAD,
            sceneId: 'scene-1',
            source: 'SceneManager',
            timestamp: Date.now(),
            metadata: { name: 'Test Scene', creator: 'AI' }
        };
        expect(event.type).toBe(SceneEventType.SCENE_PRE_LOAD);
        expect(event.metadata.name).toBe('Test Scene');
    });

    it('should create a SceneLoadedEvent with correct properties', () => {
        const event: SceneLoadedEvent = {
            type: SceneEventType.SCENE_LOADED,
            sceneId: 'scene-2',
            source: 'Loader',
            timestamp: Date.now(),
            loadTime: 1234
        };
        expect(event.type).toBe(SceneEventType.SCENE_LOADED);
        expect(event.loadTime).toBe(1234);
    });

    it('should create a SceneUnloadedEvent with correct properties', () => {
        const event: SceneUnloadedEvent = {
            type: SceneEventType.SCENE_UNLOADED,
            sceneId: 'scene-3',
            source: 'Unloader',
            timestamp: Date.now(),
            reason: 'User request'
        };
        expect(event.type).toBe(SceneEventType.SCENE_UNLOADED);
        expect(event.reason).toBe('User request');
    });

    it('should create a SceneModifiedEvent with correct properties', () => {
        const event: SceneModifiedEvent = {
            type: SceneEventType.SCENE_ACTIVATED,
            sceneId: 'scene-4',
            source: 'Modifier',
            timestamp: Date.now(),
            changeSummary: 'Added new object'
        };
        expect(event.type).toBe(SceneEventType.SCENE_ACTIVATED);
        expect(event.changeSummary).toBe('Added new object');
    });

    it('should create an ObjectAddedEvent with correct properties', () => {
        const event: ObjectAddedEvent = {
            type: SceneEventType.SCENE_OBJECT_ADDED,
            sceneId: 'scene-5',
            source: 'ObjectManager',
            timestamp: Date.now(),
            objectId: 'obj-1',
            objectData: { type: 'Mesh', name: 'Cube' }
        };
        expect(event.type).toBe(SceneEventType.SCENE_OBJECT_ADDED);
        expect(event.objectId).toBe('obj-1');
        expect(event.objectData.type).toBe('Mesh');
    });

    it('should create an ObjectRemovedEvent with correct properties', () => {
        const event: ObjectRemovedEvent = {
            type: SceneEventType.SCENE_OBJECT_REMOVED,
            sceneId: 'scene-6',
            source: 'ObjectManager',
            timestamp: Date.now(),
            objectId: 'obj-2',
            removalReason: 'Deleted by user'
        };
        expect(event.type).toBe(SceneEventType.SCENE_OBJECT_REMOVED);
        expect(event.objectId).toBe('obj-2');
        expect(event.removalReason).toBe('Deleted by user');
    });

    it('should create an ObjectTransformedEvent with correct properties', () => {
        const event: ObjectTransformedEvent = {
            type: SceneEventType.COORDINATES_CHANGED,
            sceneId: 'scene-7',
            source: 'TransformSystem',
            timestamp: Date.now(),
            objectId: 'obj-3',
            previousTransform: { x: 0, y: 0, z: 0 },
            newTransform: { x: 1, y: 2, z: 3 }
        };
        expect(event.type).toBe(SceneEventType.COORDINATES_CHANGED);
        expect(event.previousTransform.x).toBe(0);
        expect(event.newTransform.z).toBe(3);
    });

    it('should create a RegionEvent with correct properties', () => {
        const event: RegionEvent = {
            type: SceneEventType.REGION_ENTERED,
            sceneId: 'scene-8',
            source: 'RegionSystem',
            timestamp: Date.now(),
            regionId: 'region-1'
        };
        expect(event.type).toBe(SceneEventType.REGION_ENTERED);
        expect(event.regionId).toBe('region-1');
    });

    it('should create a WorldgenEvent with correct properties', () => {
        const event: WorldgenEvent = {
            type: SceneEventType.TERRAIN_LOADED,
            sceneId: 'scene-9',
            source: 'Worldgen',
            timestamp: Date.now(),
            details: { biome: 'forest', elevation: 100 }
        };
        expect(event.type).toBe(SceneEventType.TERRAIN_LOADED);
        expect(event.details.biome).toBe('forest');
    });
}); 