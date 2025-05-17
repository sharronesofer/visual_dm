import { expect } from 'chai';
import {
    movingAverage,
    standardDeviation,
    zScore,
    detectVolumeSpike,
    detectPriceAnomaly,
    detectRepetitiveTrades,
    runManipulationDetection,
    CircuitBreaker
} from './marketManipulation.js';

const now = Date.now();

function makeTrades({ n, price = 100, volume = 10, traderId = 'A', priceStep = 0, volumeStep = 0 }) {
    return Array.from({ length: n }, (_, i) => ({
        timestamp: now + i * 1000,
        price: price + i * priceStep,
        volume: volume + i * volumeStep,
        itemId: 'item1',
        regionId: 'north',
        traderId
    }));
}

describe('Market Manipulation Detection', () => {
    it('computes moving average and stddev', () => {
        const vals = [1, 2, 3, 4, 5];
        expect(movingAverage(vals, 5)).to.equal(3);
        expect(standardDeviation(vals, 5)).to.be.closeTo(1.414, 0.01);
    });

    it('computes z-score', () => {
        expect(zScore(10, 5, 2)).to.equal(2.5);
    });

    it('detects volume spike', () => {
        const trades = makeTrades({ n: 20 }).concat(makeTrades({ n: 1, volume: 1000 }));
        const result = detectVolumeSpike(trades);
        expect(result).to.exist;
        if (result) {
            expect(result.reason).to.include('Volume spike');
        }
    });

    it('detects price anomaly', () => {
        const trades = makeTrades({ n: 20 }).concat(makeTrades({ n: 1, price: 1000 }));
        const result = detectPriceAnomaly(trades);
        expect(result).to.exist;
        if (result) {
            expect(result.reason).to.include('Abnormal price movement');
        }
    });

    it('detects repetitive trades', () => {
        const trades = makeTrades({ n: 10, traderId: 'B' });
        const result = detectRepetitiveTrades(trades);
        expect(result).to.exist;
        if (result) {
            expect(result.reason).to.include('Repetitive trades');
        }
    });

    it('runs full detection pipeline', () => {
        const trades = makeTrades({ n: 20 })
            .concat(makeTrades({ n: 1, volume: 1000 }))
            .concat(makeTrades({ n: 10, traderId: 'C' }));
        const results = runManipulationDetection(trades);
        expect(results.length).to.be.greaterThan(0);
    });

    it('circuit breaker trips and resets', () => {
        const cb = new CircuitBreaker();
        expect(cb.tripped).to.be.false;
        cb.trip('Test reason');
        expect(cb.tripped).to.be.true;
        expect(cb.reason).to.equal('Test reason');
        cb.reset();
        expect(cb.tripped).to.be.false;
    });
}); 