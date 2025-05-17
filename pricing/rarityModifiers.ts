import { rarityMultipliers } from './rarityConfig.js';

/**
 * Applies a rarity multiplier to the price.
 * For unique/limited items, a scarcity metric (0-1) can be used to interpolate within the range.
 * @param price - The base price
 * @param rarity - Rarity tier (e.g., 'common', 'rare', 'unique')
 * @param scarcity - Optional, 0 (least scarce) to 1 (most scarce) for unique/limited items
 */
export function applyRarityModifier(price: number, rarity: string, scarcity?: number): number {
    const mult = rarityMultipliers[rarity] || { min: 1, max: 1 };
    let factor = mult.min;
    if (rarity === 'unique' && typeof scarcity === 'number') {
        // Interpolate within the unique range
        factor = mult.min + (mult.max - mult.min) * Math.max(0, Math.min(1, scarcity));
    } else if (mult.max > mult.min) {
        // For other tiers, use the average
        factor = (mult.min + mult.max) / 2;
    }
    return price * factor;
} 