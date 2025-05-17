import { DamageResult } from './BuildingDamageCalculator';
import { BuildingMaterial } from './BuildingDamageCalculator';

export type VisualState = 'undamaged' | 'damaged' | 'heavilyDamaged' | 'destroyed';
export type EffectSeverity = 'minor' | 'moderate' | 'severe';

export interface VisualEffect {
    type: string;
    position: { x: number; y: number };
    severity: EffectSeverity;
    sound?: string;
}

const DAMAGE_TYPE_EFFECTS: Record<string, { type: string; sound: string }> = {
    arrow: { type: 'splinter', sound: 'wood_hit' },
    fireball: { type: 'scorch', sound: 'fire_blast' },
    boulder: { type: 'crack', sound: 'stone_crack' },
    ice: { type: 'frost', sound: 'ice_shatter' },
};

const MATERIAL_EFFECT_MODIFIERS: Record<BuildingMaterial, string> = {
    wood: 'wood',
    stone: 'stone',
    metal: 'metal',
    reinforced: 'reinforced',
};

export class BuildingDamageVisualizer {
    /**
     * Determines which visual effects to spawn based on damage result, projectile type, and material.
     */
    static determineVisualEffects(
        damageResult: DamageResult,
        projectileType: string,
        buildingMaterial: BuildingMaterial,
        impactPosition: { x: number; y: number }
    ): VisualEffect[] {
        if (damageResult.damage <= 0) return [];
        let severity: EffectSeverity = 'minor';
        const percent = damageResult.damage / (damageResult.newHealth + damageResult.damage);
        if (percent > 0.5) severity = 'severe';
        else if (percent > 0.2) severity = 'moderate';
        const base = DAMAGE_TYPE_EFFECTS[projectileType] ?? { type: 'impact', sound: 'impact_generic' };
        const effectType = `${base.type}_${MATERIAL_EFFECT_MODIFIERS[buildingMaterial]}`;
        return [
            {
                type: effectType,
                position: impactPosition,
                severity,
                sound: base.sound,
            },
        ];
    }

    /**
     * Determines the visual state of a building based on current and max integrity.
     */
    static getBuildingVisualState(current: number, max: number): VisualState {
        const ratio = current / max;
        if (ratio === 0) return 'destroyed';
        if (ratio < 0.3) return 'heavilyDamaged';
        if (ratio < 0.8) return 'damaged';
        return 'undamaged';
    }
} 