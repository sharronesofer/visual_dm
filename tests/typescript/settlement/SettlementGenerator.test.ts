import { generateSettlement } from '../../../settlement/SettlementGenerator';
import { SettlementType } from '../../../settlement/Settlement';
import { ZoneType } from '../../../settlement/zoning/ZoningSystem';
import { POIType, POISubtype } from '../../../src/poi/types/POITypes';

// Use Chai for assertions
import { expect } from 'chai';

describe('SettlementGenerator', () => {
    it('should generate a complete settlement with all components', () => {
        const result = generateSettlement(SettlementType.TOWN, [
            { type: 'temple', zone: ZoneType.SPECIAL, isLandmark: true },
            { type: 'house', zone: ZoneType.RESIDENTIAL },
            { type: 'market', zone: ZoneType.COMMERCIAL },
        ]);
        // Check core objects
        expect(result.settlement).to.exist;
        expect(result.layout).to.exist;
        expect(result.roadNetwork).to.exist;
        expect(result.zoning).to.exist;
        expect(result.buildings.length).to.be.greaterThan(0);
        // Check that landmark is placed in special/commercial zone
        const landmark = result.buildings.find(b => b.isLandmark);
        expect(landmark).to.exist;
        expect([ZoneType.SPECIAL, ZoneType.COMMERCIAL]).to.include(landmark!.zone);
        // Check that house is in residential zone
        const house = result.buildings.find(b => b.type === 'house');
        expect(house).to.exist;
        expect(house!.zone).to.equal(ZoneType.RESIDENTIAL);
        // Check that market is in commercial zone
        const market = result.buildings.find(b => b.type === 'market');
        expect(market).to.exist;
        expect(market!.zone).to.equal(ZoneType.COMMERCIAL);
        // POIs for landmarks
        expect(result.pois).to.exist;
        expect(result.pois.length).to.be.greaterThan(0);
        expect(result.pois.some(poi => poi.type === POIType.LANDMARK)).to.be.true;
    });

    it('should create POIs for thematic features', () => {
        const thematicFeatures = [
            {
                type: POIType.LANDMARK,
                subtype: POISubtype.MONUMENT,
                position: { x: 10, y: 0, z: 10, level: 0 },
                name: 'Obelisk',
                description: 'Ancient obelisk',
            },
        ];
        const result = generateSettlement(
            SettlementType.TOWN,
            [
                { type: 'temple', zone: ZoneType.SPECIAL, isLandmark: true },
                { type: 'house', zone: ZoneType.RESIDENTIAL },
            ],
            thematicFeatures
        );
        // Should include both landmark and thematic POIs
        expect(result.pois.length).to.be.greaterThanOrEqual(2);
        expect(result.pois.some(poi => poi.name === 'Obelisk')).to.be.true;
        expect(result.pois.some(poi => poi.type === POIType.LANDMARK)).to.be.true;
    });
}); 