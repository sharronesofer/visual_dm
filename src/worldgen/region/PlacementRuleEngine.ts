import { RegionCell, Building, Resource, PlacementRule, PlacementRuleContext, PlacementRuleResult, PlacementRuleEngine } from './RegionGeneratorInterfaces';

/**
 * Implementation of the PlacementRuleEngine for building placement
 */
export class DefaultPlacementRuleEngine implements PlacementRuleEngine {
    /**
     * Evaluate all placement rules for a candidate cell
     * @param cell The candidate RegionCell
     * @param context Context including all cells, buildings, resources, and density map
     * @param rules Array of PlacementRule objects
     * @returns PlacementRuleResult with validity, failed rules, and reasons
     */
    evaluate(cell: RegionCell, context: PlacementRuleContext, rules: PlacementRule[]): PlacementRuleResult {
        const failedRules: string[] = [];
        const reasons: string[] = [];
        const advisory: string[] = [];
        let valid = true;
        let score = 1;
        for (const rule of rules) {
            // Biome/terrain checks
            if (rule.allowedBiomes && rule.allowedBiomes.length > 0) {
                if (!rule.allowedBiomes.includes(cell.terrain)) {
                    if (rule.isHardRule) valid = false;
                    failedRules.push(rule.id);
                    reasons.push(`Biome/terrain not allowed by rule: ${rule.id}`);
                    continue;
                }
            }
            if (rule.allowedTerrains && rule.allowedTerrains.length > 0) {
                if (!rule.allowedTerrains.includes(cell.terrain)) {
                    if (rule.isHardRule) valid = false;
                    failedRules.push(rule.id);
                    reasons.push(`Terrain not allowed by rule: ${rule.id}`);
                    continue;
                }
            }
            // Resource proximity checks
            if (rule.minDistanceToResource) {
                for (const req of rule.minDistanceToResource) {
                    const minDist = this._minDistanceToResource(cell, context.resources, req.resourceType);
                    if (minDist === undefined || minDist < req.minDistance) {
                        if (rule.isHardRule) valid = false;
                        failedRules.push(rule.id);
                        reasons.push(`Too close to resource ${req.resourceType} (min: ${req.minDistance})`);
                    }
                }
            }
            if (rule.maxDistanceToResource) {
                for (const req of rule.maxDistanceToResource) {
                    const minDist = this._minDistanceToResource(cell, context.resources, req.resourceType);
                    if (minDist === undefined || minDist > req.maxDistance) {
                        if (rule.isHardRule) valid = false;
                        failedRules.push(rule.id);
                        reasons.push(`Too far from resource ${req.resourceType} (max: ${req.maxDistance})`);
                    }
                }
            }
            // Population density checks
            if (context.densityMap && (rule.minPopulationDensity !== undefined || rule.maxPopulationDensity !== undefined)) {
                const density = this._getDensityAt(cell, context.densityMap);
                if (rule.minPopulationDensity !== undefined && density < rule.minPopulationDensity) {
                    if (rule.isHardRule) valid = false;
                    failedRules.push(rule.id);
                    reasons.push(`Population density too low (min: ${rule.minPopulationDensity})`);
                }
                if (rule.maxPopulationDensity !== undefined && density > rule.maxPopulationDensity) {
                    if (rule.isHardRule) valid = false;
                    failedRules.push(rule.id);
                    reasons.push(`Population density too high (max: ${rule.maxPopulationDensity})`);
                }
            }
            // Custom rule function
            if (rule.customRuleFn) {
                const result = rule.customRuleFn(cell, context);
                if (typeof result === 'boolean') {
                    if (!result) {
                        if (rule.isHardRule) valid = false;
                        failedRules.push(rule.id);
                        reasons.push(`Custom rule failed: ${rule.id}`);
                    }
                } else if (typeof result === 'object') {
                    if (!result.valid) {
                        if (rule.isHardRule) valid = false;
                        failedRules.push(rule.id);
                        reasons.push(...(result.reasons || [`Custom rule failed: ${rule.id}`]));
                    }
                    if (result.advisory) advisory.push(...result.advisory);
                    if (result.score !== undefined) score *= result.score;
                }
            }
        }
        return { valid, failedRules, reasons, advisory, score };
    }

    /**
     * Find all valid locations for a given rule set
     * @param context PlacementRuleContext
     * @param rules Array of PlacementRule
     * @returns Array of valid RegionCells
     */
    findValidLocations(context: PlacementRuleContext, rules: PlacementRule[]): RegionCell[] {
        return context.cells.filter(cell => this.evaluate(cell, context, rules).valid);
    }

    /**
     * Helper: Compute minimum distance from cell to a resource type
     */
    private _minDistanceToResource(cell: RegionCell, resources: Resource[], resourceType: string): number | undefined {
        let minDist: number | undefined = undefined;
        for (const res of resources) {
            if (res.templateId === resourceType) {
                const dist = Math.sqrt(Math.pow(res.x - cell.x, 2) + Math.pow(res.y - cell.y, 2));
                if (minDist === undefined || dist < minDist) minDist = dist;
            }
        }
        return minDist;
    }

    /**
     * Helper: Get population/building density at a cell from a density map
     */
    private _getDensityAt(cell: RegionCell, densityMap: number[][]): number {
        if (!densityMap[cell.x] || densityMap[cell.x][cell.y] === undefined) return 0;
        return densityMap[cell.x][cell.y];
    }
} 