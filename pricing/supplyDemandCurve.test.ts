import { calculatePrice, calculateWeightedDemand } from './supplyDemandCurve';
import { defaultCurveParams } from './curveConfig';

describe('Supply/Demand Curve', () => {
    it('calculates price for typical supply/demand', () => {
        const price = calculatePrice({
            inventoryLevel: 50,
            recentTransactions: 60,
            previousWeightedDemand: 55,
            params: { ...defaultCurveParams, basePrice: 100 }
        });
        expect(price).toBeGreaterThan(100);
    });

    it('returns base price for missing data', () => {
        const price = calculatePrice({
            inventoryLevel: NaN,
            recentTransactions: 60,
            previousWeightedDemand: 55,
            params: defaultCurveParams
        });
        expect(price).toBe(defaultCurveParams.basePrice);
    });

    it('handles zero supply (should increase price)', () => {
        const price = calculatePrice({
            inventoryLevel: 0,
            recentTransactions: 100,
            previousWeightedDemand: 80,
            params: defaultCurveParams
        });
        expect(price).toBeGreaterThan(defaultCurveParams.basePrice);
    });

    it('handles infinite demand (should cap at reasonable value)', () => {
        const price = calculatePrice({
            inventoryLevel: 10,
            recentTransactions: 1e6,
            previousWeightedDemand: 1e6,
            params: defaultCurveParams
        });
        expect(price).toBeGreaterThan(defaultCurveParams.basePrice);
        expect(price).toBeLessThan(1e6);
    });

    it('never returns price below 0.01', () => {
        const price = calculatePrice({
            inventoryLevel: 1e6,
            recentTransactions: 0,
            previousWeightedDemand: 0,
            params: defaultCurveParams
        });
        expect(price).toBeGreaterThanOrEqual(0.01);
    });

    it('calculates weighted demand correctly', () => {
        const weighted = calculateWeightedDemand(100, 50, 0.5);
        expect(weighted).toBe(75);
    });
}); 