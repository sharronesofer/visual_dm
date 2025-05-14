import { FactionType, SecurityFeature } from './types';

const baseSecurity: Record<FactionType, { type: string; baseStrength: number }[]> = {
  guild: [
    { type: 'guard', baseStrength: 2 },
    { type: 'lock', baseStrength: 1 }
  ],
  order: [
    { type: 'sentinel', baseStrength: 3 },
    { type: 'alarm', baseStrength: 2 }
  ],
  syndicate: [
    { type: 'trap', baseStrength: 2 },
    { type: 'hidden_guard', baseStrength: 2 }
  ],
  militia: [
    { type: 'barricade', baseStrength: 3 },
    { type: 'patrol', baseStrength: 2 }
  ],
  cult: [
    { type: 'curse', baseStrength: 3 },
    { type: 'watcher', baseStrength: 1 }
  ]
};

export class SecuritySystem {
  static generate(type: FactionType, hqSize: number): SecurityFeature[] {
    const features: SecurityFeature[] = [];
    let idCounter = 0;
    for (const sec of baseSecurity[type]) {
      for (let i = 0; i < Math.max(1, Math.floor(hqSize / 10)); i++) {
        features.push({
          id: `${sec.type}_${idCounter++}`,
          type: sec.type,
          location: { x: Math.floor(Math.random() * hqSize), y: Math.floor(Math.random() * hqSize) },
          strength: sec.baseStrength + Math.floor(Math.random() * 2)
        });
      }
    }
    return features;
  }
} 