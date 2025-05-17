import { ProjectileBuildingIntegration, BuildingSystem, QuestSystem, CrimeSystem, MissedShotEvent } from './ProjectileBuildingIntegration';
import { BuildingCollider } from './BuildingImpactDetector';
import { BuildingIntegrity, BuildingMaterial } from './BuildingDamageCalculator';

describe('ProjectileBuildingIntegration', () => {
    let buildingSystem: BuildingSystem;
    let questSystem: QuestSystem;
    let crimeSystem: CrimeSystem;
    let integration: ProjectileBuildingIntegration;
    let questEvents: any[];
    let crimeEvents: any[];

    beforeEach(() => {
        const colliders: BuildingCollider[] = [
            { id: 'b1', bounds: { x: 5, y: 0, width: 2, height: 4 } },
            { id: 'b2', bounds: { x: 10, y: 0, width: 2, height: 4 } },
        ];
        const integrities: Record<string, BuildingIntegrity> = {
            b1: { id: 'b1', health: 100, maxHealth: 100, material: 'wood' },
            b2: { id: 'b2', health: 100, maxHealth: 100, material: 'stone' },
        };
        buildingSystem = {
            getColliders: () => colliders,
            getIntegrity: (id) => integrities[id],
            updateIntegrity: (id, newHealth) => { if (integrities[id]) integrities[id].health = newHealth; },
            getMaterial: (id) => integrities[id]?.material ?? 'wood',
        };
        questEvents = [];
        questSystem = {
            triggerQuestEvent: (event, data) => { questEvents.push({ event, data }); },
        };
        crimeEvents = [];
        crimeSystem = {
            registerPropertyDamage: (buildingId, amount, actorId) => { crimeEvents.push({ buildingId, amount, actorId }); },
        };
        integration = new ProjectileBuildingIntegration(buildingSystem, questSystem, crimeSystem);
    });

    it('processes a missed shot and applies damage, triggers effects and hooks', () => {
        const event: MissedShotEvent = {
            projectileType: 'fireball',
            origin: { x: 0, y: 2 },
            velocity: { dx: 12, dy: 0 },
            shooterId: 'player1',
            timeStep: 0.1,
            maxTime: 2.0,
        };
        const result = integration.processMissedShot(event);
        expect(result.impacts.length).toBeGreaterThan(0);
        expect(result.damageResults.length).toBe(result.impacts.length);
        expect(result.visualEffects.length).toBe(result.impacts.length);
        expect(questEvents.length).toBe(result.impacts.length);
        expect(crimeEvents.length).toBe(result.impacts.length);
        // Check that building health was updated
        for (const dr of result.damageResults) {
            expect(dr.newHealth).toBeLessThan(100);
        }
    });

    it('handles no buildings hit (no impacts)', () => {
        const event: MissedShotEvent = {
            projectileType: 'arrow',
            origin: { x: 0, y: 10 },
            velocity: { dx: 1, dy: 0 },
            shooterId: 'player2',
            timeStep: 0.1,
            maxTime: 1.0,
        };
        const result = integration.processMissedShot(event);
        expect(result.impacts.length).toBe(0);
        expect(result.damageResults.length).toBe(0);
        expect(result.visualEffects.length).toBe(0);
        expect(questEvents.length).toBe(0);
        expect(crimeEvents.length).toBe(0);
    });

    it('handles destroyed building (health reaches zero)', () => {
        // Set up a building with low health
        buildingSystem.getIntegrity('b1')!.health = 10;
        const event: MissedShotEvent = {
            projectileType: 'fireball',
            origin: { x: 0, y: 2 },
            velocity: { dx: 12, dy: 0 },
            shooterId: 'player3',
            timeStep: 0.1,
            maxTime: 2.0,
        };
        const result = integration.processMissedShot(event);
        const destroyed = result.damageResults.find(dr => dr.buildingId === 'b1');
        expect(destroyed?.newHealth).toBe(0);
        expect(destroyed?.destroyed).toBe(true);
    });
}); 