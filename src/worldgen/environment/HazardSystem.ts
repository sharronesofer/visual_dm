import { Hazard, HazardType } from './types';

const hazardTypes: HazardType[] = ['flood', 'avalanche', 'radiation', 'fire', 'storm'];

export class HazardSystem {
  generate(region: string, count: number = 2): Hazard[] {
    const hazards: Hazard[] = [];
    for (let i = 0; i < count; i++) {
      const type = hazardTypes[Math.floor(Math.random() * hazardTypes.length)];
      hazards.push({
        id: `${type}_${i}`,
        type,
        region,
        x: Math.floor(Math.random() * 100),
        y: Math.floor(Math.random() * 100),
        severity: Math.random(),
        active: Math.random() > 0.3
      });
    }
    return hazards;
  }
} 