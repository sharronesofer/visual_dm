/**
 * Default price boundaries for item categories.
 * Admins can adjust these values as needed.
 */
export interface PriceBoundary {
    min: number;
    max: number;
}

export const priceBoundaries: Record<string, PriceBoundary> = {
    weapons: { min: 50, max: 500 },
    armor: { min: 40, max: 400 },
    consumables: { min: 5, max: 100 },
    housing: { min: 1000, max: 10000 },
    misc: { min: 1, max: 1000 }
}; 