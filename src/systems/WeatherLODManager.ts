// Define WeatherLODConfig locally (matching structure from weather.ts)
export type LODLevel = 'ultra' | 'high' | 'medium' | 'low' | 'verylow';

export interface WeatherLODProfile {
    maxParticles: number;
    textureResolution: number;
    shaderComplexity: number;
    drawDistance: number;
    minDistance: number;
}

export interface WeatherLODConfig {
    thresholds: {
        frameTime: Record<LODLevel, number>;
        memoryUsage: Record<LODLevel, number>;
        gpuScore?: Record<LODLevel, number>;
    };
    profiles: Record<string, Record<LODLevel, WeatherLODProfile>>;
    transitionSmoothing: number;
    hardwareProfiles?: Record<string, Partial<WeatherLODConfig>>;
}

export class WeatherLODManager {
    private config: WeatherLODConfig;
    // ... other properties and methods ...

    /**
     * Set LOD thresholds at runtime (for config/preset updates).
     */
    public setThresholds(thresholds: WeatherLODConfig['thresholds']) {
        this.config.thresholds = { ...thresholds };
        // Optionally, trigger recalculation or smoothing here
    }

    // ... rest of the class ...
} 