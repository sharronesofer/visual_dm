/**
 * Service to manage and report system degradation mode for POI Evolution System.
 */
export type DegradedMode = 'normal' | 'degraded' | 'critical-only';

const allowedFeatures: Record<DegradedMode, Set<string>> = {
    normal: new Set<string>(), // All features allowed
    degraded: new Set<string>(), // Only critical features allowed
    'critical-only': new Set<string>(), // Only essential features allowed
};

let currentMode: DegradedMode = 'normal';

/**
 * Set the current degraded mode.
 */
export function setDegradedMode(mode: DegradedMode) {
    currentMode = mode;
}

/**
 * Get the current degraded mode.
 */
export function getDegradedMode(): DegradedMode {
    return currentMode;
}

/**
 * Register allowed features for a given mode.
 */
export function registerAllowedFeatures(mode: DegradedMode, features: string[]) {
    allowedFeatures[mode] = new Set(features);
}

/**
 * Check if a feature is allowed in the current mode.
 */
export function isFeatureAllowed(feature: string): boolean {
    if (currentMode === 'normal') return true;
    return allowedFeatures[currentMode].has(feature);
}

/**
 * Get current status for health checks.
 */
export function getDegradedStatus() {
    return {
        mode: currentMode,
        allowedFeatures: Array.from(allowedFeatures[currentMode]),
    };
} 