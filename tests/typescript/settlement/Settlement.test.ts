import { Settlement, SettlementType } from '../../../settlement/Settlement';
import path from 'path';

describe('Settlement', () => {
    beforeAll(() => {
        // Ensure config is loaded from the correct path
        Settlement.loadTypeParameters(path.resolve(__dirname, '../../../settlement/settlementTypes.config.json'));
    });

    it('should initialize a VILLAGE with correct parameters', () => {
        const village = new Settlement(SettlementType.VILLAGE);
        expect(village.type).toBe(SettlementType.VILLAGE);
        expect(village.size).toBe(1);
        expect(village.populationCapacity).toBe(200);
        expect(village.buildingDensity).toBeCloseTo(0.5);
        expect(village.availableServices).toContain('well');
        expect(village.growthParameters.growthRate).toBeCloseTo(1.05);
    });

    it('should initialize a TOWN with correct parameters', () => {
        const town = new Settlement(SettlementType.TOWN);
        expect(town.type).toBe(SettlementType.TOWN);
        expect(town.size).toBe(2);
        expect(town.populationCapacity).toBe(2000);
        expect(town.buildingDensity).toBeCloseTo(0.7);
        expect(town.availableServices).toContain('inn');
        expect(town.growthParameters.growthRate).toBeCloseTo(1.03);
    });

    it('should initialize a CITY with correct parameters', () => {
        const city = new Settlement(SettlementType.CITY);
        expect(city.type).toBe(SettlementType.CITY);
        expect(city.size).toBe(3);
        expect(city.populationCapacity).toBe(20000);
        expect(city.buildingDensity).toBeCloseTo(0.9);
        expect(city.availableServices).toContain('university');
        expect(city.growthParameters.growthRate).toBeCloseTo(1.01);
    });

    it('should transition from VILLAGE to TOWN when population threshold is met', () => {
        const village = new Settlement(SettlementType.VILLAGE);
        const metrics = { population: 300, area: 1 };
        const nextType = village.checkForTypeTransition(metrics);
        expect(nextType).toBe(SettlementType.TOWN);
        if (nextType) village.evolveSettlement(nextType);
        expect(village.type).toBe(SettlementType.TOWN);
        expect(village.populationCapacity).toBe(2000);
    });

    it('should transition from TOWN to CITY when population threshold is met', () => {
        const town = new Settlement(SettlementType.TOWN);
        const metrics = { population: 3000, area: 2 };
        const nextType = town.checkForTypeTransition(metrics);
        expect(nextType).toBe(SettlementType.CITY);
        if (nextType) town.evolveSettlement(nextType);
        expect(town.type).toBe(SettlementType.CITY);
        expect(town.populationCapacity).toBe(20000);
    });

    it('should not transition if thresholds are not met', () => {
        const village = new Settlement(SettlementType.VILLAGE);
        const metrics = { population: 100, area: 1 };
        const nextType = village.checkForTypeTransition(metrics);
        expect(nextType).toBeNull();
    });
}); 