import { OverlayManager, OverlayType, OverlayInstance } from './OverlayManager';
import { SpriteRegistry, SpriteKey } from './SpriteRegistry';
import { BuildingStructure } from '../core/interfaces/types/building';
import { BuildingModuleSystem } from '../systems/building_modules/BuildingModuleSystem';
import { BuildingModule } from '../systems/building_modules/BuildingModule';

export type DamageAxis = 'battle' | 'deterioration';
export type DamageState = 'intact' | 'dirty' | 'dingy' | 'chipped' | 'cracked' | 'destroyed';

export interface BuildingVisualConfig {
    spriteKey: SpriteKey;
    overlayTypes: OverlayType[];
}

export interface DamageVisualSystemOptions {
    overlayManager: OverlayManager;
    spriteRegistry: SpriteRegistry;
    damageStateMap: Record<DamageState, OverlayType[]>;
    fadeDuration?: number; // ms
}

/**
 * DamageVisualSystem: Visualizes building and module damage states with overlays and sprites.
 * Performance optimizations:
 * - Sprite batching: Groups draw calls by sprite key to minimize context state changes.
 * - Minimal redraws: (Stub) Track dirty regions to avoid unnecessary redraws.
 * - Memory management: Ensure overlays and sprites are released when no longer needed.
 */
export class DamageVisualSystem {
    private overlayManager: OverlayManager;
    private spriteRegistry: SpriteRegistry;
    private damageStateMap: Record<DamageState, OverlayType[]>;
    private fadeDuration: number;

    constructor(options: DamageVisualSystemOptions) {
        this.overlayManager = options.overlayManager;
        this.spriteRegistry = options.spriteRegistry;
        this.damageStateMap = options.damageStateMap;
        this.fadeDuration = options.fadeDuration ?? 200;
    }

    /**
     * Get the overlays to apply for a given damage state.
     */
    public getOverlaysForState(state: DamageState): OverlayType[] {
        return this.damageStateMap[state] || [];
    }

    /**
     * Render the building/module visual state.
     * @param ctx Canvas context
     * @param spriteKey Sprite key for the building/module
     * @param state Current damage state
     * @param x X position
     * @param y Y position
     * @param width Width
     * @param height Height
     * @param options Optional: fade/crossfade, overlays, etc.
     */
    public renderVisual(
        ctx: CanvasRenderingContext2D,
        spriteKey: SpriteKey,
        state: DamageState,
        x: number,
        y: number,
        width: number,
        height: number,
        options?: { fade?: boolean; fadeProgress?: number; extraOverlays?: OverlayType[] }
    ) {
        // Draw base sprite
        const sprite = this.spriteRegistry.getSprite(spriteKey);
        if (sprite) {
            ctx.drawImage(sprite, x, y, width, height);
        }
        // Determine overlays
        const overlayTypes = [
            ...this.getOverlaysForState(state),
            ...(options?.extraOverlays || [])
        ];
        const overlayInstances: OverlayInstance[] = overlayTypes
            .map(type => this.overlayManager.createOverlayInstance(type, x, y, width, height))
            .filter((oi): oi is OverlayInstance => !!oi);
        // Optionally handle fade/crossfade
        if (options?.fade && typeof options.fadeProgress === 'number') {
            overlayInstances.forEach(oi => (oi.opacity = options.fadeProgress));
        }
        // Render overlays
        this.overlayManager.renderOverlays(ctx, overlayInstances);
    }

    /**
     * Utility to smoothly transition between two damage states (e.g., for animation).
     * @param ctx Canvas context
     * @param spriteKey Sprite key
     * @param fromState Previous state
     * @param toState New state
     * @param progress 0 (fromState) to 1 (toState)
     * @param x X position
     * @param y Y position
     * @param width Width
     * @param height Height
     */
    public renderTransition(
        ctx: CanvasRenderingContext2D,
        spriteKey: SpriteKey,
        fromState: DamageState,
        toState: DamageState,
        progress: number,
        x: number,
        y: number,
        width: number,
        height: number
    ) {
        // Draw base sprite
        const sprite = this.spriteRegistry.getSprite(spriteKey);
        if (sprite) {
            ctx.drawImage(sprite, x, y, width, height);
        }
        // Overlays for fromState (fade out)
        const fromOverlays = this.getOverlaysForState(fromState)
            .map(type => this.overlayManager.createOverlayInstance(type, x, y, width, height, undefined, 1 - progress))
            .filter((oi): oi is OverlayInstance => !!oi);
        // Overlays for toState (fade in)
        const toOverlays = this.getOverlaysForState(toState)
            .map(type => this.overlayManager.createOverlayInstance(type, x, y, width, height, undefined, progress))
            .filter((oi): oi is OverlayInstance => !!oi);
        this.overlayManager.renderOverlays(ctx, [...fromOverlays, ...toOverlays]);
    }

    /**
     * Called when a building's damage state changes. Used to update visuals.
     * @param structure The affected building structure
     * @param axis The damage axis ('battle' or 'deterioration')
     * @param oldValue Previous value of the axis
     * @param newValue New value of the axis
     */
    public updateVisual(structure: BuildingStructure, axis: DamageAxis, oldValue: number, newValue: number): void {
        // For now, mark the entire building as dirty for redraw.
        // In a real system, you would compute the bounding box of the building.
        // Placeholder: assume structure has a bounding box at (x, y, width, height) or default to (0,0,128,128)
        const x = (structure as any).x ?? 0;
        const y = (structure as any).y ?? 0;
        const width = (structure as any).width ?? 128;
        const height = (structure as any).height ?? 128;
        this.markDirtyRegion(x, y, width, height);
        // Optionally, trigger a re-render or notify a renderer here.
    }

    /**
     * Render all modules of a building with their damage overlays.
     * @param ctx Canvas context
     * @param structure The building structure
     * @param moduleSystem The BuildingModuleSystem instance
     * @param options Optional rendering options
     */
    public renderBuildingModules(
        ctx: CanvasRenderingContext2D,
        structure: BuildingStructure,
        moduleSystem: BuildingModuleSystem,
        options?: { fade?: boolean; debug?: boolean }
    ) {
        // For this example, assume module IDs are structure.id + '_' + moduleType + '_' + index or similar
        // In a real system, you would have a way to get all module IDs for a building
        // Here, we iterate all modules and filter by structure ID prefix if needed
        for (const module of moduleSystem['modules'].values()) {
            if (module.moduleId.startsWith(structure.id + '_')) {
                // Determine damage state (map ModuleState to DamageState if needed)
                let state: DamageState = 'intact';
                switch (module.currentState) {
                    case 'INTACT': state = 'intact'; break;
                    case 'DAMAGED': state = 'chipped'; break;
                    case 'SEVERELY_DAMAGED': state = 'cracked'; break;
                    case 'DESTROYED': state = 'destroyed'; break;
                }
                // Use module type as spriteKey, or customize as needed
                this.renderVisual(
                    ctx,
                    module.type,
                    state,
                    module.position.x,
                    module.position.y,
                    64, // width (example)
                    64, // height (example)
                    options
                );
                if (options?.debug) {
                    ctx.save();
                    ctx.fillStyle = 'red';
                    ctx.font = '10px sans-serif';
                    ctx.fillText(module.moduleId, module.position.x, module.position.y - 4);
                    ctx.restore();
                }
            }
        }
    }

    /**
     * Render a batch of modules/buildings by sprite key for performance.
     * @param ctx Canvas context
     * @param renderItems Array of { spriteKey, state, x, y, width, height, options }
     */
    public renderBatch(
        ctx: CanvasRenderingContext2D,
        renderItems: Array<{
            spriteKey: SpriteKey;
            state: DamageState;
            x: number;
            y: number;
            width: number;
            height: number;
            options?: { fade?: boolean; fadeProgress?: number; extraOverlays?: OverlayType[] }
        }>
    ) {
        // Group by spriteKey for batching
        const groups: Record<string, typeof renderItems> = {};
        for (const item of renderItems) {
            if (!groups[item.spriteKey]) groups[item.spriteKey] = [];
            groups[item.spriteKey].push(item);
        }
        for (const spriteKey in groups) {
            // Optionally: set context state for this spriteKey
            for (const item of groups[spriteKey]) {
                this.renderVisual(
                    ctx,
                    item.spriteKey,
                    item.state,
                    item.x,
                    item.y,
                    item.width,
                    item.height,
                    item.options
                );
            }
        }
    }

    /**
     * (Stub) Mark a region as dirty for minimal redraws.
     * In a real system, track dirty rectangles and only redraw those.
     */
    public markDirtyRegion(x: number, y: number, width: number, height: number) {
        // TODO: Implement dirty region tracking for minimal redraws
    }

    /**
     * (Note) Memory management: Call this to release overlays and sprites when no longer needed.
     */
    public dispose() {
        // TODO: Release references to overlays and sprites for GC
        // this.overlayManager.dispose();
        // this.spriteRegistry.dispose();
    }
} 