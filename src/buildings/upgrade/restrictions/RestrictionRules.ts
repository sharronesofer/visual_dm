import { Building, Resources } from '../BuildingUpgradeValidator';

export interface IUpgradeRestriction {
    isAllowed(building: Building, context: RestrictionContext): boolean;
    reason?: string;
}

export interface RestrictionContext {
    location?: string;
    faction?: string;
    resources?: Resources;
    [key: string]: any;
}

export class LocationRestriction implements IUpgradeRestriction {
    constructor(private allowedLocations: string[]) { }
    isAllowed(building: Building, context: RestrictionContext): boolean {
        return context.location ? this.allowedLocations.includes(context.location) : true;
    }
    reason = 'Upgrade not allowed at this location.';
}

export class FactionRestriction implements IUpgradeRestriction {
    constructor(private allowedFactions: string[]) { }
    isAllowed(building: Building, context: RestrictionContext): boolean {
        return context.faction ? this.allowedFactions.includes(context.faction) : true;
    }
    reason = 'Upgrade not allowed for this faction.';
}

export class ResourceRestriction implements IUpgradeRestriction {
    constructor(private requiredResources: Resources) { }
    isAllowed(building: Building, context: RestrictionContext): boolean {
        if (!context.resources) return true;
        for (const [resource, amount] of Object.entries(this.requiredResources)) {
            if ((context.resources[resource] || 0) < amount) {
                return false;
            }
        }
        return true;
    }
    reason = 'Insufficient resources for upgrade.';
} 