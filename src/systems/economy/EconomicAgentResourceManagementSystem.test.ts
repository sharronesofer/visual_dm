import { EconomicAgentResourceManagementSystem, EconomicResource, ResourceCategory, ResourceType, ResourcePlugin } from './EconomicAgentResourceManagementSystem';

describe('EconomicAgentResourceManagementSystem', () => {
    let system: EconomicAgentResourceManagementSystem;
    const now = Date.now();
    const resource: EconomicResource = {
        id: 'r1',
        type: ResourceType.FOOD,
        name: 'Wheat',
        quantity: 100,
        quality: 80,
        category: ResourceCategory.RENEWABLE,
        createdAt: now,
        updatedAt: now,
    };

    beforeEach(() => {
        system = new EconomicAgentResourceManagementSystem();
    });

    it('should add, get, update, and remove a resource', () => {
        system.addResource(resource);
        const fetched = system.getResource('r1');
        expect(fetched).not.toBeUndefined();
        expect(fetched?.name).toEqual('Wheat');
        system.updateResource('r1', { quantity: 50 });
        expect(system.getResource('r1')?.quantity).toEqual(50);
        system.removeResource('r1');
        expect(system.getResource('r1')).toBeUndefined();
    });

    it('should reserve and release resources for agents', () => {
        system.addResource(resource);
        const reserved = system.reserveResource('agent1', 'r1', 10);
        expect(reserved).toEqual(true);
        system.releaseResourceReservation('agent1', 'r1');
        // No assertion for internal state, just ensure no error
    });

    it('should log and retrieve consumption', () => {
        system.addResource(resource);
        system.logConsumption('agent1', 'r1', 5);
        const log = system.getConsumption('r1');
        expect(log.length).toEqual(1);
        expect(log[0].agentId).toEqual('agent1');
        expect(log[0].quantity).toEqual(5);
    });

    it('should serialize and deserialize resources', () => {
        system.addResource(resource);
        const data = system.serialize();
        const newSystem = new EconomicAgentResourceManagementSystem();
        newSystem.deserialize(data);
        expect(newSystem.getResource('r1')).not.toBeUndefined();
        expect(newSystem.getResource('r1')?.name).toEqual('Wheat');
    });

    it('should apply plugins and config defaults', () => {
        const plugin: ResourcePlugin = {
            name: 'TestPlugin',
            apply: (res) => { res.quality = 99; }
        };
        const config = { [ResourceType.FOOD]: { quantity: 200 } };
        const sys = new EconomicAgentResourceManagementSystem(config);
        sys.registerPlugin(plugin);
        const res: EconomicResource = { ...resource, id: 'r2', quantity: 1, quality: 1 };
        sys.addResource(res);
        const fetched = sys.getResource('r2');
        expect(fetched?.quantity).toEqual(200);
        expect(fetched?.quality).toEqual(99);
    });

    it('should allocate resources based on priority', () => {
        system.addResource(resource);
        // Agent 1 (high priority)
        system.reserveResource('agent1', 'r1', 60, 10);
        // Agent 2 (low priority)
        system.reserveResource('agent2', 'r1', 60, 1);
        // Only 100 available
        const allocation = system.allocateResource('r1', 100);
        expect(allocation['agent1']).toEqual(60);
        expect(allocation['agent2']).toEqual(40);
    });

    it('should support resource pooling for groups', () => {
        system.createOrUpdateResourcePool('group1', ['r1', 'r2'], true);
        const pool = system.getResourcePool('group1');
        expect(pool).not.toBeUndefined();
        expect(pool?.resourceIds).toContain('r1');
        expect(pool?.shared).toEqual(true);
    });

    it('should cleanup expired reservations', () => {
        system.addResource(resource);
        const now = Date.now();
        // Expired reservation
        system.reserveResource('agent1', 'r1', 10, 5, now - 1000);
        // Valid reservation
        system.reserveResource('agent2', 'r1', 10, 5, now + 10000);
        system.cleanupExpiredReservations();
        const reservations = system.allocationManager.getReservations('r1');
        expect(reservations.length).toEqual(1);
        expect(reservations[0].agentId).toEqual('agent2');
    });

    it('should log consumption with modifiers and retrieve them', () => {
        system.addResource(resource);
        system.logConsumption('agent1', 'r1', 5, { health: 0.8, fatigue: 0.2 });
        const log = system.getConsumption('r1');
        expect(log.length).toEqual(1);
        expect(log[0].modifiers).not.toBeUndefined();
        expect(log[0].modifiers?.health).toEqual(0.8);
        expect(log[0].modifiers?.fatigue).toEqual(0.2);
    });

    it('should calculate average consumption for agent and window', () => {
        system.addResource(resource);
        const now = Date.now();
        system.logConsumption('agent1', 'r1', 10);
        system.logConsumption('agent1', 'r1', 20);
        system.logConsumption('agent2', 'r1', 30);
        // All agents
        expect(system.getResourceEfficiency('r1')).toBeCloseTo(20, 1);
        // Agent 1 only
        expect(system.getResourceEfficiency('r1', 'agent1')).toBeCloseTo(15, 1);
        // Window (should include all, as timestamps are now)
        expect(system.getResourceEfficiency('r1', undefined, 10000)).toBeCloseTo(20, 1);
    });

    it('should forecast consumption using SMA and exponential smoothing', () => {
        system.addResource(resource);
        [5, 10, 15, 20, 25].forEach(q => system.logConsumption('agent1', 'r1', q));
        // SMA (last 3)
        expect(system.forecastResourceConsumption('r1', 'sma', { periods: 3 })).toBeCloseTo((15 + 20 + 25) / 3, 1);
        // Exponential smoothing
        const exp = system.forecastResourceConsumption('r1', 'exp', { alpha: 0.5 });
        expect(exp).toBeGreaterThan(0);
    });

    it('should cache consumption stats and clear cache', () => {
        system.addResource(resource);
        system.logConsumption('agent1', 'r1', 10);
        const stats = system.getCachedConsumptionStats('r1');
        expect(stats).not.toBeUndefined();
        expect(stats?.total).toEqual(10);
        system.consumptionTracker.clearCache();
        expect(system.getCachedConsumptionStats('r1')).toBeUndefined();
    });

    it('should trigger scarcity response and substitution', () => {
        const system = new EconomicAgentResourceManagementSystem({}, { FOOD: ['GRAIN', 'FRUIT'] });
        system.setScarcityThreshold('FOOD', 20);
        system.setAgentPersonality('agent1', { riskTolerance: 0.5, cooperation: 0.5, hoarding: 0.5, competitiveness: 0.5 });
        const resp = system.handleScarcity('agent1', 'FOOD', 10);
        expect(resp.actions.some(a => a.type === 'substitute')).toEqual(true);
    });

    it('should trigger hoarding, competition, and cooperation based on personality', () => {
        const system = new EconomicAgentResourceManagementSystem({}, { WATER: ['JUICE'] });
        system.setScarcityThreshold('WATER', 50);
        system.setAgentPersonality('agent2', { riskTolerance: 0.5, cooperation: 0.8, hoarding: 0.8, competitiveness: 0.8 });
        const resp = system.handleScarcity('agent2', 'WATER', 10);
        expect(resp.actions.some(a => a.type === 'hoard')).toEqual(true);
        expect(resp.actions.some(a => a.type === 'compete')).toEqual(true);
        expect(resp.actions.some(a => a.type === 'cooperate')).toEqual(true);
        expect(system.getHoardingFactor('agent2')).toBeGreaterThan(1.0);
    });

    it('should allow alliance formation and resource sharing stubs', () => {
        const system = new EconomicAgentResourceManagementSystem();
        system.formAlliance(['agent1', 'agent2']);
        system.shareResource('agent1', 'FOOD', 5);
        // No assertion, just ensure no error
    });
}); 