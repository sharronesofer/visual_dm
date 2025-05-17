import {
    locationWeights,
    featureWeights,
    premiumZones,
    premiumZoneMultiplier,
    appreciationRatePerYear,
    depreciationRatePerYear
} from './housingConfig.js';

export interface HousingAttributes {
    size: number; // e.g., square meters
    rooms: number;
    pool?: boolean;
    garden?: boolean;
    garage?: boolean;
    [key: string]: any;
}

export interface HousingLocation {
    proximityToResource: number; // 0-1 (1 = next to resource)
    proximityToCity: number;     // 0-1 (1 = in city)
    isWaterfront: boolean;
    zone: string;                // e.g., 'city_center', 'suburb', etc.
}

export interface HousingCondition {
    yearsOld: number;
    condition: 'excellent' | 'good' | 'average' | 'poor';
}

export interface HousingPricingInput {
    basePrice: number;
    attributes: HousingAttributes;
    location: HousingLocation;
    condition: HousingCondition;
}

export function locationModifier(location: HousingLocation): number {
    let modifier = 1;
    modifier *= 1 + location.proximityToResource * (locationWeights.resourceProximity - 1);
    modifier *= 1 + location.proximityToCity * (locationWeights.cityProximity - 1);
    if (location.isWaterfront) modifier *= locationWeights.waterfront;
    if (premiumZones.includes(location.zone)) modifier *= premiumZoneMultiplier;
    return modifier;
}

export function featureModifier(attributes: HousingAttributes): number {
    let modifier = 1;
    modifier *= 1 + (attributes.size || 0) * featureWeights.size;
    modifier *= 1 + (attributes.rooms || 0) * featureWeights.rooms;
    if (attributes.pool) modifier *= 1 + featureWeights.pool;
    if (attributes.garden) modifier *= 1 + featureWeights.garden;
    if (attributes.garage) modifier *= 1 + featureWeights.garage;
    return modifier;
}

export function appreciationDepreciationModifier(condition: HousingCondition): number {
    let modifier = 1;
    if (condition.condition === 'excellent' || condition.condition === 'good') {
        modifier *= 1 + appreciationRatePerYear * condition.yearsOld;
    } else if (condition.condition === 'poor') {
        modifier *= 1 - depreciationRatePerYear * condition.yearsOld;
        if (modifier < 0.5) modifier = 0.5; // Don't depreciate below 50%
    }
    return modifier;
}

export function calculateHousingPrice(input: HousingPricingInput): number {
    let price = input.basePrice;
    price *= locationModifier(input.location);
    price *= featureModifier(input.attributes);
    price *= appreciationDepreciationModifier(input.condition);
    return Math.max(price, 1); // Never below 1
} 