// RepairAndMaintenanceSystem.ts
// Core logic for building repair, maintenance, and integration with vendors, POIs, and tick system

import { BuildingStructure, BuildingElement } from '../core/interfaces/types/building';
import { POI } from '../core/models/models/POI';
import { calculateRepairCost, defaultRepairCostConfig } from './RepairCostCalculator';

export class RepairAndMaintenanceSystem {
    constructor() { }

    // Vendor repair workflow
    requestVendorRepair(building: BuildingStructure, vendorId: string): { cost: number; vendorId: string } {
        // Calculate repair cost using the calculator
        const cost = calculateRepairCost(building, defaultRepairCostConfig, vendorId);
        // In a real system, you would also check vendor availability, reputation, etc.
        return { cost, vendorId };
    }

    confirmVendorRepair(building: BuildingStructure, vendorId: string): void {
        // Apply full repair to the building (reset damage)
        (building as any).battleDamage = 0;
        (building as any).deterioration = 0;
        // Optionally, update vendor reputation, log transaction, etc.
    }

    // Cost calculation (delegates to RepairCostCalculator)
    calculateRepairCost(building: BuildingStructure, vendorId: string): number {
        return calculateRepairCost(building, defaultRepairCostConfig, vendorId);
    }

    // Passive repair based on POI proximity
    applyPassiveRepair(building: BuildingStructure, pois: POI[]): void {
        // Find nearest POI
        const buildingPos = this._getBuildingPosition(building);
        let bestPOI = null;
        let minDist = Infinity;
        for (const poi of pois) {
            const dist = poi.distanceTo([buildingPos.x, buildingPos.y]);
            if (dist < minDist) {
                minDist = dist;
                bestPOI = poi;
            }
        }
        // If within passive repair range, apply passive repair
        if (bestPOI && minDist < 100) { // 100 meters as example threshold
            (building as any).deterioration = Math.max(0, (building as any).deterioration - 0.1); // Slow passive repair
        }
    }

    // Hourly repair chance calculation
    processHourlyRepairTick(building: BuildingStructure, context: any): void {
        // Example: 10% base chance, +5% if near resources, -5% if bad weather
        let chance = 0.1;
        if (context.nearbyResources) chance += 0.05;
        if (context.weather === 'storm') chance -= 0.05;
        if (Math.random() < chance) {
            (building as any).battleDamage = Math.max(0, (building as any).battleDamage - 1);
        }
        // Debug log
        if (context.debug) {
            console.log(`Hourly repair tick: chance=${chance}, building=${building.id}`);
        }
    }

    // Maintenance effects
    applyMaintenanceEffects(building: BuildingStructure): void {
        // Example: If deterioration > 5, apply debuff
        if ((building as any).deterioration > 5) {
            (building as any).maintenanceStatus = 'poor';
            // Apply debuff logic here
        } else {
            (building as any).maintenanceStatus = 'good';
            // Remove debuff logic here
        }
        // Visual indicators would be handled in the UI layer
    }

    _getBuildingPosition(building: BuildingStructure): { x: number; y: number } {
        // Use the first element's position as a proxy for building position
        const firstElement = Array.from(building.elements.values()).find(
            (el: any): el is { position: { x: number; y: number } } =>
                el && typeof el.position === 'object' && typeof el.position.x === 'number' && typeof el.position.y === 'number'
        );
        return firstElement ? firstElement.position : { x: 0, y: 0 };
    }
}

// --- POI Passive Repair System ---

export interface POIRepairProperties {
    repairRadius: number; // in game units
    repairRatePerTick: number; // percent per tick
    maxRepairPercentage: number; // max percent health restored
    typeSpecialization: Record<string, number>; // e.g. {residential: 1.0, industrial: 0.5}
}

export interface RepairCapablePOI {
    id: string;
    x: number;
    y: number;
    type: string;
    repairProps: POIRepairProperties;
}

export class POIPassiveRepairSystem {
    constructor(private getBuildings: () => BuildingStructure[], private getPOIs: () => RepairCapablePOI[]) { }

    // Find all buildings within a POI's repair radius
    private buildingsInRadius(poi: RepairCapablePOI): BuildingStructure[] {
        const buildings = this.getBuildings();
        return buildings.filter(b => {
            const pos = this._getBuildingPosition(b);
            const dx = pos.x - poi.x;
            const dy = pos.y - poi.y;
            return Math.sqrt(dx * dx + dy * dy) <= poi.repairProps.repairRadius;
        });
    }

    // Apply passive repairs on tick
    applyPassiveRepairs(): void {
        const pois = this.getPOIs();
        for (const poi of pois) {
            const buildings = this.buildingsInRadius(poi);
            for (const building of buildings) {
                const type = (building as any).buildingType || 'default';
                const specialization = poi.repairProps.typeSpecialization[type] ?? 1.0;
                const maxRepair = poi.repairProps.maxRepairPercentage;
                const rate = poi.repairProps.repairRatePerTick * specialization;
                // Only repair up to maxRepairPercentage
                const currentHealth = 100 - ((building as any).battleDamage ?? 0) - ((building as any).deterioration ?? 0);
                const maxHealth = 100 * (maxRepair / 100);
                if (currentHealth < maxHealth) {
                    // Apply repair (increase health, decrease damage)
                    const repairAmount = Math.min(rate, maxHealth - currentHealth);
                    if ((building as any).battleDamage !== undefined) {
                        (building as any).battleDamage = Math.max(0, (building as any).battleDamage - repairAmount);
                    } else if ((building as any).deterioration !== undefined) {
                        (building as any).deterioration = Math.max(0, (building as any).deterioration - repairAmount);
                    }
                    // TODO: Trigger visual feedback (particle effect, etc.)
                }
            }
        }
    }

    // Helper to get building position (reuse from main system)
    private _getBuildingPosition(building: BuildingStructure): { x: number; y: number } {
        const firstElement = Array.from(building.elements.values()).find(
            (el: any): el is { position: { x: number; y: number } } =>
                el && typeof el.position === 'object' && typeof el.position.x === 'number' && typeof el.position.y === 'number'
        );
        return firstElement ? firstElement.position : { x: 0, y: 0 };
    }

    // Stub for map overlay integration
    renderRepairZones(surface: any): void {
        // TODO: Draw repair zone overlays for each POI
    }
}

// --- Hourly Repair Chance Calculation System ---

export interface RepairChanceConfig {
    baseChanceByType: Record<string, number>; // e.g. {residential: 0.10, commercial: 0.08, industrial: 0.05, default: 0.07}
    weatherModifiers: Record<string, number>; // e.g. {storm: 0.5, clear: 1.2, default: 1.0}
    timeOfDayModifiers: { day: number; night: number };
    resourceProximityBonus: number; // e.g. 0.1 per node
    resourceProximityMax: number; // e.g. 0.3 max
}

export const defaultRepairChanceConfig: RepairChanceConfig = {
    baseChanceByType: {
        residential: 0.12,
        commercial: 0.09,
        industrial: 0.06,
        default: 0.08
    },
    weatherModifiers: {
        storm: 0.5,
        clear: 1.2,
        default: 1.0
    },
    timeOfDayModifiers: {
        day: 1.25,
        night: 0.75
    },
    resourceProximityBonus: 0.1,
    resourceProximityMax: 0.3
};

export function calculateRepairChance(
    building: BuildingStructure,
    context: {
        weather: string;
        hour: number;
        nearbyResourceNodes: number;
        config?: RepairChanceConfig;
        debug?: boolean;
    }
): number {
    const cfg = context.config || defaultRepairChanceConfig;
    const type = (building as any).buildingType || 'default';
    let chance = cfg.baseChanceByType[type] ?? cfg.baseChanceByType.default;

    // Weather modifier
    const weatherMod = cfg.weatherModifiers[context.weather] ?? cfg.weatherModifiers.default;
    chance *= weatherMod;

    // Time of day modifier
    const isDay = context.hour >= 8 && context.hour < 18;
    chance *= isDay ? cfg.timeOfDayModifiers.day : cfg.timeOfDayModifiers.night;

    // Resource proximity bonus
    const resourceBonus = Math.min(cfg.resourceProximityBonus * (context.nearbyResourceNodes || 0), cfg.resourceProximityMax);
    chance += resourceBonus;

    // Clamp to [0, 1]
    chance = Math.max(0, Math.min(1, chance));

    if (context.debug) {
        console.log(`[RepairChance] type=${type}, base=${cfg.baseChanceByType[type]}, weatherMod=${weatherMod}, timeMod=${isDay ? cfg.timeOfDayModifiers.day : cfg.timeOfDayModifiers.night}, resourceBonus=${resourceBonus}, finalChance=${chance}`);
    }
    return chance;
}

// Weighted random selection for repairs
export function selectBuildingsForRepair(
    buildings: BuildingStructure[],
    context: {
        weather: string;
        hour: number;
        nearbyResourceNodes: (buildingId: string) => number;
        config?: RepairChanceConfig;
        debug?: boolean;
    }
): BuildingStructure[] {
    // Calculate chance for each building
    const weighted: { building: BuildingStructure; chance: number }[] = buildings.map(b => ({
        building: b,
        chance: calculateRepairChance(b, {
            weather: context.weather,
            hour: context.hour,
            nearbyResourceNodes: context.nearbyResourceNodes((b as any).id),
            config: context.config,
            debug: context.debug
        })
    }));
    // Select buildings to repair based on weighted random
    const selected: BuildingStructure[] = [];
    for (const { building, chance } of weighted) {
        if (Math.random() < chance) {
            selected.push(building);
            if (context.debug) {
                console.log(`[RepairChance] Building ${(building as any).id} selected for repair (chance=${chance})`);
            }
        }
    }
    return selected;
}

// --- Building Maintenance Effects System ---

export type MaintenanceStatus = 'Neglected' | 'Poor' | 'Fair' | 'Good' | 'Well-Maintained';

export interface MaintenanceComponent {
    maintenanceLevel: number; // 0-100
    status: MaintenanceStatus;
    timeSinceLastMaintenance: number; // in hours
}

export class MaintenanceEffectsManager {
    static getStatus(level: number): MaintenanceStatus {
        if (level <= 20) return 'Neglected';
        if (level <= 40) return 'Poor';
        if (level <= 60) return 'Fair';
        if (level <= 80) return 'Good';
        return 'Well-Maintained';
    }

    static applyEffects(building: BuildingStructure, maintenance: MaintenanceComponent): void {
        // Remove all previous effects first (implementation depends on effect system)
        // ...
        switch (maintenance.status) {
            case 'Well-Maintained':
                // +10-15% efficiency, -5-10% resource use, extended lifespan
                // ...
                break;
            case 'Good':
                // +5-10% efficiency
                // ...
                break;
            case 'Fair':
                // Baseline, no effect
                break;
            case 'Poor':
                // -10-15% efficiency, 5% daily shutdown chance
                // ...
                break;
            case 'Neglected':
                // -25-40% efficiency, 15% daily failure, risk of permanent damage
                // ...
                break;
        }
    }

    static calculateMaintenanceCost(building: BuildingStructure, maintenance: MaintenanceComponent, baseCost: number, moduleCount: number = 0, sizeMultiplier: number = 1): number {
        // If size or moduleCount are not available, use defaults or infer from elements
        // sizeMultiplier: 1 (default), 1.5 (medium), 2 (large) -- can be inferred from elements count
        // moduleCount: 0 if not available
        let cost = baseCost * sizeMultiplier * (1 + 0.1 * moduleCount);
        // Neglect penalty: +5% per week of neglect, max 3x
        const neglectWeeks = Math.floor(maintenance.timeSinceLastMaintenance / (24 * 7)) || 0;
        cost *= Math.min(1 + 0.05 * neglectWeeks, 3);
        return cost;
    }

    static updateMaintenanceStatus(maintenance: MaintenanceComponent): void {
        const prevStatus = maintenance.status;
        maintenance.status = this.getStatus(maintenance.maintenanceLevel);
        if (prevStatus !== maintenance.status) {
            // Trigger status change event (for UI, effects, etc.)
            // ...
        }
    }
}

// Stubs for visual/UI integration
export class BuildingAppearanceController {
    static updateAppearance(building: BuildingStructure, maintenance: MaintenanceComponent): void {
        // Change model/texture/particle effects based on maintenance.status
        // ...
    }
    static showMaintenanceStatusUI(building: BuildingStructure, maintenance: MaintenanceComponent): void {
        // Show color-coded icon, status bar, etc.
        // ...
    }
} 