// OverlayManager.ts
// Manages building damage overlays: positioning, layering, Z-ordering, and rendering
// Asset dir: /assets/overlays/

import { Point, Size, BuildingVisualInfo } from './types.ts';

/**
 * OverlayType - Enum for supported overlay types (expand as needed)
 */
export enum OverlayType {
    DIRTY = 'dirty',
    DINGY = 'dingy',
    CHIPPED = 'chipped',
    CRACKED = 'cracked',
    // Add more as needed
}

/**
 * OverlayInstance - Represents a single overlay applied to a building
 */
export interface OverlayInstance {
    buildingId: string;
    overlayType: OverlayType;
    zIndex: number;
    position: Point;
    size: Size;
    assetRef: HTMLImageElement;
}

/**
 * OverlayManager - Singleton for managing overlays on buildings
 */
export class OverlayManager {
    private static _instance: OverlayManager;
    private overlays: Map<string, OverlayInstance[]> = new Map(); // buildingId -> overlays
    private overlayAssets: Map<OverlayType, HTMLImageElement> = new Map();

    private constructor() {
        this.preloadAssets();
    }

    /**
     * Get the singleton instance
     */
    public static getInstance(): OverlayManager {
        if (!OverlayManager._instance) {
            OverlayManager._instance = new OverlayManager();
        }
        return OverlayManager._instance;
    }

    /**
     * Preload/caches overlay images from /assets/overlays/
     */
    private preloadAssets() {
        Object.values(OverlayType).forEach(type => {
            const img = new window.Image();
            img.src = `/assets/overlays/${type}.png`;
            this.overlayAssets.set(type as OverlayType, img);
        });
    }

    /**
     * Apply an overlay to a building
     * @param buildingId - Unique building identifier
     * @param overlayType - Type of overlay
     * @param options - Optional: position, size, zIndex
     */
    public applyOverlay(
        buildingId: string,
        overlayType: OverlayType,
        options?: Partial<Pick<OverlayInstance, 'position' | 'size' | 'zIndex'>>
    ) {
        const overlays = this.overlays.get(buildingId) || [];
        // Default zIndex: higher for more severe damage
        const defaultZ = this.getDefaultZIndex(overlayType);
        const assetRef = this.overlayAssets.get(overlayType);
        if (!assetRef) return;
        const instance: OverlayInstance = {
            buildingId,
            overlayType,
            zIndex: options?.zIndex ?? defaultZ,
            position: options?.position ?? { x: 0, y: 0 },
            size: options?.size ?? { width: 64, height: 64 }, // TODO: dynamic sizing
            assetRef,
        };
        // Replace if already present
        const idx = overlays.findIndex(o => o.overlayType === overlayType);
        if (idx >= 0) overlays[idx] = instance;
        else overlays.push(instance);
        // Sort overlays by zIndex
        overlays.sort((a, b) => a.zIndex - b.zIndex);
        this.overlays.set(buildingId, overlays);
    }

    /**
     * Remove an overlay from a building
     */
    public removeOverlay(buildingId: string, overlayType: OverlayType) {
        const overlays = this.overlays.get(buildingId);
        if (!overlays) return;
        const filtered = overlays.filter(o => o.overlayType !== overlayType);
        if (filtered.length) this.overlays.set(buildingId, filtered);
        else this.overlays.delete(buildingId);
    }

    /**
     * Get all active overlays for a building
     */
    public getActiveOverlays(buildingId: string): OverlayInstance[] {
        return this.overlays.get(buildingId) || [];
    }

    /**
     * Render overlays for a set of buildings
     * @param context - CanvasRenderingContext2D
     * @param buildings - Array of { id, position, size }
     */
    public renderOverlays(
        context: CanvasRenderingContext2D,
        buildings: BuildingVisualInfo[]
    ) {
        // TODO: Use offscreen canvas for batching
        for (const building of buildings) {
            const overlays = this.getActiveOverlays(building.id);
            for (const overlay of overlays) {
                // Compute position/size based on building
                const pos = overlay.position || building.position;
                const size = overlay.size || building.size;
                context.save();
                context.globalAlpha = 1.0; // TODO: support fade
                context.drawImage(overlay.assetRef, pos.x, pos.y, size.width, size.height);
                context.restore();
            }
        }
    }

    /**
     * Get default zIndex for overlay type (higher = more severe)
     */
    private getDefaultZIndex(type: OverlayType): number {
        switch (type) {
            case OverlayType.CRACKED:
                return 40;
            case OverlayType.CHIPPED:
                return 30;
            case OverlayType.DINGY:
                return 20;
            case OverlayType.DIRTY:
                return 10;
            default:
                return 0;
        }
    }

    // --- Integration stubs ---
    /**
     * Integrate with SpriteRegistry (stub)
     */
    public setSpriteRegistry(_registry: any) {
        // TODO: implement integration
    }

    // --- Performance notes ---
    // TODO: Use offscreen canvas for batching overlays
    // TODO: Minimize redraws to only changed overlays
    // TODO: Memory management for unused overlays
}

// Usage: const overlayManager = OverlayManager.getInstance();
