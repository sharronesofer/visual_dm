/**
 * Simple feature flag utility for runtime toggling of features.
 */
export type FeatureFlag = string;

const flags: Record<FeatureFlag, boolean> = {};

/**
 * Check if a feature flag is enabled.
 */
export function isFeatureEnabled(flag: FeatureFlag): boolean {
    return !!flags[flag];
}

/**
 * Set a feature flag value.
 */
export function setFeatureFlag(flag: FeatureFlag, enabled: boolean) {
    flags[flag] = enabled;
}

/**
 * Get all feature flags and their states.
 */
export function getAllFeatureFlags(): Record<FeatureFlag, boolean> {
    return { ...flags };
} 