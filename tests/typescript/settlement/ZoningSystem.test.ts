import { ZoningSystem, ZoneType } from '../../../settlement/zoning/ZoningSystem';
import { RoadNetwork } from '../../../settlement/layout/RoadNetwork';
import { LayoutPatternResult } from '../../../settlement/layout/GridLayoutGenerator';
import { Settlement, SettlementType } from '../../../settlement/Settlement';
import path from 'path';

describe('ZoningSystem', () => {
    beforeAll(() => {
        Settlement.loadTypeParameters(path.resolve(__dirname, '../../../settlement/settlementTypes.config.json'));
    });

    it('should create a grid of correct size and assign zones', () => {
        const settlement = new Settlement(SettlementType.TOWN);
        const size = settlement.size * 5;
        // Mock pattern: empty grid, main roads at center row/col
        const pattern: LayoutPatternResult = {
            grid: Array.from({ length: size }, () => Array(size).fill(0)),
            pathways: [
                ...Array.from({ length: size }, (_, i) => ({ x: Math.floor(size / 2), y: i, type: 'main' as const })),
                ...Array.from({ length: size }, (_, i) => ({ x: i, y: Math.floor(size / 2), type: 'main' as const })),
            ],
            description: 'Mock grid',
        };
        const roadNetwork = new RoadNetwork(pattern, settlement);
        const zoning = new ZoningSystem(size);
        zoning.generateZones(pattern, roadNetwork);
        // Should have special zone at center
        expect(zoning.grid[Math.floor(size / 2)][Math.floor(size / 2)].zone).toBe(ZoneType.SPECIAL);
        // Should have commercial zones near main roads
        const commercialCount = zoning.grid.flat().filter(cell => cell.zone === ZoneType.COMMERCIAL).length;
        expect(commercialCount).toBeGreaterThan(0);
        // Should have industrial zones at periphery
        const edge = 0;
        expect(zoning.grid[edge][edge].zone).toBe(ZoneType.INDUSTRIAL);
        // Density should decrease from center to edge
        const centerDensity = zoning.grid[Math.floor(size / 2)][Math.floor(size / 2)].density;
        const edgeDensity = zoning.grid[edge][edge].density;
        expect(centerDensity).toBeGreaterThan(edgeDensity);
    });
}); 