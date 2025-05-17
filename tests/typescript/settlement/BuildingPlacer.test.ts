import { BuildingPlacer } from '../../../settlement/zoning/BuildingPlacer';
import { ZoningSystem, ZoneType } from '../../../settlement/zoning/ZoningSystem';
import { RoadNetwork } from '../../../settlement/layout/RoadNetwork';
import { LayoutPatternResult } from '../../../settlement/layout/GridLayoutGenerator';
import { Settlement, SettlementType } from '../../../settlement/Settlement';
import path from 'path';

describe('BuildingPlacer', () => {
    beforeAll(() => {
        Settlement.loadTypeParameters(path.resolve(__dirname, '../../../settlement/settlementTypes.config.json'));
    });

    it('should place landmarks in special or commercial zones', () => {
        const settlement = new Settlement(SettlementType.TOWN);
        const size = settlement.size * 5;
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
        const placer = new BuildingPlacer();
        placer.placeBuildings(zoning, settlement, roadNetwork, [
            { type: 'temple', zone: ZoneType.SPECIAL, isLandmark: true },
            { type: 'house', zone: ZoneType.RESIDENTIAL },
        ]);
        // Landmark should be in special or commercial zone
        const landmark = placer.placed.find(b => b.isLandmark);
        expect(landmark).toBeDefined();
        expect([ZoneType.SPECIAL, ZoneType.COMMERCIAL]).toContain(landmark!.zone);
        // House should be in residential zone
        const house = placer.placed.find(b => b.type === 'house');
        expect(house).toBeDefined();
        expect(house!.zone).toBe(ZoneType.RESIDENTIAL);
    });

    it('should align buildings to face roads', () => {
        const settlement = new Settlement(SettlementType.TOWN);
        const size = settlement.size * 5;
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
        const placer = new BuildingPlacer();
        placer.placeBuildings(zoning, settlement, roadNetwork, [
            { type: 'house', zone: ZoneType.RESIDENTIAL },
        ]);
        const house = placer.placed.find(b => b.type === 'house');
        expect(house).toBeDefined();
        // Should be aligned to one of the four cardinal directions
        expect([0, 90, 180, 270]).toContain(house!.orientation);
    });
}); 