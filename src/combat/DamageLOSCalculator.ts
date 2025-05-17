import { Point } from '../visualization/map/types';
import { BuildingDamageSystem } from '../systems/BuildingDamageSystem';
import { BuildingStructure, BuildingElement } from '../core/interfaces/types/building';

/**
 * DamageLOSCalculator
 * Calculates line of sight (LOS) between two points, accounting for building damage states.
 * Supports partial, blocked, and clear visibility through damaged modules (walls, windows, etc.).
 * Integrates with BuildingDamageSystem and supports caching for static damage states.
 */
export class DamageLOSCalculator {
    private damageSystem: BuildingDamageSystem;
    private cache: Map<string, number> = new Map(); // key: `${from.x},${from.y},${to.x},${to.y},${structure.id}`

    constructor(damageSystem: BuildingDamageSystem) {
        this.damageSystem = damageSystem;
    }

    /**
     * Calculate visibility percentage between two points through a building structure.
     * Returns a value between 0 (blocked) and 1 (fully visible), with partial values for damaged sections.
     */
    public calculateVisibility(
        from: Point,
        to: Point,
        structure: BuildingStructure
    ): number {
        const cacheKey = `${from.x},${from.y},${to.x},${to.y},${structure.id}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey)!;
        }

        // Bresenham's line algorithm for raycasting
        let x0 = Math.floor(from.x);
        let y0 = Math.floor(from.y);
        const x1 = Math.floor(to.x);
        const y1 = Math.floor(to.y);
        const dx = Math.abs(x1 - x0);
        const dy = Math.abs(y1 - y0);
        const sx = x0 < x1 ? 1 : -1;
        const sy = y0 < y1 ? 1 : -1;
        let err = dx - dy;

        let visibility = 1; // Start fully visible
        let encounteredBlock = false;

        // For each step along the line, check for blocking/damaged elements
        while (true) {
            // Find building element at this position (if any)
            const element = this.getElementAtPosition(structure, x0, y0);
            if (element) {
                const damageRatio = element.health / element.maxHealth;
                // Define thresholds (configurable):
                // - damageRatio > 0.7: mostly intact (blocks LOS)
                // - 0.3 < damageRatio <= 0.7: partially damaged (partial LOS)
                // - damageRatio <= 0.3: heavily damaged (mostly clear)
                if (damageRatio > 0.7) {
                    visibility *= 0; // Blocked
                    encounteredBlock = true;
                    break;
                } else if (damageRatio > 0.3) {
                    visibility *= 0.5; // Partial
                } // else: minimal effect, continue
            }
            if (x0 === x1 && y0 === y1) {
                break;
            }
            const e2 = 2 * err;
            if (e2 > -dy) {
                err -= dy;
                x0 += sx;
            }
            if (e2 < dx) {
                err += dx;
                y0 += sy;
            }
        }
        // Cache result for static damage states
        this.cache.set(cacheKey, visibility);
        return visibility;
    }

    /**
     * Find a building element at a given grid position (x, y)
     */
    private getElementAtPosition(structure: BuildingStructure, x: number, y: number): BuildingElement | undefined {
        for (const element of structure.elements.values()) {
            if (Math.floor(element.position.x) === x && Math.floor(element.position.y) === y) {
                return element;
            }
        }
        return undefined;
    }

    /**
     * Invalidate cache for a structure (call when damage state changes)
     */
    public invalidateCache(structureId: string) {
        for (const key of this.cache.keys()) {
            if (key.endsWith(`,${structureId}`)) {
                this.cache.delete(key);
            }
        }
    }
} 