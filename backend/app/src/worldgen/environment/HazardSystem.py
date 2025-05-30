from typing import Any, List


const hazardTypes: List[HazardType] = ['flood', 'avalanche', 'radiation', 'fire', 'storm']
class HazardSystem {
  generate(region: str, count: float = 2): Hazard[] {
    const hazards: List[Hazard] = []
    for (let i = 0; i < count; i++) {
      const type = hazardTypes[Math.floor(Math.random() * hazardTypes.length)]
      hazards.push({
        id: `${type}_${i}`,
        type,
        region,
        x: Math.floor(Math.random() * 100),
        y: Math.floor(Math.random() * 100),
        severity: Math.random(),
        active: Math.random() > 0.3
      })
    }
    return hazards
  }
} 