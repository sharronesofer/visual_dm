import { enforcePriceBoundaries } from './priceBoundaries.js';
import { expect } from 'chai';

const category = 'weapons';

describe('enforcePriceBoundaries', () => {
    it('returns price within boundaries unchanged', () => {
        const price = enforcePriceBoundaries(200, category, () => { });
        expect(price).to.equal(200);
    });

    it('soft-limits price near min boundary', () => {
        const min = 50;
        const nearMin = min + 2;
        let logMsg = '';
        const price = enforcePriceBoundaries(nearMin, category, msg => { logMsg = msg; });
        expect(price).to.be.greaterThanOrEqual(min);
        expect(logMsg).to.contain('near min');
    });

    it('soft-limits price near max boundary', () => {
        const max = 500;
        const nearMax = max - 2;
        let logMsg = '';
        const price = enforcePriceBoundaries(nearMax, category, msg => { logMsg = msg; });
        expect(price).to.be.lessThanOrEqual(max);
        expect(logMsg).to.contain('near max');
    });

    it('clamps price below min', () => {
        let logMsg = '';
        const price = enforcePriceBoundaries(10, category, msg => { logMsg = msg; });
        expect(price).to.be.greaterThanOrEqual(50);
        expect(logMsg).to.contain('at or below min');
    });

    it('clamps price above max', () => {
        let logMsg = '';
        const price = enforcePriceBoundaries(1000, category, msg => { logMsg = msg; });
        expect(price).to.be.lessThanOrEqual(500);
        expect(logMsg).to.contain('at or above max');
    });
}); 