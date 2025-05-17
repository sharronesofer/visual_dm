/**
 * Configurable thresholds and alert levels for market manipulation detection.
 */
export const volumeSpikeThreshold = 5; // e.g., 5x normal volume
export const priceMoveZScoreThreshold = 3; // z-score for abnormal price movement
export const repetitiveTradeThreshold = 10; // e.g., 10 similar trades in a short window

export const alertLevels = {
    info: 1,
    warning: 2,
    critical: 3
}; 