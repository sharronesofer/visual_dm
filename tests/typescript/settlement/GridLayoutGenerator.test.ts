import { Settlement, SettlementType } from '../../../settlement/Settlement';
import { GridLayoutGenerator } from '../../../settlement/layout/GridLayoutGenerator';
import path from 'path';

describe('GridLayoutGenerator', () => {
    beforeAll(() => {
        Settlement.loadTypeParameters(path.resolve(__dirname, '../../../settlement/settlementTypes.config.json'));
    });

    it('should generate a grid of correct size for a VILLAGE', () => {
        const settlement = new Settlement(SettlementType.VILLAGE);
        const generator = new GridLayoutGenerator();
        const result = generator.generate(settlement);
        expect(result.grid.length).toBeGreaterThanOrEqual(4);
        expect(result.grid.length).toBe(settlement.size * 5);
        expect(result.grid[0].length).toBe(result.grid.length);
    });

    it('should place main roads every 3 blocks', () => {
        const settlement = new Settlement(SettlementType.TOWN);
        const generator = new GridLayoutGenerator();
        const result = generator.generate(settlement);
        const size = settlement.size * 5;
        // Check that there are main roads at every 3rd index
        for (let i = 0; i < size; i += 3) {
            // There should be a main road at (i, 0)
            expect(result.pathways.some(p => p.x === i && p.y === 0 && p.type === 'main')).toBe(true);
            // There should be a main road at (0, i)
            expect(result.pathways.some(p => p.x === 0 && p.y === i && p.type === 'main')).toBe(true);
        }
    });
}); 