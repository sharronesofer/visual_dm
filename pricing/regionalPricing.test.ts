import { expect } from 'chai';
import {
    getRegion,
    calculateTransportCost,
    applyRegionalModifiers,
    applyRegionalEvent,
    smoothTransition,
    calculateRegionalPrice
} from './regionalPricing.js';
import { eventTemplates } from './regionConfig.js';

describe('Regional Pricing', () => {
    it('finds a region by id', () => {
        const region = getRegion('north');
        expect(region).to.exist;
        if (region) {
            expect(region.name).to.equal('Northern Province');
        }
    });

    it('calculates transport cost for heavy, fragile item', () => {
        const cost = calculateTransportCost(100, { weight: 10, volume: 2, fragile: true });
        expect(cost).to.be.greaterThan(0);
    });

    it('applies regional modifiers', () => {
        const price = applyRegionalModifiers(100, 'central');
        expect(price).to.be.greaterThan(100);
    });

    it('applies regional event modifier', () => {
        const price = applyRegionalEvent(100, 'north', [eventTemplates[0]]);
        expect(price).to.equal(120);
    });

    it('smoothly transitions between region prices', () => {
        const price = smoothTransition(100, 200, 2, 10);
        expect(price).to.be.greaterThan(100);
        expect(price).to.be.lessThan(200);
    });

    it('calculates full regional price pipeline', () => {
        const price = calculateRegionalPrice({
            basePrice: 100,
            regionId: 'central',
            item: { weight: 5, volume: 1, fragile: false },
            distanceKm: 50,
            activeEvents: [eventTemplates[2]],
            adjacentRegionId: 'north',
            distanceToBoundary: 3,
            smoothingRange: 10
        });
        expect(price).to.be.greaterThan(100);
    });

    it('never returns price below 0.01', () => {
        const price = calculateRegionalPrice({
            basePrice: 0.001,
            regionId: 'south',
            item: { weight: 0, volume: 0, fragile: false },
            distanceKm: 0,
            activeEvents: [],
        });
        expect(price).to.be.greaterThanOrEqual(0.01);
    });
}); 