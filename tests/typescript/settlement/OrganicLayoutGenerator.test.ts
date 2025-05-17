import { Settlement, SettlementType } from '../../../settlement/Settlement';
import { OrganicLayoutGenerator } from '../../../settlement/layout/OrganicLayoutGenerator';
import path from 'path';

describe('OrganicLayoutGenerator', () => {
    beforeAll(() => {
        Settlement.loadTypeParameters(path.resolve(__dirname, '../../../settlement/settlementTypes.config.json'));
    });

    it('should generate the correct number of organic centers for a TOWN', () => {
        const settlement = new Settlement(SettlementType.TOWN);
        const generator = new OrganicLayoutGenerator();
        const result = generator.generate(settlement);
        // Count unique cluster ids in the grid (excluding 0)
        const clusterIds = new Set<number>();
        for (const row of result.grid) {
            for (const cell of row) {
                if (cell > 0) clusterIds.add(cell);
            }
        }
        expect(clusterIds.size >= settlement.size).toBeTruthy();
    });

    it('should create winding paths between centers', () => {
        const settlement = new Settlement(SettlementType.CITY);
        const generator = new OrganicLayoutGenerator();
        const result = generator.generate(settlement);
        // There should be main pathways
        const mainPaths = result.pathways.filter(p => p.type === 'main');
        expect(mainPaths.length > 0).toBeTruthy();
    });
}); 