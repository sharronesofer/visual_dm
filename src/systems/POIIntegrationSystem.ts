import { Building, BuildingMetadata, BuildingInterior, Dimensions, Location } from '../types/buildings';
import { POIType, POISubtype, Coordinates, ThematicElements } from '../poi/types/POITypes';
import { createInn, createShop, createTavern, createGuildHall, createNPCHome } from '../../utils/buildingFactory';
import { v4 as uuidv4 } from 'uuid';

interface POIIntegrationParams {
  poiType: POIType;
  poiSubtype: POISubtype;
  dangerLevel: number;
  bounds: { x: number; y: number; width: number; height: number };
  thematicElements: ThematicElements;
  specialBuildings?: string[];
}

interface BuildingPlacement {
  building: Building;
  position: Location;
  clusterId: string;
  isSpecial?: boolean;
}

interface POIIntegrationResult {
  buildings: BuildingPlacement[];
  roads: { from: Location; to: Location; type: 'PRIMARY' | 'SECONDARY' }[];
}

export class POIIntegrationSystem {
  static generateForPOI(params: POIIntegrationParams): POIIntegrationResult {
    // 1. Determine building types and counts based on POI type and danger level
    const { poiType, poiSubtype, dangerLevel, bounds, thematicElements, specialBuildings } = params;
    const buildings: BuildingPlacement[] = [];
    const roads: { from: Location; to: Location; type: 'PRIMARY' | 'SECONDARY' }[] = [];

    // Example: Social POI (settlement) - cluster buildings by function
    if (poiType === POIType.SETTLEMENT) {
      // Determine density and counts
      const baseCount = poiSubtype === POISubtype.CITY ? 20 : poiSubtype === POISubtype.TOWN ? 10 : 5;
      const dangerMod = Math.max(1, 1 + (dangerLevel - 5) * 0.1);
      const totalBuildings = Math.round(baseCount * dangerMod);

      // Cluster: central plaza (inn, tavern, shop, guild hall), residential, special
      const clusterCenters: Location[] = [
        { x: bounds.x + bounds.width / 2, y: bounds.y + bounds.height / 2, z: 0 },
        { x: bounds.x + bounds.width / 3, y: bounds.y + bounds.height / 3, z: 0 },
        { x: bounds.x + 2 * bounds.width / 3, y: bounds.y + 2 * bounds.height / 3, z: 0 }
      ];
      let buildingIdx = 0;
      for (let i = 0; i < totalBuildings; i++) {
        let building;
        let position: Location;
        let clusterId = '';
        let isSpecial = false;
        // Central cluster: inn, tavern, shop, guild hall
        if (i < 4) {
          switch (i) {
            case 0:
              building = createInn({ name: 'Central Inn', dimensions: { width: 4, height: 4 }, ...thematicElements });
              break;
            case 1:
              building = createTavern({ name: 'Central Tavern', dimensions: { width: 3, height: 3 }, ...thematicElements });
              break;
            case 2:
              building = createShop({ name: 'Central Shop', dimensions: { width: 3, height: 3 }, ...thematicElements });
              break;
            case 3:
              building = createGuildHall({ name: 'Guild Hall', dimensions: { width: 4, height: 4 }, ...thematicElements });
              break;
          }
          position = { ...clusterCenters[0], x: clusterCenters[0].x + (i - 1) * 5, y: clusterCenters[0].y + (i - 1) * 3, z: 0 };
          clusterId = 'central';
        } else if (i < totalBuildings - 2) {
          // Residential cluster
          building = createNPCHome({ name: `Home ${i}`, dimensions: { width: 2, height: 2 }, ...thematicElements });
          const angle = (2 * Math.PI * (i - 4)) / (totalBuildings - 6);
          position = {
            x: clusterCenters[1].x + Math.cos(angle) * 10,
            y: clusterCenters[1].y + Math.sin(angle) * 8,
            z: 0
          };
          clusterId = 'residential';
        } else {
          // Special/quest buildings
          building = createGuildHall({ name: `Special ${i}`, dimensions: { width: 3, height: 3 }, ...thematicElements });
          position = { ...clusterCenters[2], x: clusterCenters[2].x + (i - (totalBuildings - 2)) * 6, y: clusterCenters[2].y, z: 0 };
          clusterId = 'special';
          isSpecial = true;
        }
        buildings.push({ building, position, clusterId, isSpecial });
        buildingIdx++;
      }
      // Generate roads/paths between clusters and central plaza
      for (let i = 1; i < clusterCenters.length; i++) {
        roads.push({ from: clusterCenters[0], to: clusterCenters[i], type: 'PRIMARY' });
      }
      // Connect residential to central
      for (const b of buildings.filter(b => b.clusterId === 'residential')) {
        roads.push({ from: b.position, to: clusterCenters[0], type: 'SECONDARY' });
      }
    }
    // TODO: Add logic for DUNGEON, LANDMARK, RESOURCE, etc.
    // TODO: Add danger level influence on building types/density for other POI types
    // TODO: Add POI boundary enforcement, building replacement/evolution, and POI-specific variations
    return { buildings, roads };
  }
} 