import { TrajectoryCalculator, ProjectileParams } from './TrajectoryCalculator';
import { BuildingImpactDetector, BuildingCollider, ImpactLog } from './BuildingImpactDetector';
import { BuildingDamageCalculator, BuildingIntegrity, DamageResult, BuildingMaterial } from './BuildingDamageCalculator';
import { BuildingDamageVisualizer, VisualEffect } from './BuildingDamageVisualizer';

// Interfaces for external system hooks (to be implemented by the main game engine)
export interface BuildingSystem {
    getColliders(): BuildingCollider[];
    getIntegrity(id: string): BuildingIntegrity | undefined;
    updateIntegrity(id: string, newHealth: number): void;
    getMaterial(id: string): BuildingMaterial;
}
export interface QuestSystem {
    triggerQuestEvent(event: string, data: any): void;
}
export interface CrimeSystem {
    registerPropertyDamage(buildingId: string, amount: number, actorId: string): void;
}

export interface MissedShotEvent {
    projectileType: string;
    origin: { x: number; y: number };
    velocity: { dx: number; dy: number };
    shooterId: string;
    timeStep?: number;
    maxTime?: number;
}

export class ProjectileBuildingIntegration {
    constructor(
        private buildingSystem: BuildingSystem,
        private questSystem: QuestSystem,
        private crimeSystem: CrimeSystem
    ) { }

    /**
     * Processes a missed shot event: calculates trajectory, detects building impacts, applies damage, triggers effects and system hooks.
     */
    processMissedShot(event: MissedShotEvent): {
        impacts: ImpactLog[];
        damageResults: DamageResult[];
        visualEffects: VisualEffect[];
    } {
        // 1. Calculate trajectory
        const params: ProjectileParams = {
            initialPosition: event.origin,
            initialVelocity: event.velocity,
            timeStep: event.timeStep,
            maxTime: event.maxTime,
        };
        const trajectory = TrajectoryCalculator.calculateTrajectory(params);
        // 2. Detect building impacts
        const colliders = this.buildingSystem.getColliders();
        const impacts = BuildingImpactDetector.detectImpacts(trajectory.points, colliders, event.projectileType);
        const damageResults: DamageResult[] = [];
        const visualEffects: VisualEffect[] = [];
        for (const impact of impacts) {
            // 3. Get building integrity and material
            const integrity = this.buildingSystem.getIntegrity(impact.buildingId);
            if (!integrity) continue;
            const material = this.buildingSystem.getMaterial(impact.buildingId);
            // 4. Estimate velocity at impact (simple: use initial for now)
            const velocity = Math.sqrt(event.velocity.dx ** 2 + event.velocity.dy ** 2);
            // 5. Apply damage
            const result = BuildingDamageCalculator.applyDamage(impact, integrity, velocity);
            this.buildingSystem.updateIntegrity(impact.buildingId, result.newHealth);
            damageResults.push(result);
            // 6. Visual feedback
            visualEffects.push(...BuildingDamageVisualizer.determineVisualEffects(result, event.projectileType, material, impact.point));
            // 7. Quest system hook
            this.questSystem.triggerQuestEvent('buildingDamaged', { buildingId: impact.buildingId, damage: result.damage });
            // 8. Crime system hook
            this.crimeSystem.registerPropertyDamage(impact.buildingId, result.damage, event.shooterId);
        }
        return { impacts, damageResults, visualEffects };
    }
} 