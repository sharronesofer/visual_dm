from typing import Any, Dict, List


class POIIntegrationParams:
    poiType: POIType
    poiSubtype: POISubtype
    dangerLevel: float
    bounds: Dict[str, Any]
class BuildingPlacement:
    building: Building
    position: Location
    clusterId: str
    isSpecial?: bool
class POIIntegrationResult:
    buildings: List[BuildingPlacement]
    roads: Dict[str, Any]
class POIIntegrationSystem {
  static generateForPOI(params: POIIntegrationParams): \'POIIntegrationResult\' {
    const { poiType, poiSubtype, dangerLevel, bounds, thematicElements, specialBuildings } = params
    const buildings: List[BuildingPlacement] = []
    const roads: Dict[str, Any][] = []
    if (poiType === POIType.SETTLEMENT) {
      const baseCount = poiSubtype === POISubtype.CITY ? 20 : poiSubtype === POISubtype.TOWN ? 10 : 5
      const dangerMod = Math.max(1, 1 + (dangerLevel - 5) * 0.1)
      const totalBuildings = Math.round(baseCount * dangerMod)
      const clusterCenters: List[Location] = [
        { x: bounds.x + bounds.width / 2, y: bounds.y + bounds.height / 2, z: 0 },
        { x: bounds.x + bounds.width / 3, y: bounds.y + bounds.height / 3, z: 0 },
        { x: bounds.x + 2 * bounds.width / 3, y: bounds.y + 2 * bounds.height / 3, z: 0 }
      ]
      let buildingIdx = 0
      for (let i = 0; i < totalBuildings; i++) {
        let building
        let position: Location
        let clusterId = ''
        let isSpecial = false
        if (i < 4) {
          switch (i) {
            case 0:
              building = createInn({ name: 'Central Inn', dimensions: Dict[str, Any], ...thematicElements })
              break
            case 1:
              building = createTavern({ name: 'Central Tavern', dimensions: Dict[str, Any], ...thematicElements })
              break
            case 2:
              building = createShop({ name: 'Central Shop', dimensions: Dict[str, Any], ...thematicElements })
              break
            case 3:
              building = createGuildHall({ name: 'Guild Hall', dimensions: Dict[str, Any], ...thematicElements })
              break
          }
          position = { ...clusterCenters[0], x: clusterCenters[0].x + (i - 1) * 5, y: clusterCenters[0].y + (i - 1) * 3, z: 0 }
          clusterId = 'central'
        } else if (i < totalBuildings - 2) {
          building = createNPCHome({ name: `Home ${i}`, dimensions: Dict[str, Any], ...thematicElements })
          const angle = (2 * Math.PI * (i - 4)) / (totalBuildings - 6)
          position = {
            x: clusterCenters[1].x + Math.cos(angle) * 10,
            y: clusterCenters[1].y + Math.sin(angle) * 8,
            z: 0
          }
          clusterId = 'residential'
        } else {
          building = createGuildHall({ name: `Special ${i}`, dimensions: Dict[str, Any], ...thematicElements })
          position = { ...clusterCenters[2], x: clusterCenters[2].x + (i - (totalBuildings - 2)) * 6, y: clusterCenters[2].y, z: 0 }
          clusterId = 'special'
          isSpecial = true
        }
        buildings.push({ building, position, clusterId, isSpecial })
        buildingIdx++
      }
      for (let i = 1; i < clusterCenters.length; i++) {
        roads.push({ from: clusterCenters[0], to: clusterCenters[i], type: 'PRIMARY' })
      }
      for (const b of buildings.filter(b => b.clusterId === 'residential')) {
        roads.push({ from: b.position, to: clusterCenters[0], type: 'SECONDARY' })
      }
    }
    return { buildings, roads }
  }
} 