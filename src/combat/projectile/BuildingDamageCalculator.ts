import { ImpactLog } from './BuildingImpactDetector';

export type BuildingMaterial = 'wood' | 'stone' | 'metal' | 'reinforced';

export interface BuildingIntegrity {
    id: string;
    health: number;
    maxHealth: number;
    material: BuildingMaterial;
}

export interface DamageResult {
    buildingId: string;
    damage: number;
    newHealth: number;
    destroyed: boolean;
}

const BASE_DAMAGE: Record<string, number> = {
    arrow: 10,
    fireball: 30,
    boulder: 20,
    ice: 15,
};

const MATERIAL_MULTIPLIER: Record<BuildingMaterial, number> = {
    wood: 1.0,
    stone: 0.5,
    metal: 0.3,
    reinforced: 0.2,
};

const PROJECTILE_MATERIAL_BONUS: Record<string, Partial<Record<BuildingMaterial, number>>> = {
    fireball: { wood: 2.0, stone: 1.0, metal: 0.8, reinforced: 0.7 },
    arrow: { wood: 1.0, stone: 0.3, metal: 0.2, reinforced: 0.1 },
    boulder: { wood: 1.2, stone: 1.5, metal: 1.0, reinforced: 0.8 },
    ice: { wood: 0.8, stone: 1.0, metal: 1.2, reinforced: 1.0 },
};

export class BuildingDamageCalculator {
    /**
     * Calculates and applies damage to a building integrity object based on impact log and projectile properties.
     * Returns a DamageResult with new health and destruction status.
     */
    static applyDamage(
        impact: ImpactLog,
        integrity: BuildingIntegrity,
        velocity: number // velocity at impact (m/s)
    ): DamageResult {
        const base = BASE_DAMAGE[impact.projectileType] ?? 10;
        const matMult = MATERIAL_MULTIPLIER[integrity.material] ?? 1.0;
        const projBonus = PROJECTILE_MATERIAL_BONUS[impact.projectileType]?.[integrity.material] ?? 1.0;
        // Angle effect: direct hit (0 deg) = 1.0, glancing (90 deg) = 0.5
        const angleEffect = 1.0 - Math.min(Math.abs(impact.angle), 90) / 180;
        // Velocity effect: scale linearly, cap at 2x base for very high speed
        const velocityEffect = Math.min(1 + velocity / 30, 2.0);
        let damage = base * matMult * projBonus * angleEffect * velocityEffect;
        damage = Math.max(0, Math.round(damage));
        const newHealth = Math.max(0, integrity.health - damage);
        const destroyed = newHealth === 0;
        // Mutate integrity for persistence
        integrity.health = newHealth;
        return {
            buildingId: integrity.id,
            damage,
            newHealth,
            destroyed,
        };
    }

    /**
     * Simulates persistence by serializing and deserializing the integrity object.
     */
    static persistIntegrity(integrity: BuildingIntegrity): BuildingIntegrity {
        return JSON.parse(JSON.stringify(integrity));
    }
} 