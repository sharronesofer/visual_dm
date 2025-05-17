import { priceBoundaries } from './boundaryConfig.js';

/**
 * Soft-limits a price as it approaches min/max boundaries using interpolation.
 * Logs when price is at or near a boundary.
 */
export function enforcePriceBoundaries(price: number, category: string, log: (msg: string) => void = console.log): number {
    const bounds = priceBoundaries[category] || { min: 1, max: 1e6 };
    const threshold = 0.05 * (bounds.max - bounds.min); // 5% near boundary
    let adjusted = price;

    // Soft-limiting: interpolate as price nears boundaries
    if (price < bounds.min + threshold) {
        adjusted = bounds.min + (price - bounds.min) * 0.5;
        if (adjusted < bounds.min) adjusted = bounds.min;
        if (price <= bounds.min) log(`[Boundary] Price at or below min for ${category}: ${price}`);
        else if (price < bounds.min + threshold) log(`[Boundary] Price near min for ${category}: ${price}`);
    } else if (price > bounds.max - threshold) {
        adjusted = bounds.max - (bounds.max - price) * 0.5;
        if (adjusted > bounds.max) adjusted = bounds.max;
        if (price >= bounds.max) log(`[Boundary] Price at or above max for ${category}: ${price}`);
        else if (price > bounds.max - threshold) log(`[Boundary] Price near max for ${category}: ${price}`);
    }
    // Clamp to hard boundaries
    if (adjusted < bounds.min) adjusted = bounds.min;
    if (adjusted > bounds.max) adjusted = bounds.max;
    return adjusted;
} 