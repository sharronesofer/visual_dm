import { HexGrid } from './HexGrid';

export interface POITemplate {
  id: string;
  name: string;
  type: string;
  rarity: number; // 0-1
  allowedTerrains: string[];
  minDistance: number;
  maxDistance?: number;
  effects?: Record<string, any>;
}

export interface POIInstance {
  id: string;
  templateId: string;
  q: number;
  r: number;
  discovered: boolean;
}

export interface POIGeneratorOptions {
  seed?: number;
  maxPOIs?: number;
}

export function generatePOIs(
  grid: HexGrid,
  templates: POITemplate[],
  options: POIGeneratorOptions = {}
): POIInstance[] {
  const {
    seed = 42,
    maxPOIs = 10
  } = options;
  const pois: POIInstance[] = [];
  let poiCount = 0;
  let attempt = 0;
  const maxAttempts = maxPOIs * 20;
  while (poiCount < maxPOIs && attempt < maxAttempts) {
    attempt++;
    // Pick a template weighted by rarity
    const totalWeight = templates.reduce((sum, t) => sum + (1 - t.rarity), 0);
    let pick = (pseudoRandom(attempt, seed, 1) * totalWeight);
    let template: POITemplate | undefined;
    for (const t of templates) {
      pick -= (1 - t.rarity);
      if (pick <= 0) {
        template = t;
        break;
      }
    }
    if (!template) template = templates[0];
    // Pick a random cell
    const q = Math.floor(pseudoRandom(attempt, seed, 2) * grid.width);
    const r = Math.floor(pseudoRandom(attempt, seed, 3) * grid.height);
    const cell = grid.get(q, r);
    if (!cell) continue;
    // Terrain suitability
    if (!template.allowedTerrains.includes(cell.terrain)) continue;
    // Min/max distance constraint
    let tooClose = false;
    for (const poi of pois) {
      const dist = grid.distance(q, r, poi.q, poi.r);
      if (dist < template.minDistance) tooClose = true;
      if (template.maxDistance && dist > template.maxDistance) tooClose = true;
    }
    if (tooClose) continue;
    // Place POI
    pois.push({
      id: `poi-${poiCount}`,
      templateId: template.id,
      q,
      r,
      discovered: false
    });
    poiCount++;
  }
  return pois;
}

// Simple deterministic pseudoRandom for repeatability
function pseudoRandom(a: number, b: number, c: number): number {
  let x = a * 374761393 + b * 668265263 + c * 982451653;
  x = (x ^ (x >> 13)) * 1274126177;
  return ((x ^ (x >> 16)) >>> 0) / 0xffffffff;
}

export interface ResourceTemplate {
  id: string;
  name: string;
  type: string;
  rarity: number; // 0-1
  allowedTerrains: string[];
  clusterChance?: number; // 0-1
  clusterSize?: number;
}

export interface ResourceInstance {
  id: string;
  templateId: string;
  q: number;
  r: number;
  amount: number;
  depleted: boolean;
}

export interface ResourceGeneratorOptions {
  seed?: number;
  maxResources?: number;
}

export function generateResources(
  grid: HexGrid,
  resourceTemplates: ResourceTemplate[],
  pois: POIInstance[],
  options: ResourceGeneratorOptions = {}
): ResourceInstance[] {
  const {
    seed = 99,
    maxResources = 30
  } = options;
  const resources: ResourceInstance[] = [];
  let resourceCount = 0;
  let attempt = 0;
  const maxAttempts = maxResources * 20;
  while (resourceCount < maxResources && attempt < maxAttempts) {
    attempt++;
    // Pick a template weighted by rarity
    const totalWeight = resourceTemplates.reduce((sum, t) => sum + (1 - t.rarity), 0);
    let pick = (pseudoRandom(attempt, seed, 1) * totalWeight);
    let template: ResourceTemplate | undefined;
    for (const t of resourceTemplates) {
      pick -= (1 - t.rarity);
      if (pick <= 0) {
        template = t;
        break;
      }
    }
    if (!template) template = resourceTemplates[0];
    // Pick a random cell
    const q = Math.floor(pseudoRandom(attempt, seed, 2) * grid.width);
    const r = Math.floor(pseudoRandom(attempt, seed, 3) * grid.height);
    const cell = grid.get(q, r);
    if (!cell) continue;
    // Terrain suitability
    if (!template.allowedTerrains.includes(cell.terrain)) continue;
    // Proximity to POIs (optional: prefer near POIs for some resources)
    let nearPOI = false;
    for (const poi of pois) {
      const dist = grid.distance(q, r, poi.q, poi.r);
      if (dist <= 2) nearPOI = true;
    }
    // Cluster logic
    let clustered = false;
    if (template.clusterChance && pseudoRandom(attempt, seed, 4) < template.clusterChance) {
      clustered = true;
      const clusterSize = template.clusterSize || 2;
      for (let i = 0; i < clusterSize; i++) {
        const dq = Math.floor(pseudoRandom(attempt, seed, 5 + i) * 3) - 1;
        const dr = Math.floor(pseudoRandom(attempt, seed, 6 + i) * 3) - 1;
        const cq = q + dq;
        const cr = r + dr;
        const ccell = grid.get(cq, cr);
        if (!ccell || !template.allowedTerrains.includes(ccell.terrain)) continue;
        resources.push({
          id: `res-${resourceCount}`,
          templateId: template.id,
          q: cq,
          r: cr,
          amount: 100,
          depleted: false
        });
        resourceCount++;
        if (resourceCount >= maxResources) break;
      }
      continue;
    }
    // Place resource
    resources.push({
      id: `res-${resourceCount}`,
      templateId: template.id,
      q,
      r,
      amount: 100,
      depleted: false
    });
    resourceCount++;
  }
  return resources;
}

export function discoverPOI(pois: POIInstance[], q: number, r: number, radius: number): void {
  for (const poi of pois) {
    const dist = Math.abs(poi.q - q) + Math.abs(poi.r - r);
    if (dist <= radius) poi.discovered = true;
  }
}

export function discoverResource(resources: ResourceInstance[], q: number, r: number, radius: number): void {
  for (const res of resources) {
    const dist = Math.abs(res.q - q) + Math.abs(res.r - r);
    if (dist <= radius) res.depleted = false; // For discovery, we use depleted=false as 'discovered'
  }
}

export function queryNearbyPOIs(pois: POIInstance[], q: number, r: number, radius: number): POIInstance[] {
  return pois.filter(poi => poi.discovered && (Math.abs(poi.q - q) + Math.abs(poi.r - r) <= radius));
}

export function queryNearbyResources(resources: ResourceInstance[], q: number, r: number, radius: number): ResourceInstance[] {
  return resources.filter(res => !res.depleted && (Math.abs(res.q - q) + Math.abs(res.r - r) <= radius));
} 