// OverlayManager.ts
// Handles visual overlays for building damage states (dirty, dingy, chipped, cracked, etc.)

export type OverlayType = 'dirty' | 'dingy' | 'chipped' | 'cracked';

export interface Overlay {
    type: OverlayType;
    image: HTMLImageElement;
    zIndex: number;
    opacity?: number;
}

export interface OverlayInstance {
    overlay: Overlay;
    x: number;
    y: number;
    width: number;
    height: number;
    rotation?: number;
    opacity?: number;
}

/**
 * OverlayManager manages the application and rendering of damage overlays on buildings.
 * Supports layering, Z-ordering, and dynamic positioning/scaling.
 */
export class OverlayManager {
    private overlays: Map<OverlayType, Overlay> = new Map();

    /**
     * Register a new overlay type with its image and z-index.
     */
    public registerOverlay(type: OverlayType, image: HTMLImageElement, zIndex: number, opacity: number = 1) {
        this.overlays.set(type, { type, image, zIndex, opacity });
    }

    /**
     * Unregister an overlay type.
     */
    public unregisterOverlay(type: OverlayType) {
        this.overlays.delete(type);
    }

    /**
     * Get overlay by type.
     */
    public getOverlay(type: OverlayType): Overlay | undefined {
        return this.overlays.get(type);
    }

    /**
     * Render overlays for a building at the given position/size.
     * @param ctx Canvas rendering context
     * @param overlayInstances List of overlay instances to render (with position, size, etc.)
     */
    public renderOverlays(ctx: CanvasRenderingContext2D, overlayInstances: OverlayInstance[]) {
        // Sort overlays by zIndex for correct layering
        const sorted = [...overlayInstances].sort((a, b) => (a.overlay.zIndex - b.overlay.zIndex));
        for (const instance of sorted) {
            ctx.save();
            ctx.globalAlpha = instance.opacity ?? instance.overlay.opacity ?? 1;
            if (instance.rotation) {
                ctx.translate(instance.x + instance.width / 2, instance.y + instance.height / 2);
                ctx.rotate(instance.rotation);
                ctx.drawImage(
                    instance.overlay.image,
                    -instance.width / 2,
                    -instance.height / 2,
                    instance.width,
                    instance.height
                );
            } else {
                ctx.drawImage(
                    instance.overlay.image,
                    instance.x,
                    instance.y,
                    instance.width,
                    instance.height
                );
            }
            ctx.restore();
        }
    }

    /**
     * Utility to create an OverlayInstance for a given overlay type and building bounds.
     */
    public createOverlayInstance(type: OverlayType, x: number, y: number, width: number, height: number, rotation?: number, opacity?: number): OverlayInstance | undefined {
        const overlay = this.getOverlay(type);
        if (!overlay) return undefined;
        return { overlay, x, y, width, height, rotation, opacity };
    }
} 