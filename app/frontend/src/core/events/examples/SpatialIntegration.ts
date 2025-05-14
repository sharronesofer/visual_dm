/**
 * Example integration between Spatial System and Scene Event System.
 * 
 * This demonstrates how a system would integrate with the Scene Event System
 * to receive and handle scene events.
 */

import {
    SceneEventSystem,
    SceneEventType,
    DependencyType,
    ISceneEvent
} from '../index';

/**
 * Integration between Spatial System and Scene Event System
 */
export class SpatialIntegration {
    /** The scene event system instance */
    private eventSystem: SceneEventSystem;

    /** ID of the currently active scene */
    private activeScene: string | null = null;

    /** Set of boundary IDs being tracked */
    private trackedBoundaries: Set<string> = new Set();

    /**
     * Initialize the integration
     * 
     * @param spatialSystem Optional spatial system to integrate with
     */
    constructor(private spatialSystem: any = null) {
        this.eventSystem = SceneEventSystem.getInstance();

        // Register with scene event system
        this.registerEventHandlers();

        console.log('Spatial Integration initialized');
    }

    /**
     * Register handlers for scene events
     */
    private registerEventHandlers(): void {
        // Register system dependency
        this.eventSystem.registerSystemDependency(
            'SpatialSystem',
            [DependencyType.SCENE_LIFECYCLE, DependencyType.SPATIAL]
        );

        // Register global listeners
        this.eventSystem.registerGlobalListener(
            SceneEventType.SCENE_ACTIVATED,
            this.handleSceneActivated.bind(this)
        );

        this.eventSystem.registerGlobalListener(
            SceneEventType.SCENE_DEACTIVATED,
            this.handleSceneDeactivated.bind(this)
        );

        this.eventSystem.registerGlobalListener(
            SceneEventType.COORDINATES_CHANGED,
            this.handleCoordinatesChanged.bind(this)
        );

        this.eventSystem.registerGlobalListener(
            SceneEventType.BOUNDARY_CROSSED,
            this.handleBoundaryCrossed.bind(this)
        );
    }

    /**
     * Handle scene activated event
     * 
     * @param event Scene event
     */
    private handleSceneActivated(event: ISceneEvent): void {
        const sceneId = event.sceneId;

        if (!sceneId) {
            console.warn('Received SCENE_ACTIVATED event without sceneId');
            return;
        }

        console.log(`SpatialSystem: Scene ${sceneId} activated`);
        this.activeScene = sceneId;

        // Initialize spatial data for this scene
        if (this.spatialSystem) {
            // Example: this.spatialSystem.initializeScene(sceneId);
            console.log(`SpatialSystem: Initialized spatial data for scene ${sceneId}`);
        }
    }

    /**
     * Handle scene deactivated event
     * 
     * @param event Scene event
     */
    private handleSceneDeactivated(event: ISceneEvent): void {
        const sceneId = event.sceneId;

        if (!sceneId || sceneId !== this.activeScene) {
            return;
        }

        console.log(`SpatialSystem: Scene ${sceneId} deactivated`);
        this.activeScene = null;

        // Clean up spatial data for this scene
        if (this.spatialSystem) {
            // Example: this.spatialSystem.cleanupScene(sceneId);
            console.log(`SpatialSystem: Cleaned up spatial data for scene ${sceneId}`);
        }
    }

    /**
     * Handle coordinates changed event
     * 
     * @param event Scene event
     */
    private handleCoordinatesChanged(event: ISceneEvent): void {
        if (!event.data?.coordinates) {
            console.warn('Received COORDINATES_CHANGED event without coordinates data');
            return;
        }

        const coordinates = event.data.coordinates;
        console.log(`SpatialSystem: Coordinates changed to ${JSON.stringify(coordinates)}`);

        // Update spatial indices, check for boundary crossings, etc.
        if (this.spatialSystem) {
            // Example: this.spatialSystem.updatePosition(coordinates);
            console.log('SpatialSystem: Updated spatial indices');
        }
    }

    /**
     * Handle boundary crossed event
     * 
     * @param event Scene event
     */
    private handleBoundaryCrossed(event: ISceneEvent): void {
        if (!event.data?.boundary) {
            console.warn('Received BOUNDARY_CROSSED event without boundary data');
            return;
        }

        const boundary = event.data.boundary;
        const entering = event.data.entering ?? false;

        console.log(`SpatialSystem: ${entering ? 'Entered' : 'Exited'} boundary ${boundary}`);

        if (entering) {
            this.trackedBoundaries.add(boundary);
        } else {
            this.trackedBoundaries.delete(boundary);
        }

        // Update spatial tracking based on boundary
        if (this.spatialSystem) {
            // Example: this.spatialSystem.updateBoundaryStatus(boundary, entering);
            console.log(`SpatialSystem: Updated boundary status for ${boundary}`);
        }
    }

    /**
     * Disconnect from the event system
     */
    public disconnect(): void {
        // Unregister global listeners
        this.eventSystem.unregisterGlobalListener(
            SceneEventType.SCENE_ACTIVATED,
            this.handleSceneActivated.bind(this)
        );

        this.eventSystem.unregisterGlobalListener(
            SceneEventType.SCENE_DEACTIVATED,
            this.handleSceneDeactivated.bind(this)
        );

        this.eventSystem.unregisterGlobalListener(
            SceneEventType.COORDINATES_CHANGED,
            this.handleCoordinatesChanged.bind(this)
        );

        this.eventSystem.unregisterGlobalListener(
            SceneEventType.BOUNDARY_CROSSED,
            this.handleBoundaryCrossed.bind(this)
        );

        // Unregister system dependency
        this.eventSystem.unregisterSystemDependency('SpatialSystem');

        console.log('Spatial Integration disconnected');
    }
}