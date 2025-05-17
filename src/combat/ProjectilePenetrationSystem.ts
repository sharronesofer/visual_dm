import { BuildingStructure, BuildingElement, MaterialType } from '../core/interfaces/types/building';

/**
 * ProjectilePenetrationSystem
 * Handles projectile penetration through damaged building elements, calculating damage reduction and effects.
 */
export class ProjectilePenetrationSystem {
    // Penetration resistance by material type (configurable)
    private static penetrationResistance: Record<MaterialType, number> = {
        wood: 0.3,
        stone: 0.7,
        metal: 0.8,
        reinforced: 0.9,
    };

    /**
     * Process a projectile's path through a building structure, returning final damage and penetration status.
     * @param from Start point of the projectile.
     * @param to End point of the projectile.
     * @param structure The building structure.
     * @param baseDamage The initial damage of the projectile.
     * @returns { damage: number, penetrated: boolean, effects: string[] }
     */
    public static processProjectile(
        from: { x: number; y: number },
        to: { x: number; y: number },
        structure: BuildingStructure,
        baseDamage: number
    ): { damage: number; penetrated: boolean; effects: string[] } {
        // Raycast through the structure
        let x0 = Math.floor(from.x);
        let y0 = Math.floor(from.y);
        const x1 = Math.floor(to.x);
        const y1 = Math.floor(to.y);
        const dx = Math.abs(x1 - x0);
        const dy = Math.abs(y1 - y0);
        const sx = x0 < x1 ? 1 : -1;
        const sy = y0 < y1 ? 1 : -1;
        let err = dx - dy;

        let damage = baseDamage;
        let penetrated = true;
        const effects: string[] = [];

        while (true) {
            const element = this.getElementAtPosition(structure, x0, y0);
            if (element) {
                const resistance = this.penetrationResistance[element.material] ?? 0.5;
                const damageRatio = element.health / element.maxHealth;
                // Penetration chance decreases as resistance increases and damageRatio increases
                const effectiveResistance = resistance * (0.5 + 0.5 * damageRatio);
                if (Math.random() < effectiveResistance) {
                    penetrated = false;
                    effects.push('ricochet');
                    break;
                }
                // Reduce damage based on resistance and damage state
                damage *= 1 - (effectiveResistance * 0.7);
                effects.push('penetrate');
            }
            if (x0 === x1 && y0 === y1) {
                break;
            }
            const e2 = 2 * err;
            if (e2 > -dy) {
                err -= dy;
                x0 += sx;
            }
            if (e2 < dx) {
                err += dx;
                y0 += sy;
            }
        }
        return { damage: Math.max(0, damage), penetrated, effects };
    }

    /**
     * Find a building element at a given grid position (x, y)
     */
    private static getElementAtPosition(structure: BuildingStructure, x: number, y: number): BuildingElement | undefined {
        for (const element of structure.elements.values()) {
            if (Math.floor(element.position.x) === x && Math.floor(element.position.y) === y) {
                return element;
            }
        }
        return undefined;
    }
} 