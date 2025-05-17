import { HistoricalGrowthSimulator, GrowthPhase } from '../../../settlement/layout/HistoricalGrowthSimulator';
import { GridLayoutGenerator } from '../../../settlement/layout/GridLayoutGenerator';
import { ClusteredLayoutGenerator } from '../../../settlement/layout/ClusteredLayoutGenerator';
import { RadialLayoutGenerator } from '../../../settlement/layout/RadialLayoutGenerator';
import { OrganicLayoutGenerator } from '../../../settlement/layout/OrganicLayoutGenerator';
import { Settlement, SettlementType } from '../../../settlement/Settlement';
import path from 'path';

describe('HistoricalGrowthSimulator', () => {
    beforeAll(() => {
        Settlement.loadTypeParameters(path.resolve(__dirname, '../../../settlement/settlementTypes.config.json'));
    });

    it('should blend multiple growth phases in sequence', () => {
        const settlement = new Settlement(SettlementType.CITY);
        const phases: GrowthPhase[] = [
            { generator: new GridLayoutGenerator(), weight: 2 },
            { generator: new ClusteredLayoutGenerator(), weight: 1 },
            { generator: new RadialLayoutGenerator(), weight: 1 },
            { generator: new OrganicLayoutGenerator(), weight: 1 },
        ];
        const result = HistoricalGrowthSimulator.simulateGrowth(settlement, phases);
        expect(result.grid.length).toBeGreaterThan(0);
        expect(result.grid[0].length).toBe(result.grid.length);
        expect(result.pathways.length).toBeGreaterThan(0);
        expect(result.description).toContain('Blended pattern');
    });

    it('should throw if no phases are provided', () => {
        const settlement = new Settlement(SettlementType.VILLAGE);
        expect(() => HistoricalGrowthSimulator.simulateGrowth(settlement, [])).toThrow();
    });
}); 