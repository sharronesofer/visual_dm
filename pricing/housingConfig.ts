/**
 * Configurable weights and premium zone definitions for housing pricing.
 */

export const locationWeights: Record<string, number> = {
    resourceProximity: 1.2, // multiplier for proximity to resources
    cityProximity: 1.5,     // multiplier for proximity to cities
    waterfront: 2.0         // multiplier for waterfront locations
};

export const featureWeights: Record<string, number> = {
    size: 1.0,              // base multiplier per unit size
    rooms: 0.2,             // multiplier per room
    pool: 0.5,              // pool adds 50%
    garden: 0.3,            // garden adds 30%
    garage: 0.2             // garage adds 20%
};

export const premiumZones: string[] = [
    'city_center',
    'waterfront',
    'historic_district'
];

export const premiumZoneMultiplier: number = 2.5; // Premium zones get 2.5x price

export const appreciationRatePerYear: number = 0.03; // 3% appreciation per year
export const depreciationRatePerYear: number = 0.02; // 2% depreciation per year (for poor condition) 