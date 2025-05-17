/**
 * Region definitions and economic characteristics.
 */
export interface Region {
    id: string;
    name: string;
    neighbors: string[];
    baseModifier: number;
    supplyModifier: number;
    demandModifier: number;
}

export const regions: Region[] = [
    { id: 'north', name: 'Northern Province', neighbors: ['central'], baseModifier: 1.0, supplyModifier: 1.1, demandModifier: 0.9 },
    { id: 'central', name: 'Central City', neighbors: ['north', 'south'], baseModifier: 1.2, supplyModifier: 1.0, demandModifier: 1.2 },
    { id: 'south', name: 'Southern Coast', neighbors: ['central'], baseModifier: 0.9, supplyModifier: 0.8, demandModifier: 1.1 }
];

/**
 * Transport cost factors by item property.
 */
export const transportCostPerKm = 0.05; // base cost per km
export const weightCostFactor = 0.01;   // per kg
export const volumeCostFactor = 0.02;   // per m^3
export const fragilityCostFactor = 0.1; // multiplier for fragile items

/**
 * Regional economic event templates.
 */
export interface RegionalEvent {
    id: string;
    name: string;
    regionId: string;
    modifier: number;
    type: 'festival' | 'disaster' | 'resource_discovery';
    durationDays: number;
}

export const eventTemplates: RegionalEvent[] = [
    { id: 'fest1', name: 'Harvest Festival', regionId: 'north', modifier: 1.2, type: 'festival', durationDays: 7 },
    { id: 'dis1', name: 'Flood', regionId: 'south', modifier: 0.7, type: 'disaster', durationDays: 5 },
    { id: 'res1', name: 'Gold Discovery', regionId: 'central', modifier: 1.5, type: 'resource_discovery', durationDays: 10 }
]; 