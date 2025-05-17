import { expect } from 'chai';
import {
    locationModifier,
    featureModifier,
    appreciationDepreciationModifier,
    calculateHousingPrice
} from './housingPricing.js';

describe('Housing Pricing', () => {
    it('calculates location modifier for premium zone and waterfront', () => {
        const mod = locationModifier({
            proximityToResource: 1,
            proximityToCity: 1,
            isWaterfront: true,
            zone: 'city_center'
        });
        expect(mod).to.be.greaterThan(1);
    });

    it('calculates feature modifier for large house with pool and garden', () => {
        const mod = featureModifier({ size: 200, rooms: 5, pool: true, garden: true });
        expect(mod).to.be.greaterThan(1);
    });

    it('applies appreciation for good condition', () => {
        const mod = appreciationDepreciationModifier({ yearsOld: 10, condition: 'good' });
        expect(mod).to.be.greaterThan(1);
    });

    it('applies depreciation for poor condition', () => {
        const mod = appreciationDepreciationModifier({ yearsOld: 10, condition: 'poor' });
        expect(mod).to.be.lessThan(1);
        expect(mod).to.be.greaterThanOrEqual(0.5);
    });

    it('calculates full housing price pipeline', () => {
        const price = calculateHousingPrice({
            basePrice: 100000,
            attributes: { size: 150, rooms: 4, pool: true },
            location: { proximityToResource: 0.8, proximityToCity: 1, isWaterfront: false, zone: 'suburb' },
            condition: { yearsOld: 5, condition: 'excellent' }
        });
        expect(price).to.be.greaterThan(100000);
    });

    it('never returns price below 1', () => {
        const price = calculateHousingPrice({
            basePrice: 10,
            attributes: { size: 0, rooms: 0 },
            location: { proximityToResource: 0, proximityToCity: 0, isWaterfront: false, zone: 'nowhere' },
            condition: { yearsOld: 100, condition: 'poor' }
        });
        expect(price).to.be.greaterThanOrEqual(1);
    });
}); 