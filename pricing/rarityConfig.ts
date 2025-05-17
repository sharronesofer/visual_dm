/**
 * Default rarity multipliers for item pricing.
 * Admins can adjust these values as needed.
 */
export interface RarityMultiplier {
    min: number;
    max: number;
}

export const rarityMultipliers: Record<string, RarityMultiplier> = {
    common: { min: 1, max: 1 },
    uncommon: { min: 1.5, max: 2 },
    rare: { min: 3, max: 5 },
    epic: { min: 7, max: 10 },
    legendary: { min: 15, max: 25 },
    unique: { min: 30, max: 100 } // for special/limited items
}; 