import fs from 'fs';
import path from 'path';

export enum SettlementType {
    VILLAGE = 'VILLAGE',
    TOWN = 'TOWN',
    CITY = 'CITY',
}

export interface SettlementConfig {
    size: number;
    populationCapacity: number;
    buildingDensity: number;
    availableServices: string[];
    growthParameters: { [key: string]: number };
    transitionThresholds: { [key in SettlementType]?: number };
}

export class Settlement {
    type: SettlementType;
    size: number;
    populationCapacity: number;
    buildingDensity: number;
    availableServices: string[];
    growthParameters: { [key: string]: number };
    static config: Record<SettlementType, SettlementConfig>;

    constructor(type: SettlementType) {
        if (!Settlement.config) {
            Settlement.loadTypeParameters();
        }
        this.type = type;
        const cfg = Settlement.config[type];
        this.size = cfg.size;
        this.populationCapacity = cfg.populationCapacity;
        this.buildingDensity = cfg.buildingDensity;
        this.availableServices = [...cfg.availableServices];
        this.growthParameters = { ...cfg.growthParameters };
    }

    static loadTypeParameters(configPath = path.join(__dirname, 'settlementTypes.config.json')) {
        const raw = fs.readFileSync(configPath, 'utf-8');
        const parsed = JSON.parse(raw);
        Settlement.config = parsed as Record<SettlementType, SettlementConfig>;
    }

    calculateGrowthMetrics(currentPopulation: number, area: number): { [key: string]: number } {
        // Example: return metrics used for transition logic
        return {
            population: currentPopulation,
            area,
        };
    }

    checkForTypeTransition(metrics: { [key: string]: number }): SettlementType | null {
        const thresholds = Settlement.config[this.type].transitionThresholds;
        if (this.type === SettlementType.VILLAGE && metrics.population >= (thresholds[SettlementType.TOWN] || Infinity)) {
            return SettlementType.TOWN;
        }
        if (this.type === SettlementType.TOWN && metrics.population >= (thresholds[SettlementType.CITY] || Infinity)) {
            return SettlementType.CITY;
        }
        return null;
    }

    evolveSettlement(newType: SettlementType) {
        if (!Settlement.config[newType]) throw new Error('Invalid settlement type');
        this.type = newType;
        const cfg = Settlement.config[newType];
        this.size = cfg.size;
        this.populationCapacity = cfg.populationCapacity;
        this.buildingDensity = cfg.buildingDensity;
        this.availableServices = [...cfg.availableServices];
        this.growthParameters = { ...cfg.growthParameters };
    }
} 