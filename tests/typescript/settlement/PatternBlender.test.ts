import { PatternBlender } from '../../../settlement/layout/PatternBlender';
import { GridLayoutGenerator } from '../../../settlement/layout/GridLayoutGenerator';
import { ClusteredLayoutGenerator } from '../../../settlement/layout/ClusteredLayoutGenerator';
import { Settlement, SettlementType } from '../../../settlement/Settlement';
import path from 'path';

describe('PatternBlender', () => {
    beforeAll(() => {
        Settlement.loadTypeParameters(path.resolve(__dirname, '../../../settlement/settlementTypes.config.json'));
    });

    it('should blend two patterns with equal weights', () => {
        const settlement = new Settlement(SettlementType.TOWN);
        const gridGen = new GridLayoutGenerator();
        const clusterGen = new ClusteredLayoutGenerator();
        const gridPattern = gridGen.generate(settlement);
        const clusterPattern = clusterGen.generate(settlement);
        const blended = PatternBlender.blend([gridPattern, clusterPattern], [1, 1]);
        expect(blended.grid.length).toBe(gridPattern.grid.length);
        expect(blended.grid[0].length).toBe(gridPattern.grid[0].length);
        // Should have pathways from both patterns
        const allPaths = [...gridPattern.pathways, ...clusterPattern.pathways];
        const blendedKeys = new Set(blended.pathways.map(p => `${p.x},${p.y},${p.type}`));
        for (const p of allPaths) {
            expect(blendedKeys.has(`${p.x},${p.y},${p.type}`)).toBeTruthy();
        }
    });

    it('should throw if patterns and weights length mismatch', () => {
        const settlement = new Settlement(SettlementType.VILLAGE);
        const gridGen = new GridLayoutGenerator();
        const gridPattern = gridGen.generate(settlement);
        expect(() => PatternBlender.blend([gridPattern], [1, 2])).toThrow();
    });
}); 