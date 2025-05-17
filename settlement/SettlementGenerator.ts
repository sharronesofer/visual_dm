import { Settlement, SettlementType } from './Settlement';
import { GridLayoutGenerator, LayoutPatternResult } from './layout/GridLayoutGenerator';
import { RoadNetwork } from './layout/RoadNetwork';
import { ZoningSystem, ZoneType } from './zoning/ZoningSystem';
import { BuildingPlacer, PlacedBuilding } from './zoning/BuildingPlacer';
// POI integration
import { POIManager } from '../src/poi/managers/POIManager';
import { POIType, POISubtype, Coordinates } from '../src/poi/types/POITypes';
import { IPOI } from '../src/poi/interfaces/IPOI';

export interface GeneratedSettlement {
    settlement: Settlement;
    layout: LayoutPatternResult;
    roadNetwork: RoadNetwork;
    zoning: ZoningSystem;
    buildings: PlacedBuilding[];
    pois: IPOI[];
}

export function generateSettlement(
    type: SettlementType,
    buildingTypes: { type: string; zone: ZoneType; isLandmark?: boolean }[],
    thematicFeatures?: { type: POIType; subtype: POISubtype; position: Coordinates; name?: string; description?: string }[]
): GeneratedSettlement {
    // 1. Create settlement
    const settlement = new Settlement(type);
    // 2. Generate layout (can swap for other pattern generators)
    const layoutGen = new GridLayoutGenerator();
    const layout = layoutGen.generate(settlement);
    // 3. Generate road network
    const roadNetwork = new RoadNetwork(layout, settlement);
    // 4. Generate zoning
    const zoning = new ZoningSystem(layout.grid.length);
    zoning.generateZones(layout, roadNetwork);
    // 5. Place buildings
    const placer = new BuildingPlacer();
    placer.placeBuildings(zoning, settlement, roadNetwork, buildingTypes);
    // 6. Integrate POIs and thematic elements
    const poiManager = POIManager.getInstance();
    const pois: IPOI[] = [];
    // Add POIs for landmark buildings
    placer.placed.forEach(b => {
        if (b.isLandmark) {
            const poi = poiManager.createPOI(
                POIType.LANDMARK,
                POISubtype.BUILDING,
                {
                    position: b.position,
                    name: b.type,
                    description: b.type + ' landmark',
                }
            );
            pois.push(poi);
        }
    });
    // Add thematic features as POIs
    if (thematicFeatures) {
        thematicFeatures.forEach(f => {
            const poi = poiManager.createPOI(
                f.type,
                f.subtype,
                {
                    position: f.position,
                    name: f.name,
                    description: f.description,
                }
            );
            pois.push(poi);
        });
    }
    // 7. Return all data
    return {
        settlement,
        layout,
        roadNetwork,
        zoning,
        buildings: placer.placed,
        pois,
    };
}

// Example usage (for test/demo):
// const result = generateSettlement(SettlementType.TOWN, [
//   { type: 'temple', zone: ZoneType.SPECIAL, isLandmark: true },
//   { type: 'house', zone: ZoneType.RESIDENTIAL },
// ]); 