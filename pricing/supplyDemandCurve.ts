// pricing/supplyDemandCurve.ts

/**
 * Core supply/demand curve logic for dynamic pricing.
 * Uses a sigmoid function and time-weighted averaging for demand/supply.
 */

export interface CurveParams {
    basePrice: number;
    k: number; // max adjustment factor
    a: number; // steepness
    equilibrium: number; // equilibrium point (demand-supply offset)
    decayAlpha: number; // time-weighting factor (0-1)
}

export interface PriceInput {
    inventoryLevel: number;
    recentTransactions: number;
    previousWeightedDemand: number;
    params: CurveParams;
}

/**
 * Calculate the weighted demand using exponential decay.
 */
export function calculateWeightedDemand(currentDemand: number, previousWeighted: number, alpha: number): number {
    return currentDemand * alpha + previousWeighted * (1 - alpha);
}

/**
 * Calculate price using a sigmoid supply/demand curve.
 * Handles edge cases for new/rare items and missing data.
 */
export function calculatePrice({
    inventoryLevel,
    recentTransactions,
    previousWeightedDemand,
    params
}: PriceInput): number {
    // Handle edge cases: new/rare items
    if (isNaN(inventoryLevel) || isNaN(recentTransactions)) {
        return params.basePrice;
    }
    // Weighted demand
    const weightedDemand = calculateWeightedDemand(recentTransactions, previousWeightedDemand, params.decayAlpha);
    // Sigmoid price adjustment
    const x = weightedDemand - inventoryLevel - params.equilibrium;
    const adjustment = params.k / (1 + Math.exp(-params.a * x));
    const price = params.basePrice * (1 + adjustment);
    // Ensure price is not negative or zero
    return Math.max(price, 0.01);
} 