// DamageVisualSystem.ts
// Maps building damage states to visual representations and handles state transitions

import { OverlayManager, OverlayType } from './OverlayManager.ts';
import { SpriteRegistry, SpriteKey } from './SpriteRegistry.ts';
import { Point, Size, BuildingVisualInfo } from './types.ts';

/**
 * DamageState - Enum for canonical damage states
 */
export enum DamageState {
    PRISTINE = 'pristine',
    DIRTY = 'dirty',
    DINGY = 'dingy',
    CHIPPED = 'chipped',
    CRACKED = 'cracked',
    DESTROYED = 'destroyed',
}

/**
 * DamageVisualMapping - Maps damage states to overlays/sprites
 */
export interface DamageVisualMapping {
    state: DamageState;
    overlayTypes: OverlayType[];
    spriteKey?: SpriteKey;
    transition?: 'fade' | 'crossfade' | 'instant';
}

/**
 * DamageVisualSystem - Singleton for managing damage state visuals
 */
export class DamageVisualSystem {
    private static _instance: DamageVisualSystem;
    private overlayManager: OverlayManager | null = null;
    private spriteRegistry: SpriteRegistry | null = null;
    private mappings: Map<DamageState, DamageVisualMapping> = new Map();

    private constructor() {
        this.registerDefaultMappings();
    }

    /**
     * Get the singleton instance
     */
    public static getInstance(): DamageVisualSystem {
        if (!DamageVisualSystem._instance) {
            DamageVisualSystem._instance = new DamageVisualSystem();
        }
        return DamageVisualSystem._instance;
    }

    /**
     * Register default mappings for damage states
     */
    private registerDefaultMappings() {
        this.registerMapping({ state: DamageState.PRISTINE, overlayTypes: [], spriteKey: 'pristine', transition: 'instant' });
        this.registerMapping({ state: DamageState.DIRTY, overlayTypes: [OverlayType.DIRTY], spriteKey: 'dirty', transition: 'fade' });
        this.registerMapping({ state: DamageState.DINGY, overlayTypes: [OverlayType.DINGY], spriteKey: 'dingy', transition: 'fade' });
        this.registerMapping({ state: DamageState.CHIPPED, overlayTypes: [OverlayType.CHIPPED], spriteKey: 'chipped', transition: 'crossfade' });
        this.registerMapping({ state: DamageState.CRACKED, overlayTypes: [OverlayType.CRACKED], spriteKey: 'cracked', transition: 'crossfade' });
        this.registerMapping({ state: DamageState.DESTROYED, overlayTypes: [], spriteKey: 'destroyed', transition: 'instant' });
    }

    /**
     * Register a mapping for a damage state
     */
    public registerMapping(mapping: DamageVisualMapping) {
        this.mappings.set(mapping.state, mapping);
    }

    /**
     * Get the visual mapping for a damage state
     */
    public getVisualMapping(state: DamageState): DamageVisualMapping | undefined {
        return this.mappings.get(state);
    }

    /**
     * Update visuals for a building based on its damage state
     * @param buildingId - Unique building identifier
     * @param state - Current damage state
     * @param options - { position, size }
     */
    public updateVisualsForBuilding(
        buildingId: string,
        state: DamageState,
        options?: { position?: Point; size?: Size }
    ) {
        if (!this.overlayManager) return;
        // Remove all overlays first
        Object.values(OverlayType).forEach(type => this.overlayManager!.removeOverlay(buildingId, type));
        // Apply overlays for this state
        const mapping = this.getVisualMapping(state);
        if (mapping) {
            mapping.overlayTypes.forEach((type, idx) => {
                this.overlayManager!.applyOverlay(buildingId, type, {
                    position: options?.position,
                    size: options?.size,
                    zIndex: 100 + idx, // Ensure overlays are above base sprite
                });
            });
            // Optionally update sprite (integration stub)
            // TODO: Use spriteRegistry to update base sprite if needed
        }
        // TODO: Handle transitions (fade/crossfade/instant)
    }

    /**
     * Get the current visual state for a building (stub)
     */
    public getVisualState(buildingId: string): DamageState {
        // TODO: Integrate with damage tracking system
        return DamageState.PRISTINE;
    }

    /**
     * Set the OverlayManager instance
     */
    public setOverlayManager(manager: OverlayManager) {
        this.overlayManager = manager;
    }

    /**
     * Set the SpriteRegistry instance
     */
    public setSpriteRegistry(registry: SpriteRegistry) {
        this.spriteRegistry = registry;
    }

    // --- Performance notes ---
    // TODO: Use offscreen canvas for batching visual updates
    // TODO: Minimize redraws to only changed visuals
    // TODO: Memory management for unused visual assets
}

// Usage: const dvs = DamageVisualSystem.getInstance();
