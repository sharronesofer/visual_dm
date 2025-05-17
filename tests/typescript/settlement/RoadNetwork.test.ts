import { RoadNetwork } from '../../../settlement/layout/RoadNetwork';
import { GridLayoutGenerator } from '../../../settlement/layout/GridLayoutGenerator';
import { ClusteredLayoutGenerator } from '../../../settlement/layout/ClusteredLayoutGenerator';
import { Settlement, SettlementType } from '../../../settlement/Settlement';
import path from 'path';

describe('RoadNetwork', () => {
    beforeAll(() => {
        Settlement.loadTypeParameters(path.resolve(__dirname, '../../../settlement/settlementTypes.config.json'));
    });

    it('should build a fully connected road network for a grid pattern', () => {
        const settlement = new Settlement(SettlementType.TOWN);
        const generator = new GridLayoutGenerator();
        const pattern = generator.generate(settlement);
        const network = new RoadNetwork(pattern, settlement);
        expect(network.isFullyConnected()).toBe(true);
        // Should have main roads
        expect(network.edges.some(e => e.type === 'main')).toBe(true);
    });

    it('should assign side streets and alleys for a city', () => {
        const settlement = new Settlement(SettlementType.CITY);
        const generator = new ClusteredLayoutGenerator();
        const pattern = generator.generate(settlement);
        const network = new RoadNetwork(pattern, settlement);
        expect(network.edges.some(e => e.type === 'side')).toBe(true);
        expect(network.edges.some(e => e.type === 'alley')).toBe(true);
    });

    it('should not add alleys for a village', () => {
        const settlement = new Settlement(SettlementType.VILLAGE);
        const generator = new GridLayoutGenerator();
        const pattern = generator.generate(settlement);
        const network = new RoadNetwork(pattern, settlement);
        expect(network.edges.some(e => e.type === 'alley')).toBe(false);
    });
}); 