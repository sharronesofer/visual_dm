import { Settlement, SettlementType } from '../../../settlement/Settlement';
import { RadialLayoutGenerator } from '../../../settlement/layout/RadialLayoutGenerator';
import path from 'path';

describe('RadialLayoutGenerator', () => {
    beforeAll(() => {
        Settlement.loadTypeParameters(path.resolve(__dirname, '../../../settlement/settlementTypes.config.json'));
    });

    it('should generate the correct number of rings for a TOWN', () => {
        const settlement = new Settlement(SettlementType.TOWN);
        const generator = new RadialLayoutGenerator();
        const result = generator.generate(settlement);
        // Count unique ring ids in the grid (excluding 0)
        const ringIds = new Set<number>();
        for (const row of result.grid) {
            for (const cell of row) {
                if (cell > 0) ringIds.add(cell);
            }
        }
        expect(ringIds.size).toBeGreaterThanOrEqual(settlement.size + 1);
    });

    it('should generate rays from the center', () => {
        const settlement = new Settlement(SettlementType.CITY);
        const generator = new RadialLayoutGenerator();
        const result = generator.generate(settlement);
        const size = Math.max(8, settlement.size * 6);
        const center = { x: Math.floor(size / 2), y: Math.floor(size / 2) };
        // There should be main pathways that start at or near the center
        const nearCenter = result.pathways.filter(p => Math.abs(p.x - center.x) <= 1 && Math.abs(p.y - center.y) <= 1);
        expect(nearCenter.length).toBeGreaterThan(0);
    });
}); 