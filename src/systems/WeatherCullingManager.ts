// WeatherCullingManager moved from WeatherEffectSystem.ts for testability and maintainability

import type { WeatherEffect } from '../core/interfaces/types/weather';

export enum WeatherEffectPriority {
    Critical = 3,
    High = 2,
    Medium = 1,
    Low = 0,
}

export interface WeatherCullingConfig {
    distanceThresholds: Record<string, number>; // effectType -> max distance
    priority: Record<string, WeatherEffectPriority>;
    frustumBuffer: number; // extra margin for frustum culling
    occlusionEnabled: boolean;
    smoothingMs: number; // fade in/out duration
}

export class WeatherCullingManager {
    private config: WeatherCullingConfig;
    private activeEffects: Map<string, WeatherEffect[]>; // regionId -> effects
    private camera: { isInFrustum: (pos: { x: number; y: number; z: number }, buffer: number) => boolean };
    private occlusionQuery: (effect: WeatherEffect) => boolean;
    private fadeTimers: Map<string, NodeJS.Timeout> = new Map();

    constructor(
        config: WeatherCullingConfig,
        activeEffects: Map<string, WeatherEffect[]>,
        camera: { isInFrustum: (pos: { x: number; y: number; z: number }, buffer: number) => boolean },
        occlusionQuery: (effect: WeatherEffect) => boolean
    ) {
        this.config = config;
        this.activeEffects = activeEffects;
        this.camera = camera;
        this.occlusionQuery = occlusionQuery;
    }

    // Main culling method: returns effects to keep for a region
    cull(regionId: string, cameraPos: { x: number; y: number; z: number }): WeatherEffect[] {
        const effects = this.activeEffects.get(regionId) || [];
        const kept: WeatherEffect[] = [];
        // Sort by priority (highest first)
        effects.sort((a, b) =>
            (this.config.priority[a.type] ?? WeatherEffectPriority.Medium) -
            (this.config.priority[b.type] ?? WeatherEffectPriority.Medium)
        );
        for (const effect of effects) {
            // Distance-based culling
            const dist = this.getEffectDistance(effect, cameraPos);
            const maxDist = this.config.distanceThresholds[effect.type] ?? 100;
            if (dist > maxDist) continue;
            // Frustum culling
            if (!this.camera.isInFrustum(this.getEffectPosition(effect), this.config.frustumBuffer)) continue;
            // Occlusion culling (if enabled)
            if (this.config.occlusionEnabled && !this.occlusionQuery(effect)) continue;
            // Temporal smoothing (fade in/out)
            // (For brevity, just add to kept; real fade logic would update effect alpha over time)
            kept.push(effect);
        }
        return kept;
    }

    // Example: get effect position (should be extended for real effect data)
    private getEffectPosition(effect: WeatherEffect): { x: number; y: number; z: number } {
        // Placeholder: assume effect has position property
        return (effect as any).position || { x: 0, y: 0, z: 0 };
    }

    // Example: compute distance from camera
    private getEffectDistance(effect: WeatherEffect, cameraPos: { x: number; y: number; z: number }): number {
        const pos = this.getEffectPosition(effect);
        return Math.sqrt(
            Math.pow(pos.x - cameraPos.x, 2) +
            Math.pow(pos.y - cameraPos.y, 2) +
            Math.pow(pos.z - cameraPos.z, 2)
        );
    }

    // Expose for debugging/visualization
    getConfig() { return this.config; }
    setConfig(config: WeatherCullingConfig) { this.config = config; }

    /**
     * Set culling distances at runtime (for config/preset updates).
     */
    public setDistances(distances: Record<string, number>) {
        this.config.distanceThresholds = { ...distances };
        // Optionally, trigger logic to re-cull effects
    }
} 