// LODSystem.ts
// Manages Level of Detail (LOD) selection for buildings in large-scale worldgen

export enum LODLevel {
    Full = 0,         // Full detail
    Simplified = 1,   // Reduced geometry/textures
    Placeholder = 2,  // Minimal representation
    None = 3          // Not rendered/generated
}

export interface LODSystemOptions {
    lodDistances: [number, number, number]; // [Full->Simplified, Simplified->Placeholder, Placeholder->None]
    getPlayerPosition: () => { x: number; y: number };
}

/**
 * LODSystem: Handles LOD selection and transitions for buildings
 */
export class LODSystem {
    private options: LODSystemOptions;

    constructor(options: LODSystemOptions) {
        this.options = options;
    }

    /**
     * Get LOD level for a building at (x, y) based on player/camera distance
     */
    getLODLevel(x: number, y: number): LODLevel {
        const player = this.options.getPlayerPosition();
        const dx = x - player.x;
        const dy = y - player.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const [d1, d2, d3] = this.options.lodDistances;
        if (dist < d1) return LODLevel.Full;
        if (dist < d2) return LODLevel.Simplified;
        if (dist < d3) return LODLevel.Placeholder;
        return LODLevel.None;
    }

    /**
     * Smooth transition helper (for future use)
     */
    getTransitionFactor(x: number, y: number): number {
        // Returns a value 0-1 for smooth LOD transitions (e.g., for fading)
        // Can be extended for more advanced blending
        const player = this.options.getPlayerPosition();
        const dx = x - player.x;
        const dy = y - player.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const [d1, d2, d3] = this.options.lodDistances;
        if (dist < d1) return 1;
        if (dist < d2) return (d2 - dist) / (d2 - d1);
        if (dist < d3) return (d3 - dist) / (d3 - d2);
        return 0;
    }
} 