import { Settlement, SettlementType } from '../../../settlement/Settlement';
import { ClusteredLayoutGenerator } from '../../../settlement/layout/ClusteredLayoutGenerator';
import path from 'path';

describe('ClusteredLayoutGenerator', () => {
    beforeAll(() => {
        Settlement.loadTypeParameters(path.resolve(__dirname, '../../../settlement/settlementTypes.config.json'));
    });

    it('should generate the correct number of clusters for a TOWN', () => {
        const settlement = new Settlement(SettlementType.TOWN);
        const generator = new ClusteredLayoutGenerator();
        const result = generator.generate(settlement);
        // Count unique cluster ids in the grid (excluding 0)
        const clusterIds = new Set<number>();
        for (const row of result.grid) {
            for (const cell of row) {
                if (cell > 0) clusterIds.add(cell);
            }
        }
        expect(clusterIds.size >= settlement.size + 1).toBeTruthy();
    });

    it('should create organic connections between clusters', () => {
        const settlement = new Settlement(SettlementType.CITY);
        const generator = new ClusteredLayoutGenerator();
        const result = generator.generate(settlement);
        // There should be at least as many main pathways as clusters - 1
        const mainPaths = result.pathways.filter(p => p.type === 'main');
        expect(mainPaths.length >= settlement.size).toBeTruthy();
    });
}); 