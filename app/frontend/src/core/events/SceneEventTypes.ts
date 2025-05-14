/**
 * Scene event types for the central event bus system
 */

/**
 * Defines event types related to scene management
 */
export enum SceneEventType {
    // Scene lifecycle events
    SCENE_PRE_LOAD = 'scene_pre_load',
    SCENE_LOADED = 'scene_loaded',
    SCENE_PRE_UNLOAD = 'scene_pre_unload',
    SCENE_UNLOADED = 'scene_unloaded',
    SCENE_LOAD_FAILED = 'scene_load_failed',

    // Scene activation events
    SCENE_ACTIVATED = 'scene_activated',
    SCENE_DEACTIVATED = 'scene_deactivated',

    // Object-related events
    SCENE_OBJECT_ADDED = 'scene_object_added',
    SCENE_OBJECT_REMOVED = 'scene_object_removed',

    // Memory management events
    MEMORY_WARNING = 'memory_warning',
    MEMORY_CRITICAL = 'memory_critical',

    // Region-related events
    REGION_ENTERED = 'region_entered',
    REGION_EXITED = 'region_exited',

    // Spatial system events
    COORDINATES_CHANGED = 'coordinates_changed',
    BOUNDARY_CROSSED = 'boundary_crossed',

    // Worldgen events
    TERRAIN_LOADED = 'terrain_loaded',
    TERRAIN_UNLOADED = 'terrain_unloaded',
    BIOME_CHANGED = 'biome_changed',
}

/**
 * Base interface for all scene events
 */
export interface ISceneEvent {
    /** Type of the event */
    type: SceneEventType;
    /** Unique identifier for the scene related to this event */
    sceneId?: string;
    /** Component/system that generated this event */
    source: string;
    /** Timestamp when the event was created */
    timestamp: number;
    /** Additional data associated with the event */
    data?: Record<string, any>;
}

/**
 * Scene lifecycle event: Scene created
 */
export interface SceneCreatedEvent extends ISceneEvent {
    type: SceneEventType.SCENE_PRE_LOAD;
    /** Metadata about the created scene */
    metadata: Record<string, any>;
}

/**
 * Scene lifecycle event: Scene loaded
 */
export interface SceneLoadedEvent extends ISceneEvent {
    type: SceneEventType.SCENE_LOADED;
    /** Reference to the loaded scene */
    loadTime: number;
}

/**
 * Scene lifecycle event: Scene unloaded
 */
export interface SceneUnloadedEvent extends ISceneEvent {
    type: SceneEventType.SCENE_UNLOADED;
    /** Reason for unloading */
    reason?: string;
}

/**
 * Scene lifecycle event: Scene modified
 */
export interface SceneModifiedEvent extends ISceneEvent {
    type: SceneEventType.SCENE_ACTIVATED | SceneEventType.SCENE_DEACTIVATED;
    /** Details about the modification */
    changeSummary: string;
}

/**
 * Object event: Object added to scene
 */
export interface ObjectAddedEvent extends ISceneEvent {
    type: SceneEventType.SCENE_OBJECT_ADDED;
    objectId: string;
    parentId?: string;
    objectData: Record<string, any>;
}

/**
 * Object event: Object removed from scene
 */
export interface ObjectRemovedEvent extends ISceneEvent {
    type: SceneEventType.SCENE_OBJECT_REMOVED;
    objectId: string;
    removalReason?: string;
}

/**
 * Object event: Object transformed in scene
 */
export interface ObjectTransformedEvent extends ISceneEvent {
    type: SceneEventType.COORDINATES_CHANGED | SceneEventType.BOUNDARY_CROSSED;
    objectId: string;
    previousTransform: Record<string, any>;
    newTransform: Record<string, any>;
}

/**
 * Region event: Entered or exited region
 */
export interface RegionEvent extends ISceneEvent {
    type: SceneEventType.REGION_ENTERED | SceneEventType.REGION_EXITED;
    regionId: string;
}

/**
 * Worldgen event: Terrain or biome changed
 */
export interface WorldgenEvent extends ISceneEvent {
    type: SceneEventType.TERRAIN_LOADED | SceneEventType.TERRAIN_UNLOADED | SceneEventType.BIOME_CHANGED;
    details: Record<string, any>;
} 