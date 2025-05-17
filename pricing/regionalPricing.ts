import {
    regions,
    transportCostPerKm,
    weightCostFactor,
    volumeCostFactor,
    fragilityCostFactor,
    eventTemplates,
    Region,
    RegionalEvent
} from './regionConfig.js';

export interface ItemProperties {
    weight: number; // kg
    volume: number; // m^3
    fragile: boolean;
}

export function getRegion(regionId: string): Region | undefined {
    return regions.find(r => r.id === regionId);
}

export function calculateTransportCost(distanceKm: number, item: ItemProperties): number {
    let cost = distanceKm * transportCostPerKm;
    cost += item.weight * weightCostFactor;
    cost += item.volume * volumeCostFactor;
    if (item.fragile) cost *= 1 + fragilityCostFactor;
    return cost;
}

export function applyRegionalModifiers(basePrice: number, regionId: string): number {
    const region = getRegion(regionId);
    if (!region) return basePrice;
    return basePrice * region.baseModifier * region.supplyModifier * region.demandModifier;
}

export function applyRegionalEvent(price: number, regionId: string, activeEvents: RegionalEvent[]): number {
    let modifiedPrice = price;
    for (const event of activeEvents) {
        if (event.regionId === regionId) {
            modifiedPrice *= event.modifier;
        }
    }
    return modifiedPrice;
}

export function smoothTransition(priceA: number, priceB: number, distanceToBoundary: number, smoothingRange: number): number {
    // Interpolate between two region prices near a boundary
    if (distanceToBoundary >= smoothingRange) return priceA;
    const t = 1 - distanceToBoundary / smoothingRange;
    return priceA * (1 - t) + priceB * t;
}

export interface RegionalPricingInput {
    basePrice: number;
    regionId: string;
    item: ItemProperties;
    distanceKm: number;
    activeEvents: RegionalEvent[];
    adjacentRegionId?: string;
    distanceToBoundary?: number;
    smoothingRange?: number;
}

export function calculateRegionalPrice(input: RegionalPricingInput): number {
    let price = input.basePrice;
    price = applyRegionalModifiers(price, input.regionId);
    price = applyRegionalEvent(price, input.regionId, input.activeEvents);
    price += calculateTransportCost(input.distanceKm, input.item);
    // Smooth transition if near boundary
    if (input.adjacentRegionId && typeof input.distanceToBoundary === 'number' && typeof input.smoothingRange === 'number') {
        const adjacentPrice = applyRegionalModifiers(input.basePrice, input.adjacentRegionId);
        price = smoothTransition(price, adjacentPrice, input.distanceToBoundary, input.smoothingRange);
    }
    return Math.max(price, 0.01);
} 